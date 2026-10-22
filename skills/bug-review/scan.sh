#!/usr/bin/env bash
# shellcheck disable=SC2207  # IFS is newline and globbing is off, so array splits are safe
# Run installed static scanners on files changed since a base ref. Output is review input, so it always exits 0.
# Usage: [UNTRUSTED=1] scan.sh [base-ref]   (default: origin/HEAD, then main, then master)
# UNTRUSTED=1 skips tools that execute repo code (clippy build scripts, eslint/biome configs and plugins)
# and ignores the repo's golangci-lint config.
set -uo pipefail
IFS=$'\n'; set -f
cd "$(git rev-parse --show-toplevel)" || exit 0

base="${1:-}"
if [ -z "$base" ]; then
  for b in origin/HEAD main master; do git rev-parse -q --verify "$b" >/dev/null && { base=$b; break; }; done
fi
# Shallow clones (CI default) have no merge-base, so fall back to the base commit itself.
mb=$(git merge-base "$base" HEAD 2>/dev/null || git rev-parse -q --verify "$base^{commit}") || { echo "scan: cannot resolve base '$base'"; exit 0; }

# Committed + uncommitted changes since the merge-base, plus untracked files.
files=()
while IFS= read -r f; do [ -f "$f" ] && files+=("$f"); done < <(
  { git diff --name-only --diff-filter=ACMR "$mb"; git ls-files --others --exclude-standard; } | sort -u)
[ ${#files[@]} -eq 0 ] && { echo "scan: no changed files since $base"; exit 0; }

pick() { local re=$1 f; for f in "${files[@]}"; do [[ $f =~ $re ]] && printf '%s\n' "$f"; done; }
has() { command -v "$1" >/dev/null 2>&1; }
section() { printf '\n## %s\n' "$1"; }

echo "# Scanner report: ${#files[@]} changed files since $base ($mb)"

section gitleaks
if has gitleaks; then
  for f in "${files[@]}"; do gitleaks detect --no-git --no-banner --no-color --redact -v -s "$f" 2>/dev/null | grep -v '^$'; done
else echo "skipped: not installed"; fi

section semgrep
if semgrep --version >/dev/null 2>&1; then
  semgrep scan --config p/default --metrics off --quiet "${files[@]}" 2>&1
else echo "skipped: not installed or broken (semgrep --version fails)"; fi

py=($(pick '\.py$'))
section ruff
if [ ${#py[@]} -eq 0 ]; then echo "skipped: no Python changes"
elif has ruff; then
  # A pyenv shim fails inside repos pinning an uninstalled Python, so fall back to the global install.
  ruff=ruff
  ruff --version >/dev/null 2>&1 || ruff=$(cd "$HOME" && pyenv which ruff 2>/dev/null) || ruff=
  if [ -n "$ruff" ]; then "$ruff" check --no-fix --extend-select B,S,ASYNC,BLE --output-format concise "${py[@]}" 2>&1
  else echo "skipped: ruff not runnable here"; fi
else echo "skipped: not installed"; fi

sh=($(pick '\.(sh|bash)$'))
section shellcheck
if [ ${#sh[@]} -eq 0 ]; then echo "skipped: no shell changes"
elif has shellcheck; then shellcheck -f gcc "${sh[@]}" 2>&1
else echo "skipped: not installed"; fi

wf=($(pick '^\.github/workflows/.*\.ya?ml$'))
section actionlint
if [ ${#wf[@]} -eq 0 ]; then echo "skipped: no workflow changes"
elif has actionlint; then actionlint "${wf[@]}" 2>&1
else echo "skipped: not installed"; fi

js=($(pick '\.(js|jsx|ts|tsx|mjs|cjs)$'))
section eslint/biome
if [ ${#js[@]} -eq 0 ]; then echo "skipped: no JS/TS changes"
elif [ -n "${UNTRUSTED:-}" ]; then echo "skipped: UNTRUSTED set (runs repo JS)"
elif [ -x node_modules/.bin/biome ]; then node_modules/.bin/biome lint "${js[@]}" 2>&1
elif [ -x node_modules/.bin/eslint ]; then node_modules/.bin/eslint --format unix "${js[@]}" 2>&1
else echo "skipped: no local biome or eslint in node_modules"; fi

go=($(pick '\.go$'))
section golangci-lint
if [ ${#go[@]} -eq 0 ]; then echo "skipped: no Go changes"
elif has golangci-lint; then
  for d in $(for f in "${go[@]}"; do (cd "$(dirname "$f")" && dirname "$(go env GOMOD)"); done | sort -u); do
    [ "$d" = . ] || [ "$d" = /dev ] && continue
    # A repo .golangci.yml can load plugin code, so UNTRUSTED ignores it.
    (cd "$d" && golangci-lint run --allow-parallel-runners ${UNTRUSTED:+--no-config} --new-from-rev="$mb" ./... 2>&1)
  done
else echo "skipped: not installed"; fi

rs=($(pick '\.rs$'))
section clippy
if [ ${#rs[@]} -eq 0 ]; then echo "skipped: no Rust changes"
elif [ -n "${UNTRUSTED:-}" ]; then echo "skipped: UNTRUSTED set (runs build.rs and proc macros)"
elif has cargo && [ -f Cargo.toml ]; then
  # Clippy reports the whole crate, keep only lines that name a changed file.
  cargo clippy --quiet --message-format short 2>&1 | grep -F -f <(printf '%s\n' "${rs[@]}")
else echo "skipped: no cargo or no root Cargo.toml"; fi
exit 0

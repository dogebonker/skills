"""Resolve the ast-grep command once and run inline rules over files with JSON output."""
import functools
import json
import shutil
import subprocess
import tempfile

CANDIDATES = (
    ["uvx", "--from", "ast-grep-cli", "ast-grep"],
    ["npx", "-y", "@ast-grep/cli"],
    ["ast-grep"],
    ["sg"],
)
BATCH = 400  # files per ast-grep call, keeps argv well under ARG_MAX


@functools.lru_cache(maxsize=None)
def command():
    for cmd in CANDIDATES:
        if not shutil.which(cmd[0]):
            continue
        try:
            r = subprocess.run(cmd + ["--version"], capture_output=True, text=True, timeout=600)
        except (OSError, subprocess.TimeoutExpired):
            continue
        # `sg` on Linux can be the shadow-utils setgroups tool, so check the banner.
        if r.returncode == 0 and "ast-grep" in r.stdout:
            return cmd
    raise SystemExit("ast-grep not found: install uv (uvx) or node (npx), or put ast-grep on PATH")


def scan(rules, files):
    """Yield ast-grep JSON matches of the inline `rules` YAML over `files` (absolute paths)."""
    files = list(files)
    for i in range(0, len(files), BATCH):
        r = subprocess.run(
            command() + ["scan", "--inline-rules", rules, "--json=stream", *files[i:i + BATCH]],
            capture_output=True, text=True, cwd=tempfile.gettempdir(),  # no repo sgconfig.yml
        )
        if r.returncode != 0:
            raise RuntimeError(f"ast-grep scan failed: {r.stderr.strip()[:2000]}")
        for line in r.stdout.splitlines():
            if line.strip():
                yield json.loads(line)

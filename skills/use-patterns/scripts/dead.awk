# Signal 24 helper, run after ranges.awk. The stream continues with:
#   <path>:<line>:W<word>    scope words outside comment lines
#   ROOT:<absolute REPO_ROOT>
#   <path>:<line>:X <name>   definitions anywhere under REPO_ROOT
#   <count> <path>:R<word>   words outside comment lines anywhere under REPO_ROOT (sort | uniq -c)
# With -v here="$PWD", paths print as ./<path> under the scope and <path> under the root.
# A use is a word outside the name's own definition lines and outside code already found dead.
# Prints each dead definition with the first pass that found it:
#   pass 1 (no tag): no use anywhere;
#   pass N: every use sits inside the dead definitions it names;
#   copy: a top-level definition its own file never uses while other files define the name too,
#         and no file that uses the name without defining it sits beside it or names its file
#         or directory.
function norm(p) { return index(p, here "/") == 1 ? "." substr(p, length(here) + 1) : index(p, root "/") == 1 ? substr(p, length(root) + 2) : p }
function dir(p) { sub(/\/[^\/]*$/, "", p); return p }
function last1(p) { sub(/^.*\//, "", p); return p }
function base(p) { p = last1(p); sub(/\.[^.]*$/, "", p); return p }
function pkg(p) { p = dir(p); return last1(p == "." ? here : p) }
function mark(n, p) { if (!((n, p) in has)) { has[n, p] = 1; hf[n] = hf[n] " " p } }
function setup(   i) {
    for (i = 1; i <= nd; i++) { want[dn[i]]; want[base(df[i])]; want[pkg(df[i])]; mark(dn[i], df[i]) }
    ready = 1
}
!ready { setup() }
/^ROOT:/ { root = substr($0, 6); next }
match($0, /:[0-9]+:W/) {
    w = substr($0, RSTART + RLENGTH)
    if (!(w in want)) next
    f = substr($0, 1, RSTART - 1); k = ++no[w]
    of[w, k] = f; ol[w, k] = substr($0, RSTART + 1, RLENGTH - 3) + 0; seen[w, f] = 1
    next
}
match($0, /:[0-9]+:X /) {
    n = substr($0, RSTART + RLENGTH)
    if (!(n in want)) next
    p = norm(substr($0, 1, RSTART - 1)); mark(n, p)
    if (!(p in scope)) xd[n, p]++
    next
}
match($0, /^ *[0-9]+ /) {
    c = substr($0, 1, RLENGTH) + 0; s = substr($0, RLENGTH + 1)
    if (!match(s, /:R[A-Za-z0-9_]+$/)) next
    w = substr(s, RSTART + 2)
    if (!(w in want)) next
    p = norm(substr(s, 1, RSTART - 1))
    if (p in scope) next
    if (!((w, p) in rc)) rf[w] = rf[w] SUBSEP p
    rc[w, p] += c
    next
}
function used(w, g) { return (w, g) in seen || (w, g) in rc }
# 0: live, 1: no use outside dead code (users: the dead names holding the uses), 2: copy
function check(i,   n, f, k, g, l, t, m, p, use, other, by) {
    n = dn[i]; f = df[i]; users = ""
    for (k = 1; k <= no[n]; k++) {
        g = of[n, k]; l = ol[n, k]
        if ((g, l) in gone) { if (!(dn[gone[g, l]] in by)) { by[dn[gone[g, l]]]; users = users ", " dn[gone[g, l]] } continue }
        if (((g, l) in at && at[g, l] == n) || (g == f && l >= dl[i] && l <= de[i])) continue
        use[g]++; other[g]
    }
    m = split(rf[n], p, SUBSEP)
    for (k = 2; k <= m; k++) if (rc[n, p[k]] > xd[n, p[k]]) other[p[k]]
    if (!length(other)) return 1
    t = txt[f, dl[i]]
    if (ind[f, dl[i]] || substr(t, 1, index(t, n) - 1) ~ /\(/ || f in use || split(hf[n], p, " ") < 2) return 0
    for (g in other)
        if (!((n, g) in has) && g !~ /\.(md|rst|txt|adoc)$/ && (dir(g) == dir(f) || used(base(f), g) || used(pkg(f), g))) return 0
    return 2
}
END {
    if (!ready) setup()
    ends()
    for (pass = 1; pass <= 9; pass++) {
        m = 0
        for (i = 1; i <= nd; i++)
            if (!dead[i] && (r = check(i))) { found[++m] = i; why[i] = r; who[i] = substr(users, 3) }
        for (j = 1; j <= m; j++) {
            i = found[j]; dead[i] = pass
            for (k = dl[i]; k <= de[i]; k++) gone[df[i], k] = i
        }
        if (!m) break
    }
    for (i = 1; i <= nd; i++) {
        if (!dead[i]) continue
        t = ""
        if (why[i] == 2) { t = hf[dn[i]]; sub(" " df[i], "", t); t = " (copy: unused in its own file; also defined in" t ")" }
        else if (dead[i] > 1) t = " (pass " dead[i] ": used only by " who[i] ")"
        print df[i] ":" dl[i] ": " dn[i] t
    }
}

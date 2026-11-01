# Shared by dead.awk (signal 24) and long.awk (signal 25); run as `awk -f ranges.awk -f <helper>`.
# Reads, first on one stream:
#   <path>:<line>:D <name>   definitions in scope   (rg -n -H -o -P <definition regex> -r 'D $1')
#   L <path>:<line>:<text>   every scope source line (rg -n -H '' . | sed 's/^/L /')
# ends() gives definition i the lines dl[i]..de[i]: up to the next non-blank line indented no
# deeper than the definition line, where a line opening with ) ] or } still belongs to it.
/^L / {
    s = substr($0, 3); match(s, /:[0-9]+:/)
    f = substr(s, 1, RSTART - 1); l = substr(s, RSTART + 1, RLENGTH - 2) + 0
    t = substr(s, RSTART + RLENGTH)
    match(t, /^[ \t]*/)
    ind[f, l] = RLENGTH == length(t) ? -1 : RLENGTH
    cl[f, l] = substr(t, RLENGTH + 1, 1) ~ /[]})]/
    if ((f, l) in at) txt[f, l] = t
    last[f] = l; scope[f] = 1
    next
}
match($0, /:[0-9]+:D /) {
    n = substr($0, RSTART + RLENGTH)
    if (skip != "" && n ~ skip) next
    f = substr($0, 1, RSTART - 1); l = substr($0, RSTART + 1, RLENGTH - 4) + 0
    ++nd; df[nd] = f; dl[nd] = l; dn[nd] = n; at[f, l] = n
    next
}
function ends(   i, k, f) {
    for (i = 1; i <= nd; i++) {
        f = df[i]
        for (k = dl[i] + 1; k <= last[f]; k++)
            if (ind[f, k] >= 0 && ind[f, k] <= ind[f, dl[i]] && !cl[f, k]) break
        de[i] = k - 1
    }
}

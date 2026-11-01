# Step 2 triage. Input, in this order on one stream:
#   D:<path>:<line>:<text>   every definition (rg -n -H "$DEF")
#   N:<path>:<count>         line count per file (rg -c -H '^')
#   the saved scan output    (# ID lines, then path:line: hits, then aggregated lists)
# Prints the hits clustered by enclosing definition, ranked by hit count then length,
# with a running total, followed by the aggregated lists grouped by signal id.
# Type checks (signals 2 and 11) inside a definition whose line or file says parse, normalize,
# extract, from_json or payload form their own [boundary] clusters, ranked after all others.
/^D:/ {
    s = substr($0, 3); match(s, /:[0-9]+:/)
    f = substr(s, 1, RSTART - 1); k = ++nd[f]
    dl[f, k] = substr(s, RSTART + 1, RLENGTH - 2) + 0
    dt[f, k] = substr(s, RSTART + RLENGTH)
    next
}
/^N:/ { s = substr($0, 3); match(s, /:[0-9]+$/); len[substr(s, 1, RSTART - 1)] = substr(s, RSTART + 1) + 0; next }
/^# [A-Z]+[0-9]+$/ { id = $2; next }
/^(rg|for|command) |^\{ |^rg\(\)|^--$|^[^ :]+-[0-9]+-/ { next }
match($0, /^[^ :]+:[0-9]+:/) {
    f = substr($0, 1, RLENGTH); sub(/:[0-9]+:$/, "", f)
    l = substr($0, length(f) + 2) + 0
    k = 0
    for (i = 1; i <= nd[f]; i++) if (dl[f, i] <= l) k = i
    key = f SUBSEP k
    if (id ~ /^[A-Z]+(2|11)$/ && tolower(f " " (k ? dt[f, k] : "")) ~ /parse|normali[sz]e|extract|from_?json|payload/) key = key SUBSEP "b"
    if (!(key in hits)) order[++nk] = key
    hits[key]++; total++
    if (index(" " ids[key] " ", " " id " ") == 0) ids[key] = ids[key] (ids[key] == "" ? "" : " ") id
    next
}
NF { list[++nl] = id SUBSEP $0 }
END {
    for (j = 1; j <= nk; j++) {
        split(order[j], p, SUBSEP); f = p[1]; k = p[2] + 0; b[j] = p[3] == "b"
        start = k ? dl[f, k] : 1
        stop = (k < nd[f]) ? dl[f, k + 1] - 1 : (f in len ? len[f] : start)
        h[j] = hits[order[j]]; n[j] = stop - start + 1
        row[j] = f ":" start "\t" ids[order[j]] (b[j] ? " [boundary]" : "") "\t" (k ? dt[f, k] : "<module>")
    }
    for (j = 2; j <= nk; j++)
        for (i = j; i > 1 && (b[i] < b[i - 1] || (b[i] == b[i - 1] && (h[i] > h[i - 1] || (h[i] == h[i - 1] && n[i] > n[i - 1])))); i--) {
            t = b[i]; b[i] = b[i - 1]; b[i - 1] = t
            t = h[i]; h[i] = h[i - 1]; h[i - 1] = t
            t = n[i]; n[i] = n[i - 1]; n[i - 1] = t
            t = row[i]; row[i] = row[i - 1]; row[i - 1] = t
        }
    for (j = 1; j <= nk; j++) if (b[j]) { bh += h[j]; bc++ }
    print "# triage: " total " hits in " nk " clusters, " bh + 0 " hits in " bc + 0 " [boundary] clusters. Columns: rank, hits, cumulative hits, lines, where, signals, definition"
    for (j = 1; j <= nk; j++) { cum += h[j]; print j "\t" h[j] "\t" cum "\t" n[j] "\t" row[j] }
    print "# lists"
    for (j = 1; j <= nl; j++) { split(list[j], p, SUBSEP); if (p[1] != last) print "# " (last = p[1]); print p[2] }
}

# Signal 5 helper. Reads `rg -U -o -n -H ... -r '@@<name>@@<params>'` output, where a
# multi-line signature arrives as several numbered lines. Prints one line per signature
# with at least `min` parameters (default 4), not counting self, cls or bare `*` and `/`:
#   path:line: name (N params[, keyword-only])
function flush(   s, n, i, a, c, kw) {
    if (loc == "") return
    s = rec
    gsub(/[-=]>/, " ", s)
    while (gsub(/\([^()]*\)|\[[^][]*\]|\{[^{}]*\}|<[^<>]*>/, "", s)) {}
    n = split(s, a, ",")
    for (i = 1; i <= n; i++) {
        if (a[i] ~ /^[[:space:]]*\*[[:space:]]*$/) kw = ", keyword-only"
        if (a[i] ~ /[[:alnum:]_]/ && a[i] !~ /^[[:space:]]*&?(mut[[:space:]]+)?(self|cls)[[:space:]]*$/) c++
    }
    if (c >= (min ? min : 4)) print loc ": " name " (" c " params" kw ")"
    loc = ""
}
{
    match($0, /^[^:]*:[0-9]+:/)
    pre = substr($0, 1, RLENGTH - 1)
    body = substr($0, RLENGTH + 1)
}
body ~ /^@@/ {
    flush()
    loc = pre
    name = substr(body, 3)
    sub(/@@.*/, "", name)
    rec = body
    sub(/^@@[^@]*@@/, "", rec)
    next
}
{ rec = rec " " body }
END { flush() }

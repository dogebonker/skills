# Signal 25 helper, run after ranges.awk. Prints each definition longer than min lines (default 80):
#   path:line: name (N lines)
END {
    ends()
    for (i = 1; i <= nd; i++)
        if ((n = de[i] - dl[i] + 1) > (min ? min : 80)) print df[i] ":" dl[i] ": " dn[i] " (" n " lines)"
}

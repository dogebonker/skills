//! Tiny parser used by the fixtures. Ünïcödé in docs.

/// Parses a duration like "10s".
pub fn parse_secs(s: &str) -> Option<u64> {
    s.strip_suffix('s')?.parse().ok()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_seconds() {
        assert_eq!(parse_secs("10s"), Some(10));
    }

    /// Rejects input without the unit — non-ASCII doc: ✓
    #[test]
    #[should_panic(expected = "none")]
    fn rejects_missing_unit() {
        parse_secs("10").expect("none");
    }

    #[tokio::test(flavor = "multi_thread")]
    async fn parses_async() {
        assert_eq!(parse_secs("1s"), Some(1));
    }

    #[rstest]
    #[case("1s", 1)]
    #[case("2s", 2)]
    fn parses_cases(#[case] input: &str, #[case] want: u64) {
        assert_eq!(parse_secs(input), Some(want));
    }

    fn helper() -> u64 {
        1
    }

    mod nested {
        #[test]
        fn inner() {
            assert_eq!(super::helper(), 1);
        }
    }
}

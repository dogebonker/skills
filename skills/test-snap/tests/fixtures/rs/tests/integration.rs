use fixture::parse_secs;

fn setup() -> &'static str {
    "5s"
}

#[test]
fn parses_from_setup() {
    assert_eq!(parse_secs(setup()), Some(5));
}

#[test]
fn parses_zero() {
    assert_eq!(parse_secs("0s"), Some(0));
}

/// Not a test, though this doc mentions #[test].
fn helper_with_doc() {}

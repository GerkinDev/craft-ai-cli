import pytest

from utils.parse_payload import ReaderWrapper, parse_payload, tokenize_json_arr, tokenize_chars

def idfnval(val):
    return f'{val!r}'


@pytest.mark.parametrize('input,expected', [
    ('foo', 'foo'),
    ('"foo"', 'foo'),
    ("'foo'", 'foo'),
    ("`foo`", 'foo'),
    ("`foo'`", "foo'"),
    ('foo\\ ', 'foo '),
    ('"foo\\""', 'foo\"'),
    ("'foo\\''", 'foo\''),
    ("`foo\\``", 'foo`'),
    ('\\ foo', ' foo'),
    ('\\""foo"', '""foo"'),
    ("\\''foo'", '\'\'foo\''),
    ("\\``foo`", '``foo`'),
    ('"foo\\\\"', 'foo\\'),
    ('foo\\\\', 'foo\\'),
], ids=idfnval)
def test_tokenize_chars(input: str, expected: str):
    assert tokenize_chars(ReaderWrapper(input))[0] == expected

@pytest.mark.parametrize('input', [
    '"foo',
    '"foo\\',
    'foo\\',
], ids=idfnval)
def test_tokenize_chars_fail(input: str):
    with pytest.raises(SyntaxError):
        print(tokenize_chars(ReaderWrapper(input)))

@pytest.mark.parametrize('input,expected', [
    ('[]', []),
    ('[asd]', ['asd']),
], ids=idfnval)
def test_tokenize_json_arr(input: str, expected: list):
    assert tokenize_json_arr(ReaderWrapper(input[1:])) == expected

@pytest.mark.parametrize('input,expected', [
    ('foo="double quote"', {"foo": "double quote"}),
    ('foo=\'single quote\'', {"foo": "single quote"}),
    ('foo=`backtick`', {"foo": "backtick"}),
    ('foo="1"', {"foo": "1"}),
    ('foo="True"', {"foo": "True"}),
    ('foo={"bar": 1}', {"foo": {"bar": 1}}),
    ('foo={"bar": true, baz:[   qux,{}   ]}', {"foo": {"bar": True, "baz": ['qux', {}]}}),
    ('foo=[1]', {"foo": [1]}),
    ('foo=1', {"foo": 1}),
    ('foo=.1', {"foo": .1}),
    ('foo=-.1', {"foo": -.1}),
], ids=idfnval)
def test_parse_payload(input: str, expected: dict):
    assert parse_payload(input) == expected


def test_parse_payload_complex():
    parsed = parse_payload(f"key1='value with, commas', key2={{\"json\": {{\"nested\": \"value\"}}}}, key3=@{__file__}, key4=true, key5=42, key6=unquoted")
    assert parsed["key1"] == 'value with, commas'
    assert parsed["key2"] == {"json": {"nested": "value"}}
    assert parsed["key3"] == open(__file__, 'rb').read()
    assert parsed["key4"] is True
    assert parsed["key5"] == 42
    assert parsed["key6"] == "unquoted"

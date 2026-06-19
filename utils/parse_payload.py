from io import StringIO
import re
from typing import Any

def parse_payload(payload_str: str) -> dict[str, Any]:
    """Parse the payload string with quoted strings, JSON, and file references.

    Supports:
    - Quoted strings with `'`, `"`, or `` ` ``.
    - Nested JSON values (e.g., `{"key": {"nested": "value"}}`).
    - File references with `@path`.
    - Boolean, numeric, and unquoted string values.

    Example:
    `--payload "key1='value with, commas', key2={\"json\": {\"nested\": \"value\"}}, key3=@file.txt, key4=true, key5=42, key6=unquoted"`
    """
    payload = {}
    for kvp in tokenize_payload(payload_str):
        payload[kvp[0]] = kvp[1]

    return payload

class ReaderWrapper(StringIO):
    def __init__(self, payload_str: str):
        super().__init__(payload_str)
        self.is_end = False

    def next(self, allow_finished = False):
        char = self.read(1)
        if char == '':
            if allow_finished:
                self.is_end = True
                return None
            else:
                raise SyntaxError('Unexpected end of string')
        return char
    
    def current(self, allow_finished = False):
        char = self.next(allow_finished)
        self.rewind()
        return char
    
    def rewind(self):
        self.seek(self.tell() - 1)
    
    def skip_white(self):
        char = None
        while char is None or char.isspace():
            char = self.next(True)
            if char is None:
                return True
        self.rewind()
        return False
    
    def get_leftovers(self):
        return self.getvalue()[self.tell():]
    
def tokenize_payload(payload_str: str):
    try:
        reader = ReaderWrapper(payload_str)
        while True:
            key = tokenize_payload_key(reader)
            if key is None:
                return

            # Iterate until key/value separator
            reader.skip_white()
            if reader.next() != '=':
                raise SyntaxError('missing `=` delimiter between key and value')

            value = tokenize_payload_value(reader)
            yield key, value

            # Iterate until comma separator or end of string
            reader.skip_white()
            if reader.is_end:
                return
            if reader.next() != ',':
                raise SyntaxError('expected comma')
    except SyntaxError as e:
        next_chars = payload_str[reader.tell()-2:reader.tell() + 10]
        raise SyntaxError(f"Invalid input string near {next_chars!r}: {e}") from e

def tokenize_payload_key(reader: ReaderWrapper):
    is_end = reader.skip_white()
    if is_end:
        return None
    key, quoted = tokenize_chars(reader, {"="})
    return key

def tokenize_payload_value(reader: ReaderWrapper):
    reader.skip_white()
    first_char = reader.next()
    if first_char == '@': # File mode
        path, quoted = tokenize_chars(reader, {','})
        with open(path, 'rb') as f:
            return f.read()
    if first_char == '{': # JSON object mode
        return tokenize_json_obj(reader)
    if first_char == '[': # JSON array mode
        return tokenize_json_arr(reader)
    reader.rewind()
    value = coerce_string(tokenize_chars(reader, {','}))
    return value

def coerce_string(parsed_string: tuple[str, bool]):
    if not parsed_string[1]:
        if parsed_string[0] in {'True', 'true'}:
            return True
        elif parsed_string[0] in {'False', 'false'}:
            return False
        elif re.match(r'-?(\d*\.)?\d+', parsed_string[0]):
            return float(parsed_string[0])
        elif parsed_string[0] in {'null', 'None'}:
            return None
    return parsed_string[0]

def tokenize_json_value(reader: ReaderWrapper, extra_delimiter: set[str] | None = None):
    reader.skip_white()
    first_char = reader.next()
    if first_char == '{': # JSON object mode
        return tokenize_json_obj(reader)
    if first_char == '[': # JSON array mode
        return tokenize_json_arr(reader)
    reader.rewind()
    value = coerce_string(tokenize_chars(reader, extra_delimiter))
    return value

def tokenize_json_obj(reader: ReaderWrapper):
    reader.skip_white()
    acc = {}
    while True:
        if reader.next() == '}':
            return acc
        reader.rewind()
        obj_key = tokenize_chars(reader, {':'})[0]

        if reader.next() != ':':
            raise SyntaxError('Missing json : delimiter')
        reader.skip_white()
        
        obj_value = tokenize_json_value(reader, {',', '}'})
        acc[obj_key] = obj_value
        reader.skip_white()

        next = reader.next()
        if next == ',':
            pass
        elif next == '}':
            return acc
        else:
            raise SyntaxError('Missing json comma or object end delimiter')


def tokenize_json_arr(reader: ReaderWrapper):
    reader.skip_white()
    acc = []
    while True:
        if reader.next() == ']':
            return acc
        reader.rewind()
        arr_item = tokenize_json_value(reader, {',', ']'})
        acc.append(arr_item)
        reader.skip_white()

        next = reader.next()
        if next == ',':
            pass
        elif next == ']':
            return acc
        else:
            raise SyntaxError('Missing json comma or object end delimiter')

def tokenize_chars(reader: ReaderWrapper, extra_delimiter: set[str] | None = None):
    started = False
    delimiter = None
    escaping = False
    token = ''
    while True:
        char = reader.next(True)
        if char is None:
            if delimiter or escaping:
                raise SyntaxError('Unterminated string')
            return token, delimiter is not None
        # Skip whitespace padding
        if not started and char.isspace():
            continue
        if not started and char in ['"', "'", '`']:
            delimiter = char
            continue
        if char == '\\' and not escaping:
            escaping = True
            started = True
            continue
        if started and not escaping and (
            char.isspace()
            if delimiter is None else
            char == delimiter
        ):
            return token, delimiter is not None
        if started and not escaping and delimiter is None and extra_delimiter is not None and char in extra_delimiter:
            reader.rewind()
            return token, delimiter is not None
        started = True
        token += char
        escaping = False



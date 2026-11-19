"""Bounded ConfigFile subset for the owned fixtures, not a Godot parser."""
import json
import re


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate dictionary key')
        result[key] = value
    return result


def _strip_comments(text):
    output = []
    quoted = escaped = comment = False
    for character in text:
        if comment:
            if character == '\n':
                comment = False
                output.append(character)
            continue
        if quoted:
            output.append(character)
            if escaped:
                escaped = False
            elif character == '\\':
                escaped = True
            elif character == '"':
                quoted = False
        elif character == '"':
            quoted = True
            output.append(character)
        elif character == ';':
            comment = True
        else:
            output.append(character)
    if quoted:
        raise ValueError('unterminated descriptor string')
    return ''.join(output)


def _remove_trailing_commas(value):
    output = []
    quoted = escaped = False
    for index, character in enumerate(value):
        if quoted:
            output.append(character)
            if escaped:
                escaped = False
            elif character == '\\':
                escaped = True
            elif character == '"':
                quoted = False
        elif character == '"':
            quoted = True
            output.append(character)
        elif character == ',':
            following = index + 1
            while following < len(value) and value[following].isspace():
                following += 1
            if following >= len(value) or value[following] != '}':
                output.append(character)
        else:
            output.append(character)
    return ''.join(output)


def parse_sections(text):
    """Parse only fixture library and dictionary-valued dependency entries."""
    if len(text.encode('utf-8')) > 1024 * 1024:
        raise ValueError('fixture descriptor size limit exceeded')
    lines = _strip_comments(text).splitlines()
    sections = {'libraries': [], 'dependencies': []}
    seen_sections = set()
    section = None
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        index += 1
        if not line:
            continue
        if line.startswith('[') and line.endswith(']'):
            section = line[1:-1]
            if section in sections:
                if section in seen_sections:
                    raise ValueError('duplicate fixture descriptor section')
                seen_sections.add(section)
            continue
        if section not in sections:
            continue
        match = re.fullmatch(r'([A-Za-z0-9_.]+)\s*=\s*(.+)', line)
        if not match:
            raise ValueError('unsupported fixture descriptor line')
        key, value = match.groups()
        if any(previous == key for previous, _ in sections[section]):
            raise ValueError('duplicate fixture descriptor key')
        if value.startswith('{'):
            parts = []
            depth = 0
            quoted = escaped = False
            while True:
                parts.append(value)
                for character in value:
                    if quoted:
                        if escaped:
                            escaped = False
                        elif character == '\\':
                            escaped = True
                        elif character == '"':
                            quoted = False
                    elif character == '"':
                        quoted = True
                    elif character == '{':
                        depth += 1
                        if depth > 32:
                            raise ValueError('fixture dictionary nesting limit exceeded')
                    elif character == '}':
                        depth -= 1
                        if depth < 0:
                            raise ValueError('invalid fixture dictionary braces')
                if depth == 0 and not quoted:
                    break
                if index >= len(lines):
                    raise ValueError('unterminated fixture dictionary')
                value = lines[index]
                index += 1
            value = _remove_trailing_commas('\n'.join(parts))
        parsed = json.loads(value, object_pairs_hook=_unique)
        sections[section].append((key, parsed))
    return sections

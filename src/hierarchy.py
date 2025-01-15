import sys

# ----------------------------------------------------
#     STEP 1: HIERARCHY INPUT & CRITERIA AHP
# ----------------------------------------------------

def parse_hierarchy(input_string):
    """
    Parse a hierarchy string like 'A, B{a, b{i, ii}}, C' into a nested dictionary.
    """
    def parse_level(text):
        hierarchy = {}
        stack = []
        current = hierarchy
        buffer = ""

        for char in text:
            if char == '{':
                if buffer.strip():
                    stack.append((current, buffer.strip()))
                    current[buffer.strip()] = {}
                    current = current[buffer.strip()]
                    buffer = ""
            elif char == '}':
                if buffer.strip():
                    current[buffer.strip()] = {}
                    buffer = ""
                if stack:
                    current, _ = stack.pop()
            elif char == ',':
                if buffer.strip():
                    current[buffer.strip()] = {}
                    buffer = ""
            else:
                buffer += char

        if buffer.strip():
            current[buffer.strip()] = {}

        return hierarchy

    if input_string.count('{') != input_string.count('}'):
        raise ValueError("Mismatched brackets in the input hierarchy.")
    return parse_level(input_string)


def display_hierarchy(hierarchy, indent=0):
    for key, value in hierarchy.items():
        print("  " * indent + f"- {key}")
        if value:
            display_hierarchy(value, indent + 1)

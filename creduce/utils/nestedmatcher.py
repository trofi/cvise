#!/usr/bin/env python3

import enum
import re

@enum.unique
class BalancedExpr(enum.Enum):
    parens = ("(", ")")
    brackets = ("[", "]")
    curlys = ("{", "}")
    angles = ("<", ">")

class Pattern:
    pass

class RegExPattern(Pattern):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return "(expr={})".format(self.expr)

class BalancedPattern(Pattern):
    def __init__(self, expr):
        self.start = expr.value[0]
        self.end = expr.value[1]

    def __repr__(self):
        return "(start={}, end={})".format(self.start, self.end)

class OrPattern(Pattern):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return "(left={}, right={})".format(self.left, self.right)

def __get_regex_match(pattern, string, pos=0, search=False):
    regex = re.compile(pattern.expr, flags=re.DOTALL)

    if search:
        m = regex.search(string, pos=pos)
    else:
        m = regex.match(string, pos=pos)

    if m is not None:
        return (m.start(), m.end())
    else:
        return None

def __get_balanced_match(pattern, string, pos=0, search=False):
    if pos < 0 or pos >= len(string):
        return None

    if search:
        pos = string.find(pattern.start, pos)

        if pos == -1:
            return None
    else:
        if string[pos] != pattern.start:
            return None

    start_pos = pos
    depth = 1
    pos += 1

    while pos < len(string) and depth > 0:
        if string[pos] == pattern.start:
            depth += 1
        elif string[pos] == pattern.end:
            depth -= 1

        pos += 1

    if depth != 0:
        return None

    return (start_pos, pos)

def __get_leftmost_match(matches):
    matches = filter(lambda m: m is not None, matches)

    leftmost = next(matches, None)

    if leftmost is not None:
        for m in matches:
            if m[0] < leftmost[0]:
                leftmost = m

        return leftmost

def __match_pattern(pattern, string, pos=0, search=False):
    if isinstance(pattern, OrPattern):
        left_match = __match_pattern(pattern.left, string, pos=pos, search=search)
        right_match = __match_pattern(pattern.right, string, pos=pos, search=search)

        return __get_leftmost_match([left_match, right_match])
    elif isinstance(pattern, BalancedPattern):
        match = __get_balanced_match(pattern, string, pos=pos, search=search)
    elif isinstance(pattern, RegExPattern):
        match = __get_regex_match(pattern, string, pos=pos, search=search)
    else:
        return None

    return match

def __unify_part(part):
    if not isinstance(part, tuple):
        part = (part, None)

    return part

def find(expr, string, pos=0, prefix=""):
    parts = []

    if prefix:
        parts.append(RegExPattern(prefix))

    parts.append(BalancedPattern(expr))

    matches = search(parts, string, pos)

    if matches:
        return matches["all"]
    else:
        return None

def search(parts, string, pos=0):
    if not parts or pos < 0 or pos >= len(string):
        return None

    start_pos = pos
    found_complete_match = False

    while not found_complete_match and start_pos < len(string):
        (pattern, _) = __unify_part(parts[0])

        match = __match_pattern(pattern, string, pos=start_pos, search=True)

        if match is None:
            return None
        else:
            start_pos = match[0]

        matches = {}
        pos = start_pos
        found_complete_match = True

        for part in parts:
            (pattern, name) = __unify_part(part)

            print("Pattern: " + str(pattern))

            match = __match_pattern(pattern, string, pos=pos, search=False)

            if match is None:
                start_pos += 1
                found_complete_match = False
                print("No complete match")
                break

            print("Match: " + str(match) + " -> |" + string[match[0]:match[1]] + "|")

            if name is not None:
                matches[name] = match

            pos += match[1] - match[0]

    if found_complete_match:
        matches["all"] = (start_pos, pos)
        return matches
    else:
        return None

#!/usr/bin/env python3
"""Subset Construction (Kozen 1997, Lecture 6): NFA -> equivalent DFA.

Reads one or more NFAs from standard input and prints, for each one, the
transition table of the deterministic automaton M built with the subset
construction:

    Q_M       = 2^{Q_N}
    delta_M(A, a) = union of Delta_N(p, a) for p in A
    s_M       = S_N
    F_M       = { A subset of Q_N | A intersect F_N != empty }

By default only the states of M that are accessible from s_M are printed
(the inaccessible ones can never be reached and do not change L(M)).
Run with --all to print every subset of Q_N, exactly as in the formal
definition.
"""

import re
import sys
from collections import deque
from itertools import combinations

TOKEN_RE = re.compile(r"[{}]|\d+")


# ----------------------------------------------------------------------------
# Input
# ----------------------------------------------------------------------------

def parse_sets(text):
    """Parse a line such as '3 {2 4} 0 5' into a list of frozensets.

    '{...}' is a set, a bare '0' is the empty set and any other bare number n
    is the singleton {n}. Commas inside braces are tolerated: '{1,5}'.
    """
    sets = []
    current = None  # elements of the set being read, or None outside braces
    for tok in TOKEN_RE.findall(text):
        if tok == "{":
            current = set()
        elif tok == "}":
            sets.append(frozenset(current or ()))
            current = None
        elif current is not None:
            current.add(int(tok))
        else:
            n = int(tok)
            sets.append(frozenset() if n == 0 else frozenset([n]))
    return sets


def parse_states(text):
    """Parse a line of states such as '3 5' ('0' or '{}' means none)."""
    states = set()
    for s in parse_sets(text):
        states |= s
    return frozenset(states)


def read_cases(stream):
    """Yield (n, start, alphabet, final, delta) for every case in the input."""
    lines = (line.strip() for line in stream)
    lines = iter([line for line in lines if line])  # ignore blank lines

    cases = int(next(lines))
    for _ in range(cases):
        n = int(next(lines))
        start = parse_states(next(lines))
        alphabet = next(lines).split()
        final = parse_states(next(lines))

        delta = {}
        for row_number in range(1, n + 1):
            row = parse_sets(next(lines))
            if len(row) == len(alphabet) + 1:  # row begins with its state
                state = next(iter(row[0]))
                row = row[1:]
            elif len(row) == len(alphabet):  # row without state label
                state = row_number
            else:
                raise ValueError(
                    f"row {row_number} has {len(row)} entries, expected "
                    f"{len(alphabet)} (one per symbol)"
                )
            for symbol, targets in zip(alphabet, row):
                delta[(state, symbol)] = targets

        yield n, start, alphabet, final, delta


# ----------------------------------------------------------------------------
# Subset construction
# ----------------------------------------------------------------------------

def step(delta, subset, symbol):
    """delta_M(A, a) = Delta_N-hat(A, a) = union of Delta_N(p, a), p in A."""
    result = set()
    for p in subset:
        result |= delta.get((p, symbol), frozenset())
    return frozenset(result)


def subset_construction(n, start, alphabet, final, delta, all_subsets=False):
    """Build the DFA M = (Q_M, Sigma, delta_M, s_M, F_M).

    Returns (states, transitions, s_M, F_M) where `states` is the list of
    states of M (each a frozenset of NFA states) in the order they are
    printed, and transitions[(A, a)] = delta_M(A, a).
    """
    s_m = frozenset(start)
    transitions = {}

    if all_subsets:
        # Q_M = 2^{Q_N}: every subset, ordered by size and then lexically.
        q_n = range(1, n + 1)
        states = [frozenset(c) for k in range(n + 1)
                  for c in combinations(q_n, k)]
        # Show the start state first for readability.
        states.remove(s_m)
        states.insert(0, s_m)
        for a_set in states:
            for symbol in alphabet:
                transitions[(a_set, symbol)] = step(delta, a_set, symbol)
    else:
        # Only the states reachable from s_M (breadth-first search).
        states = [s_m]
        seen = {s_m}
        queue = deque([s_m])
        while queue:
            a_set = queue.popleft()
            for symbol in alphabet:
                target = step(delta, a_set, symbol)
                transitions[(a_set, symbol)] = target
                if target not in seen:
                    seen.add(target)
                    states.append(target)
                    queue.append(target)

    f_m = {a_set for a_set in states if a_set & final}
    return states, transitions, s_m, f_m


# ----------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------

def show(subset):
    """Same notation as the input: '{1 5}' for sets, '0' for the empty set."""
    if not subset:
        return "0"
    return "{" + " ".join(str(q) for q in sorted(subset)) + "}"


def format_table(alphabet, states, transitions, s_m, f_m):
    """Return the table of M as a list of lines.

    The first column marks the state: '->' start, '<-' final, '<->' both,
    following the convention of the assignment's table.
    """
    def mark(a_set):
        if a_set == s_m and a_set in f_m:
            return "<->"
        if a_set == s_m:
            return "->"
        if a_set in f_m:
            return "<-"
        return ""

    rows = [["", ""] + list(alphabet)]
    for a_set in states:
        rows.append([mark(a_set), show(a_set)]
                    + [show(transitions[(a_set, s)]) for s in alphabet])

    widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    return ["  ".join(cell.ljust(w) for cell, w in zip(row, widths)).rstrip()
            for row in rows]


def main():
    all_subsets = "--all" in sys.argv[1:]
    for n, start, alphabet, final, delta in read_cases(sys.stdin):
        dfa = subset_construction(n, start, alphabet, final, delta, all_subsets)
        print("\n".join(format_table(alphabet, *dfa)))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import functools
from pathlib import Path

# A hand is a string of length 5.
HandType = str
# List of (hand, bid amount).
InputType = list[tuple[HandType, int]]
ResultType = int


def load(input_path: Path) -> InputType:
    with open(input_path) as f:
        return [(hand, int(bid)) for hand, bid in [line.strip().split() for line in f.readlines()]]


def part1(input_data: InputType) -> ResultType:
    card_values = "AKQJT98765432"

    def hand_type_score(h: HandType) -> int:
        """
        Return an integer representing the quality of a hand based only on its 'type'.
        A full 6 points for 'five of a kind', down to 0 points for 'high card'.
        """
        return {
            (5,): 6,  # Five of a kind
            (4, 1): 5,  # Four of a kind
            (3, 2): 4,  # Full house
            (3, 1, 1): 3,  # Three of a kind
            (2, 2, 1): 2,  # Two pair
            (2, 1, 1, 1): 1,  # One pair
            (1, 1, 1, 1, 1): 0  # High card
        }[tuple([x for x in sorted([h.count(val) for val in card_values], reverse=True) if x != 0])]

    def compare_hands(a: HandType, b: HandType) -> int:
        a_score = hand_type_score(a)
        b_score = hand_type_score(b)
        if a_score < b_score:
            return -1
        if b_score < a_score:
            return 1

        for i in range(len(a)):
            if card_values.index(a[i]) > card_values.index(b[i]):
                return -1
            if card_values.index(b[i]) > card_values.index(a[i]):
                return 1

        return 0

    return sum([rank * hand[1] for rank, hand in
                enumerate(sorted(input_data, key=functools.cmp_to_key(lambda a, b: compare_hands(a[0], b[0]))), 1)])


def part2(input_data: InputType) -> ResultType:
    card_values = "AKQT98765432J"

    def hand_type_score(h: HandType) -> int:
        """
        Return an integer representing the quality of a hand based only on its 'type'.
        A full 6 points for 'five of a kind', down to 0 points for 'high card'.
        """
        hand_shape = [x for x in sorted([h.count(val) for val in card_values if val != "J"], reverse=True) if x != 0]
        if len(hand_shape) == 0:
            # Special case for hand JJJJJ
            hand_shape = [0]
        hand_shape[0] += h.count("J")
        return {
            (5,): 6,  # Five of a kind
            (4, 1): 5,  # Four of a kind
            (3, 2): 4,  # Full house
            (3, 1, 1): 3,  # Three of a kind
            (2, 2, 1): 2,  # Two pair
            (2, 1, 1, 1): 1,  # One pair
            (1, 1, 1, 1, 1): 0  # High card
        }[tuple(hand_shape)]

    # Remainder of solution is the same as part1.
    def compare_hands(a: HandType, b: HandType) -> int:
        a_score = hand_type_score(a)
        b_score = hand_type_score(b)
        if a_score < b_score:
            return -1
        if b_score < a_score:
            return 1

        for i in range(len(a)):
            if card_values.index(a[i]) > card_values.index(b[i]):
                return -1
            if card_values.index(b[i]) > card_values.index(a[i]):
                return 1

        return 0

    return sum([rank * hand[1] for rank, hand in
                enumerate(sorted(input_data, key=functools.cmp_to_key(lambda a, b: compare_hands(a[0], b[0]))), 1)])

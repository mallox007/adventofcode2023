from collections import Counter
from dataclasses import dataclass
from enum import Enum


@dataclass
class Hand:
    value: str
    type: Enum
    bid: int


class HandType(Enum):
    FIVE = 6000
    FOUR = 5000
    FULL = 4000
    THREE = 3000
    TWO = 2000
    ONE = 1000
    HIGH = 0


class CardGame:
    def __init__(self):
        self.card_strengths = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2', 'J']
        self.card_strengths.reverse()

    def handle(self, input: str) -> int:
        hands = []
        for line in input.splitlines():
            game_info = line.split(" ")
            value = game_info[0].strip()
            bid = int(game_info[1].strip())
            count = self.get_char_count(value)
            hand_type = self.get_hand_type(count)
            hands.append(Hand(value, hand_type, bid))

        hands.sort(key=lambda x: (x.type.value, [self.card_strengths.index(c) for c in x.value]))
        totals = 0
        for i, hand in enumerate(hands):
            totals = totals + (hand.bid * (i + 1))

        print(totals)

    def get_char_count(self, value: str) -> dict:
        counter = Counter(value)
        if 'J' not in counter:
            return counter
        else:
            max_items = counter.most_common(2)
            one = max_items[0]
            element_one = one[0]
            if len(max_items) == 1:
                counter[element_one] = 5
            else:
                two = max_items[1]
                element_two = two[0]
                count_one = one[1]
                count_two = two[1]
                joker_count = counter['J']
                count_source = count_one
                target = element_one
                if element_one == 'J':
                    count_source = count_two
                    target = element_two
                if count_source + joker_count >= 3:
                    counter[target] = count_source + joker_count
                elif count_one + count_two + joker_count >= 5:
                    max_count = max(count_one, count_two)
                    if max_count == count_one:
                        counter[element_one] = count_one + (3 - count_one)
                        counter[element_two] = count_two + joker_count - 3 + max_count
                    else:
                        counter[element_two] = count_two + (3 - count_two)
                        counter[element_one] = count_one + joker_count - 3 + max_count
                elif count_one + count_two + joker_count >= 4:
                    counter[element_two] = 2
                    counter[element_one] = 2
                elif count_one + count_two + joker_count >= 2:
                    max_count = max(count_one, count_two)
                    if max_count == count_one and element_one != 'J':
                        counter[element_one] = count_one + joker_count
                    else:
                        counter[element_two] = count_two + joker_count
                counter.pop('J')
        return counter

    def get_strength(self, value: str):
        strength = []
        for ch in value:
            strength.append(self.card_strengths.index(ch))

        return strength

    def get_hand_type(self, counter: dict):
        if any(hand == 5 for hand in counter.values()):
            return HandType.FIVE
        elif any(hand == 4 for hand in counter.values()):
            return HandType.FOUR
        elif set(counter.values()) == {2, 3}:
            return HandType.FULL
        elif (any(count == 3 for count in counter.values()) and any(hand == 1 for hand in counter.values())):
            return HandType.THREE
        elif list(counter.values()).count(2) == 2:
            return HandType.TWO
        elif 2 in counter.values() and 1 in counter.values():
            return HandType.ONE
        else:
            return HandType.HIGH


if __name__ == "__main__":
    with open("input.txt", 'r') as f:
        CardGame().handle(f.read())

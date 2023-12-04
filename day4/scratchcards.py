from dataclasses import dataclass


@dataclass
class CardPoints:
    card: int
    matches: int
    points: int
    multiplier: int = 1
    handled = False

    def add_hit(self):
        self.multiplier += 1

    def copy(self):
        copy = CardPoints(self.card, self.matches, self.points)
        copy.handled = False
        return copy

    def __str__(self):
        return f"Card {self.card}, matches: {self.matches}, copy: {self.handled}"


class ScratchCards:
    def __init__(self):
        pass

    def handle(self, input: str) -> int:
        cardpoints = []
        for line in input.splitlines():
            cardpoints.append(self.handle_line(line.strip()))

        self.calculateCardsSum(cardpoints)

    def calculateSum(self, cards: list[CardPoints]):
        sum = 0
        for card in cards:
            sum += card.points

        print(f"The total is {sum}")

    def calculateCardsSum(self, cards: list[CardPoints]):
        additional_cards = self.handle_cards(cards, cards)
        all_cards = []
        all_cards.extend(cards)
        all_cards.extend(additional_cards)
        groups = {}
        for card in all_cards:
            if card.card in groups:
                groups[card.card] += 1
            else:
                groups[card.card] = 1
        print(groups)
        total = len(all_cards)
        print(f"We have {total} cards")

    def handle_cards(self, cards, lookup_cards):
        additional_cards = []
        for card in cards:
            if not card.handled:
                start = card.card
                end = min(card.card + card.matches, len(lookup_cards))
                print(f"[{start}:{end}] total of {end - start}")
                for additional_card in lookup_cards[card.card: end]:
                    print(f"Match for card {card.card}, Adding copy of card ({additional_card})")
                    additional_cards.append(additional_card.copy())
                card.handled = True
        if not additional_cards:
            return additional_cards
        else:
            additional_cards.extend(self.handle_cards(additional_cards, lookup_cards))
            return additional_cards

    def handle_line(self, line) -> CardPoints:
        card_info = line.split(":")
        card = card_info[0].replace("Card", "").strip()
        card_playinfo = card_info[1].strip().split("|")
        winning_numbers = card_playinfo[0].strip().split(" ")
        own_numbers = card_playinfo[1].strip().split(" ")

        # print(line)
        first_match = True
        matches = 0
        line_total = 0
        for owned_number in [own_number for own_number in own_numbers if (own_number.strip() != "")]:
            if owned_number != " " and owned_number in winning_numbers:
                print(f"We have a match for {owned_number}")
                matches += 1
                if first_match:
                    first_match = False
                    line_total = 1
                else:
                    line_total = line_total * 2

        print(f"Card {card}: matches: {matches} total: {line_total}")
        return CardPoints(int(card), matches, line_total)


if __name__ == "__main__":
    with open("input.txt", 'r') as f:
        ScratchCards().handle(f.read())

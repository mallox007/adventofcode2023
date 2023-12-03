import re
import string
from dataclasses import dataclass


@dataclass
class NumberMatch:
    x: int
    y: int
    value: int

    def match_coordinates(self, elem):
        return elem.x == self.x and elem.y == self.y


class Lift:

    def __init__(self):
        super().__init__()
        self.valid_symbols = string.punctuation
        self.symbol_locations = []

    def is_valid_symbol(self, ch: str):
        return not ch.isdigit() and ch != '.'

    def is_valid_gear(self, ch: str):
        return ch == '*'

    def handle(self, text_input: str, gear_calc=False) -> int:

        all_matches = []
        self.determine_symbols(text_input, gear_calc)

        line_counter = 0
        for line in text_input.splitlines():
            all_matches.extend(self.handle_line(line.strip(), line_counter))
            line_counter += 1

        sum = 0
        if gear_calc:
            sum = self.calc_gears(all_matches)
        else:
            sum = self.calc_sum(all_matches)
        print(f"Sum is {sum}")
        return sum

    def calc_sum(self, all_matches: list[NumberMatch]):
        sum = 0
        for match in all_matches:
            sum += match.value

        return sum

    def calc_gears(self, all_matches: list[NumberMatch]):
        sum = 0
        processed_coordinates = []
        for match in all_matches:
            if match not in processed_coordinates:
                matching_gear = next((elem for elem in all_matches if elem.match_coordinates(match) and match != elem), None)
                if matching_gear:
                    print(f"Gear match for {match} and {matching_gear}")
                    processed_coordinates.append(matching_gear)
                    sum += (match.value * matching_gear.value)

        return sum

    def determine_symbols(self, text_input, gear_calc=False):
        for line in text_input.splitlines():
            line_symbols = []
            for i in range(len(line)):
                ch = line[i]
                is_symbol = False
                if gear_calc:
                    is_symbol = self.is_valid_gear(ch)
                else:
                    is_symbol = self.is_valid_symbol(ch)
                line_symbols.append(is_symbol)
            self.symbol_locations.append(line_symbols)

    def handle_line(self, line: str, line_index: int) -> list[NumberMatch]:
        line_matches = []
        all_number_matches = re.finditer('\d+', line)
        for number_match in all_number_matches:
            start_range = number_match.start()
            end_range = number_match.end()
            number = int(line[start_range:end_range])
            match = self.get_match(start_range, end_range, line, line_index, number)
            if len(match) > 0:
                print(f"number is a match {number}")
                line_matches.extend(match)
        return line_matches

    def get_match(self, start_range, end_range, line, line_index, number):
        start_scan = start_range
        end_scan = end_range
        if start_range > 0:
            start_scan = start_range - 1
        if end_range < len(line) + 1:
            end_scan = end_range + 1
        symbols_current_line: list[bool] = self.symbol_locations[line_index][start_scan:end_scan]
        number_matches = []
        if True in symbols_current_line:
            number_matches.append(NumberMatch(line_index, start_scan + symbols_current_line.index(True), number))
        if line_index > 0:
            symbols_previous_line = self.symbol_locations[line_index - 1][start_scan:end_scan]
            if True in symbols_previous_line:
                number_matches.append(NumberMatch(line_index - 1, start_scan + symbols_previous_line.index(True), number))
        if line_index < (len(self.symbol_locations) - 1):
            symbols_next_line = self.symbol_locations[line_index + 1][start_scan:end_scan]
            if True in symbols_next_line:
                number_matches.append(NumberMatch(line_index + 1, start_scan + symbols_next_line.index(True), number))

        return number_matches


if __name__ == "__main__":
    with open("input.txt", 'r') as f:
        Lift().handle(f.read(), True)

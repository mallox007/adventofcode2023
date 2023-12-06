import re
from dataclasses import dataclass


@dataclass
class Race:
    duration: int
    record: int

    def get_range(self):
        return range(1, self.duration - 1)

    def get_distance(self, start):
        return (self.duration - start) * start


class BoatRace:
    def __init__(self):
        pass

    def handle(self, input: str) -> int:
        lines = input.splitlines()
        durations = re.findall('\d+', lines[0].replace(" ", ""))
        records = re.findall('\d+', lines[1].replace(" ", ""))
        races: list[Race] = []

        for i, val in enumerate(durations):
            races.append(Race(int(val), int(records[i])))

        record_multiplier = 1
        for race in races:
            start = self.get_start_of_new_record(race)
            end = self.get_end_of_new_record(race)
            record_multiplier = (end - start + 1) * record_multiplier

        print(record_multiplier)

    def get_start_of_new_record(self, race: Race) -> int:
        for i in race.get_range():
            my_distance = race.get_distance(i)
            if my_distance > race.record:
                print(f"new record start {i}")
                return i

    def get_end_of_new_record(self, race: Race) -> int:
        records = 0
        for i in reversed(race.get_range()):
            my_distance = race.get_distance(i)
            if my_distance > race.record:
                print(f"new record end {i}")
                return i

        return records


if __name__ == "__main__":
    with open("input.txt", 'r') as f:
        BoatRace().handle(f.read())

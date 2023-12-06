import math
import multiprocessing
import re
from collections import defaultdict
from dataclasses import dataclass
from multiprocessing import Queue


@dataclass
class Interval:
    start: int
    end: int
    type: str
    dynamic: bool = False

    def intersect(self, start, end):
        return end >= self.start and start <= self.end


@dataclass
class SeedMapping:
    sourceName: str
    destinationName: str
    source_start: int
    source_end: int
    destination_start: int
    destination_end: int
    proxy: bool = False

    def get_destination_val(self, source_value):
        return self.destination_start + abs(self.source_start - source_value)

    def get_destination_match(self, val, dest):
        if self.destinationName == dest:
            if self.destination_start <= val <= self.destination_end:
                return self.source_start + abs(self.destination_start - val)
            elif self.proxy:
                return val
        else:
            return None

    def get_source_match(self, val, source):
        if self.sourceName == source:
            if self.source_start <= val <= self.source_end:
                return self.destination_start + abs(self.source_start - val)
            elif self.proxy:
                return val
        else:
            return None

    def intersect(self, start, end):
        return end >= self.source_start and start <= self.source_end


@dataclass
class SeedRange:
    start: int
    length: int
    end: int

    def __init__(self, start, length):
        self.start = start
        self.length = length
        self.end = self.start + self.length - 1

    def in_range(self, val):
        return self.start <= val <= self.end

    def intersect(self, seed_range):
        return seed_range.end >= self.start and seed_range.start <= self.end

    def merge(self, seed_range):
        if seed_range.start < self.start:
            self.start = seed_range.start
        if seed_range.end > self.end:
            self.end = seed_range.end


class Seeding:
    def __init__(self):
        self.destinations = ['seed', 'soil', 'fertilizer', 'water', 'light', 'temperature', 'humidity',
                             'location']
        self.groups: dict[str, list[SeedMapping]] = defaultdict(list)

    def handle(self, input: str) -> int:
        seed_request = []
        mappings = []
        seed_map_init = re.compile("([a-z]+)-to-([a-z]+) map")
        active_seed_map = None
        seed_map_info = []
        for line in input.splitlines():
            if active_seed_map:
                if line != "":
                    seed_map_info.append(line)
                else:
                    mappings.extend(self.build_mapping(active_seed_map, seed_map_info))
                    active_seed_map = None
                    seed_map_info = []
            if line.startswith("seeds:"):
                seed_request = re.findall('\d+', line)
            match = seed_map_init.match(line)
            if match:
                active_seed_map = match.groups()
        mappings.extend(self.build_mapping(active_seed_map, seed_map_info))

        for mapping in mappings:
            self.groups[mapping.sourceName].append(mapping)

        ranges = self.process_request(seed_request)
        min_val = self.process_ranges(ranges)
        print(f"min {min_val}")

    def process_request(self, seeds) -> list[SeedRange]:
        tuples = []
        current_tuple = []
        merged_tuples = []
        for seed in seeds:
            current_tuple.append(int(seed))
            if len(current_tuple) == 2:
                print(f"creating Tuple: {current_tuple[0]} {current_tuple[1]}")
                tuples.append(SeedRange(current_tuple[0], current_tuple[1]))
                current_tuple = []
        for seed_tuple in tuples:
            if len(merged_tuples) == 0:
                merged_tuples.append(seed_tuple)
            else:
                merged = False
                for merged_tuple in merged_tuples:
                    if merged_tuple.intersect(seed_tuple):
                        print("merging")
                        merged = True
                        merged_tuple.merge(seed_tuple)
                if not merged:
                    merged_tuples.append(seed_tuple)
        return tuples


    def build_custom_range(self, start, end, target, destination='seed'):
        destination_name = None
        min_match = None
        max_match = None
        for seed_mapping in self.groups[destination]:
            if seed_mapping.intersect(start, end):
                calc_start = seed_mapping.get_destination_val(max(start, seed_mapping.source_start))
                min_match = self.min_null_safe(calc_start, min_match)
                calc_end = seed_mapping.get_destination_val(min(end, seed_mapping.source_end))
                target[destination].append(Interval(calc_start, calc_end, seed_mapping.destinationName))
                max_match = self.max_null_safe(calc_end, max_match)
                if seed_mapping.destinationName:
                    self.build_custom_range(calc_start,
                                            calc_end, target,
                                            seed_mapping.destinationName)
            else:
                destination_name = seed_mapping.destinationName

        if len(self.groups[destination]) > 0:
            if min_match and min_match > start and destination_name:
                target[destination].append(Interval(start, min_match, destination_name, True))
                self.build_custom_range(start, min_match - 1, target, destination_name)
            if max_match and max_match < end and destination_name:
                target[destination].append(Interval(max_match + 1, end, destination_name, True))
                self.build_custom_range(max_match + 1, end, target, destination_name)
            if len(target[destination]) == 0:
                target[destination].append(Interval(start, end, destination_name, True))
                if destination_name:
                    self.build_custom_range(start,
                                            end, target,
                                            destination_name)
            target[destination_name].sort(key=lambda x: x.start)

    def process_ranges(self, seed_ranges: list[SeedRange]):
        results = []
        for seed_range in seed_ranges:
            self.fast_min_for_range(seed_range, results)

        results.sort()
        results.reverse()
        valid = False
        min_value = None
        while not valid and len(results) > 0:
            found_value = results.pop()
            seed_id = self.get_soil(self.groups, found_value, counter=len(self.destinations) - 1)
            found_in_range = False
            for seed_range in seed_ranges:
                if seed_range.in_range(seed_id):
                    found_in_range = True
            if found_in_range:
                min_value = self.min_null_safe(min_value, found_value)
        return min_value

    def fast_min_for_range(self, seed_range: SeedRange, results):
        custom_mapping: dict[str, list[Interval]] = defaultdict(list)
        self.build_custom_range(seed_range.start, seed_range.end, custom_mapping)
        for mapping in custom_mapping['humidity']:
            results.append(mapping.start)

    def get_soil(self, global_mappings, seed, counter=0, destination_type='location'):
        # print(f"Destination {destination_type}")
        source_type = self.destinations[counter]
        mappings = global_mappings[source_type]
        seed_val = int(seed)
        dest_mapping = next(
            (location for location in mappings if location.get_destination_match(seed_val, destination_type)),
            self.get_fallback(destination_type, seed_val, source_type))

        source_value = dest_mapping.get_destination_match(seed_val, destination_type)
        # print(f"{dest_mapping.sourceName} {source_value} at {dest_mapping.destinationName} {seed_val}")
        current_counter = counter - 1
        if current_counter >= 0:
            return self.get_soil(global_mappings, source_value,
                                 current_counter, destination_type=dest_mapping.sourceName)
        else:
            return source_value

    def min_null_safe(self, destination_value, min_value):
        if not min_value:
            return destination_value
        if not destination_value:
            return min_value

        return min(min_value, destination_value)

    def max_null_safe(self, destination_value, max_value):
        if not max_value:
            return destination_value
        if not destination_value:
            return max_value

        return max(max_value, destination_value)

    def get_fallback(self, destination_type, seed_val, source_type):
        return SeedMapping(source_type, destination_type, seed_val, seed_val, seed_val, seed_val, True)

    def build_mapping(self, mapping_info, lines) -> list[SeedMapping]:
        source_name = mapping_info[0]
        destination_name = mapping_info[1]
        mappings = []
        for line in lines:
            all_number_matches = re.findall('\d+', line)
            source_start = int(all_number_matches[1])
            destination_start = int(all_number_matches[0])
            amount = int(all_number_matches[2])
            # print(f"{source_name} -> {destination_name} {amount} [{source_start}:{source_start + amount - 1}]")
            mappings.append(SeedMapping(source_name, destination_name,
                                        source_start, source_start + amount - 1,
                                        destination_start,
                                        destination_start + amount - 1))

        return mappings


if __name__ == "__main__":
    with open("input.txt", 'r') as f:
        Seeding().handle(f.read())

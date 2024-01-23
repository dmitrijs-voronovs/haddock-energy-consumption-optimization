import re

import pandas as pd

from data_analysis.CLI.extractors.Parser import IndividualParser


class MemoryUtilizationParser(IndividualParser):
    @staticmethod
    def extract(file_path: str):
        timestamp_pattern = re.compile(r'^(\d{2}:\d{2}:\d{2} [APMapm]+)')
        header_pattern = re.compile(
            r'\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)$')

        timestamp = None
        memory_data = []

        with open(file_path, 'r') as file:
            try:
                for line in file:
                    timestamp_match = timestamp_pattern.match(line)
                    header_match = header_pattern.search(line)

                    if timestamp_match:
                        timestamp_str = timestamp_match.group(1)
                        timestamp = pd.to_datetime(timestamp_str)

                    if header_match:
                        memory_info = header_match.groups()
                        memory_data.append(
                            {'Timestamp': timestamp, 'kbmemfree': int(memory_info[0]), 'kbavail': int(memory_info[1]),
                             'kbmemused': int(memory_info[2]), '%memused': float(memory_info[3]),
                             'kbbuffers': int(memory_info[4]), 'kbcached': int(memory_info[5]),
                             'kbcommit': int(memory_info[6]), '%commit': float(memory_info[7]),
                             'kbactive': int(memory_info[8]), 'kbinact': int(memory_info[9]),
                             'kbdirty': int(memory_info[10]), 'kbanonpg': int(memory_info[11]),
                             'kbslab': int(memory_info[12]), 'kbkstack': int(memory_info[13]),
                             'kbpgtbl': int(memory_info[14]), 'kbvmused': int(memory_info[15])})
            except Exception as e:
                print(e)

        df = pd.DataFrame(memory_data)
        return df

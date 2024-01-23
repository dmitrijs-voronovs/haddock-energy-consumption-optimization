import re
from datetime import datetime

import pandas as pd

from data_analysis.CLI.extractors.Parser import IndividualParser


class CPUFrequencyParser(IndividualParser):
    @staticmethod
    def extract(file_path: str):
        timestamp_pattern = re.compile(r'^([a-zA-Z]{3} [a-zA-Z]{3} \d+ \d{2}:\d{2}:\d{2} [APMapm]+ UTC \d{4})')
        cpu_frequency_pattern = re.compile(r'^cpu MHz\s+:\s+(\d+\.\d+)')

        timestamp = None
        cpu_frequency_data = []
        cpu_idx = 0

        with open(file_path, 'r') as file:
            for line in file:
                timestamp_match = timestamp_pattern.match(line)
                cpu_frequency_match = cpu_frequency_pattern.match(line)

                if timestamp_match:
                    timestamp_str = timestamp_match.group(1)
                    timestamp = datetime.strptime(timestamp_str, '%a %b %d %I:%M:%S %p %Z %Y')
                    cpu_idx = 0

                if cpu_frequency_match:
                    cpu_frequency_info = cpu_frequency_match.groups()
                    cpu_frequency_data.append({
                        'Timestamp': timestamp,
                        'CPU': cpu_idx,
                        'CPU MHz': float(cpu_frequency_info[0])
                    })
                    cpu_idx += 1

        df = pd.DataFrame(cpu_frequency_data)
        return df

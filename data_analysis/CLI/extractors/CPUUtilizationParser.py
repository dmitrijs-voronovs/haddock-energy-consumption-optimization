import re
from datetime import datetime

import pandas as pd

from data_analysis.CLI.extractors.Parser import IndividualParser


class CPUUtilizationParser(IndividualParser):
    @staticmethod
    def extract(file_path: str):
        header_pattern = re.compile(
            r'^(\S+\s*\S+)\s+(\d+|all)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$')

        timestamp = None
        cpu_data = []

        with open(file_path, 'r') as file:
            try:
                for line in file:
                    match = header_pattern.search(line)

                    if match:
                        timestamp_str = match.group(1)
                        timestamp = datetime.strptime(timestamp_str, '%H:%M:%S %p')

                        cpu_info = match.groups()
                        cpu_data.append(
                            {'Timestamp': timestamp.isoformat(), 'CPU': cpu_info[1],
                             '%user': float(cpu_info[2]), '%nice': float(cpu_info[3]),
                             '%system': float(cpu_info[4]), '%iowait': float(cpu_info[5]),
                             '%steal': float(cpu_info[6]), '%idle': float(cpu_info[7])})
            except Exception as e:
                print(e)

        df = pd.DataFrame(cpu_data)
        return df

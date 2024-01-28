import re
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from data_analysis.CLI.extractors.CPUFrequencyParser import CPUFrequencyParser
from data_analysis.CLI.extractors.Parser import IndividualParser


class CPUUtilizationParser(IndividualParser):
    @staticmethod
    def get_start_date(file_path):
        timestamp_file = Path(file_path).parent / 'cpu_frequency.log'
        with open(timestamp_file, 'r') as file:
            timestamp_line = file.readline()
            timestamp_match = CPUFrequencyParser.timestamp_pattern.match(timestamp_line)
            timestamp = CPUFrequencyParser.extract_timestamp(timestamp_match)
            return timestamp.date()

    @staticmethod
    def get_timestamp(prev_date, date, timestamp_str):
        time = datetime.strptime(timestamp_str, '%I:%M:%S %p').time()
        timestamp = datetime.combine(date, time)

        new_date = date
        # Check if day has changed
        if prev_date and timestamp < datetime.fromisoformat(prev_date):
            new_date += timedelta(days=1)
            timestamp = datetime.combine(new_date, time)
        return timestamp, new_date

    @staticmethod
    def extract(file_path: str):
        header_pattern = re.compile(
            r'^(\S+\s*\S+)\s+(\d+|all)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$')

        try:
            date = CPUUtilizationParser.get_start_date(file_path)
        except ValueError:
            date = datetime.now().date()

        cpu_data = []

        with open(file_path, 'r') as file:
            try:
                for line in file:
                    match = header_pattern.search(line)

                    if match:
                        timestamp_str = match.group(1)
                        prev_date = cpu_data[-1]['Timestamp'] if cpu_data else None
                        timestamp, date = CPUUtilizationParser.get_timestamp(prev_date, date, timestamp_str)

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

from typing import List, Tuple

import pandas as pd

from data_analysis.CLI.extractors.Parser import CombinedParser


class CPUAvgFrequencyParser(CombinedParser):
    # TODO: make dynamic by instantiating in constructor and making methods non-static
    DATA_PATH = 'cpu.csv'

    @staticmethod
    def extract_into_file(src: List[Tuple[str, str]], destination_path: str):
        avg_freq = []
        for job_name, file in src:
            try:
                data = pd.read_csv(file)
                data = data.groupby(['CPU']).mean('CPU MHz').mean()
                avg_freq.append({"JobName": job_name, "AVG_CPU_freq_MHz": float(data['CPU MHz'])})
            except FileNotFoundError:
                pass
            except Exception as e:
                print(f"Failed to extract data from file {file}", e)

        pd.DataFrame(avg_freq).to_csv(destination_path, index=False)

from typing import List

from examples.domain import Config, LocalConfig, LocalExperiment


class LocalExperimentGL6(LocalExperiment):
    def create_configs(self) -> List[Config]:
        return [
            LocalConfig(workflow, "gl6", trial, ncores)
            for workflow in ["dpp", "daa"]
            for ncores in [2, 4, 8, 16, 32]
            for trial in range(1, 11)
        ]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "gl6", 1, 8, True)

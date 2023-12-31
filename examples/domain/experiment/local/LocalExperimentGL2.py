from typing import List

from examples.domain import LocalExperiment
from examples.domain.config.Config import Config
from examples.domain.config.LocalConfig import LocalConfig


class LocalExperimentGL2(LocalExperiment):
    ID = "gl2"

    def create_configs(self) -> List[Config]:
        return [
            LocalConfig(workflow, "gl2", trial, ncores)
            for workflow in ["dpp", "daa"]
            for ncores in [2, 4, 8]
            for trial in range(1, 11)
        ]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "gl2", 1, 8, True)

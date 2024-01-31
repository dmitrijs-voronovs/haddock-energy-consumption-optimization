from typing import List

from examples.domain import LocalExperiment
from examples.domain.config.Config import Config
from examples.domain.config.LocalConfig import LocalConfig


class GL5_5(LocalExperiment):

    def create_configs(self) -> List[Config]:
        return [
            LocalConfig(workflow, "gl5", trial, ncores)
            for workflow in ["daa"]
            for ncores in [16, 32]
            for trial in range(41, 41 + 3)
        ]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "gl5", 41, 32, True)

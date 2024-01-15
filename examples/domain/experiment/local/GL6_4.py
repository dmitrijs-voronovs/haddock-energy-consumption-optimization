from typing import List

from examples.domain import LocalExperiment
from examples.domain.config.Config import Config
from examples.domain.config.LocalConfig import LocalConfig


class GL6_4(LocalExperiment):

    def create_configs(self) -> List[Config]:
        return [
            LocalConfig(workflow, "gl6", trial, ncores)
            for workflow in ["dpp"]
            for ncores in [2, 4, 8, 16, 32]
            for trial in range(31, 41)
        ]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "gl6", 31, 32, True)

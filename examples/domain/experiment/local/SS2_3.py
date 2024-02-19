from typing import List

from examples.domain import LocalExperiment
from examples.domain.config.Config import Config
from examples.domain.config.LocalConfig import LocalConfig


class SS2_3(LocalExperiment):

    def create_configs(self) -> List[Config]:
        return [
            LocalConfig(workflow, "ss2", trial, ncores)
            for workflow in ["daa", "dpp"]
            for ncores in [32]
            for trial in range(21, 21 + 10)
        ]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "ss2", 21, 32, True)

from typing import List

from examples.domain import LocalExperiment
from examples.domain.config.Config import Config
from examples.domain.config.LocalConfig import LocalConfig


class SS2_2(LocalExperiment):

    def create_configs(self) -> List[Config]:
        return [
            LocalConfig(workflow, "ss2", trial, ncores)
            for workflow in ["daa"]
            for ncores in [16, 32]
            for trial in range(11, 11 + 3)
        ]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "ss2", 11, 32, True)

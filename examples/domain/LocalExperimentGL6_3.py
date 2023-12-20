
from typing import List

from examples.domain import LocalExperiment
from examples.domain.Config import Config
from examples.domain.LocalConfig import LocalConfig

class LocalExperimentGl6_3(LocalExperiment):
    def create_configs(self) -> List[Config]:
        return [LocalConfig("daa", "gl6", trial, 4) for trial in range(20, 20 + 1)] + [LocalConfig("dpp", "gl6", trial, 4) for trial in range(20, 20 + 1)]

    def create_warmup_config(self) -> Config:
        return LocalConfig("daa", "gl6", 20, 4)

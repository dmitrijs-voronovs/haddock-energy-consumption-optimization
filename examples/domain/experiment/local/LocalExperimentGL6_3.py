from typing import List

from examples.domain import LocalExperiment
from examples.domain.config.Config import Config
from examples.domain.config.LocalConfig import LocalConfig


class LocalExperimentGL6_3(LocalExperiment):
    ID = "gl6_3"

    def create_configs(self) -> List[Config]:
        return [LocalConfig("daa", "gl6", trial, 4) for trial in range(20, 20 + 1)] + [
            LocalConfig("dpp", "gl6", trial, 4) for trial in range(20, 20 + 1)]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "gl6", 20, 32, True)

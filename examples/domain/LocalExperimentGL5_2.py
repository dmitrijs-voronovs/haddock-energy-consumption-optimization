
from typing import List

from examples.domain import LocalExperiment
from examples.domain.Config import Config
from examples.domain.LocalConfig import LocalConfig


class LocalExperimentGL5_2(LocalExperiment):
    def create_configs(self) -> List[Config]:
        return [LocalConfig("daa", "gl5", trial, 4) for trial in range(10, 10 + 2)] + [LocalConfig("daa", "gl5", trial, 8) for trial in range(10, 10 + 5)] + [LocalConfig("daa", "gl5", trial, 16) for trial in range(10, 10 + 2)] + [LocalConfig("daa", "gl5", trial, 32) for trial in range(10, 10 + 1)] + [LocalConfig("dpp", "gl5", trial, 4) for trial in range(10, 10 + 3)] + [LocalConfig("dpp", "gl5", trial, 8) for trial in range(10, 10 + 3)] + [LocalConfig("dpp", "gl5", trial, 16) for trial in range(10, 10 + 1)] + [LocalConfig("dpp", "gl5", trial, 32) for trial in range(10, 10 + 4)]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "gl5", 10, 32, True)

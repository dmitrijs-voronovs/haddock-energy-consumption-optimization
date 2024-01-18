
from typing import List

from examples.domain import LocalExperiment
from examples.domain.config.Config import Config
from examples.domain.config.LocalConfig import LocalConfig

class GL5_3(LocalExperiment):
    def create_configs(self) -> List[Config]:
        return [LocalConfig("daa", "gl5", trial, 4) for trial in range(21, 21 + 8)] + [LocalConfig("daa", "gl5", trial, 8) for trial in range(21, 21 + 8)] + [LocalConfig("dpp", "gl5", trial, 4) for trial in range(21, 21 + 9)] + [LocalConfig("dpp", "gl5", trial, 8) for trial in range(21, 21 + 9)] + [LocalConfig("dpp", "gl5", trial, 16) for trial in range(21, 21 + 5)] + [LocalConfig("dpp", "gl5", trial, 32) for trial in range(21, 21 + 7)]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "gl5", 21, 32, True)

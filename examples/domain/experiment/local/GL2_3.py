from typing import List

from examples.domain import LocalExperiment
from examples.domain.config.Config import Config
from examples.domain.config.LocalConfig import LocalConfig


class GL2_3(LocalExperiment):

    def create_configs(self) -> List[Config]:
        return [LocalConfig("daa", "gl2", trial, 8) for trial in range(20, 20 + 1)] + [
            LocalConfig("dpp", "gl2", trial, 8) for trial in range(20, 20 + 1)]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "gl2", 20, 8, True)

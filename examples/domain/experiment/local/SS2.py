from typing import List

from examples.domain import LocalExperiment
from examples.domain.config.Config import Config
from examples.domain.config.LocalConfig import LocalConfig


class SS2(LocalExperiment):
    def create_configs(self) -> List[Config]:
        return [LocalConfig("daa", "ss2", trial, 4) for trial in range(1, 1 + 8)] + [
            LocalConfig("daa", "ss2", trial, 8) for trial in range(1, 1 + 8)] + [LocalConfig("dpp", "ss2", trial, 4)
                                                                                 for trial in range(1, 1 + 9)] + [
            LocalConfig("dpp", "ss2", trial, 8) for trial in range(1, 1 + 9)] + [LocalConfig("dpp", "ss2", trial, 16)
                                                                                 for trial in range(1, 1 + 5)] + [
            LocalConfig("dpp", "ss2", trial, 32) for trial in range(1, 1 + 7)]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "ss2", 1, 32, True)

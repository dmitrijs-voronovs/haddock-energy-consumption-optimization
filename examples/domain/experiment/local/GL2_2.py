from typing import List

from examples.domain import LocalExperiment
from examples.domain.config.Config import Config
from examples.domain.config.LocalConfig import LocalConfig


class GL2_2(LocalExperiment):

    def create_configs(self) -> List[Config]:
        return [LocalConfig("daa", "gl2", trial, 2) for trial in range(11, 11 + 8)] + [
            LocalConfig("daa", "gl2", trial, 4) for trial in range(11, 11 + 4)] + [LocalConfig("daa", "gl2", trial, 8)
                                                                                   for trial in range(11, 11 + 2)] + [
            LocalConfig("dpp", "gl2", trial, 2) for trial in range(11, 11 + 8)] + [LocalConfig("dpp", "gl2", trial, 4)
                                                                                   for trial in range(11, 11 + 0)] + [
            LocalConfig("dpp", "gl2", trial, 8) for trial in range(11, 11 + 4)]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "gl2", 1, 8, True)

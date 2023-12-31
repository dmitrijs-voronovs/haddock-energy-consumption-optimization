from typing import List

from examples.domain import LocalExperiment
from examples.domain.config.Config import Config
from examples.domain.config.LocalConfig import LocalConfig


class LocalExperimentGL5(LocalExperiment):
    ID = "gl5"

    def create_configs(self) -> List[Config]:
        return [LocalConfig("daa", "gl5", trial, 2) for trial in range(11, 11 + 9)] + [
            LocalConfig("daa", "gl5", trial, 4) for trial in range(11, 11 + 2)] + [LocalConfig("daa", "gl5", trial, 8)
                                                                                   for trial in range(11, 11 + 5)] + [
            LocalConfig("daa", "gl5", trial, 16) for trial in range(11, 11 + 2)] + [LocalConfig("daa", "gl5", trial, 32)
                                                                                    for trial in range(11, 11 + 1)] + [
            LocalConfig("dpp", "gl5", trial, 2) for trial in range(11, 11 + 9)] + [LocalConfig("dpp", "gl5", trial, 4)
                                                                                   for trial in range(11, 11 + 3)] + [
            LocalConfig("dpp", "gl5", trial, 8) for trial in range(11, 11 + 3)] + [LocalConfig("dpp", "gl5", trial, 16)
                                                                                   for trial in range(11, 11 + 2)] + [
            LocalConfig("dpp", "gl5", trial, 32) for trial in range(11, 11 + 4)]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "gl5", 1, 8, True)

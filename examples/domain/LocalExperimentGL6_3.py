from typing import List

from examples.domain import Config, LocalConfig, LocalExperiment


class LocalExperimentGL6_3(LocalExperiment):
    def create_configs(self) -> List[Config]:
        return [LocalConfig("daa", "gl6", trial, 4) for trial in range(11, 11 + 1)] + [
            LocalConfig("daa", "gl6", trial, 8) for trial in range(11, 11 + 4)] + [LocalConfig("daa", "gl6", trial, 16)
                                                                                   for trial in range(11, 11 + 0)] + [
            LocalConfig("daa", "gl6", trial, 32) for trial in range(11, 11 + 0)] + [LocalConfig("dpp", "gl6", trial, 4)
                                                                                    for trial in range(11, 11 + 2)] + [
            LocalConfig("dpp", "gl6", trial, 8) for trial in range(11, 11 + 2)] + [LocalConfig("dpp", "gl6", trial, 16)
                                                                                   for trial in range(11, 11 + 1)] + [
            LocalConfig("dpp", "gl6", trial, 32) for trial in range(11, 11 + 1)]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "gl6", 1, 20, True)

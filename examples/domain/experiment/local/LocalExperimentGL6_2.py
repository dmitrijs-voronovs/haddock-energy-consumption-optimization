from typing import List

from examples.domain import Config, LocalConfig, LocalExperimentGL6


class LocalExperimentGL6_2(LocalExperimentGL6):
    def get_ID(self):
        return "gl6_2"

    def create_configs(self) -> List[Config]:
        return [LocalConfig("daa", "gl6", trial, 4) for trial in range(11, 11 + 1)] + [
            LocalConfig("daa", "gl6", trial, 8) for trial in range(11, 11 + 4)] + [LocalConfig("daa", "gl6", trial, 16)
                                                                                   for trial in range(11, 11 + 0)] + [
            LocalConfig("daa", "gl6", trial, 32) for trial in range(11, 11 + 0)] + [LocalConfig("dpp", "gl6", trial, 4)
                                                                                    for trial in range(11, 11 + 2)] + [
            LocalConfig("dpp", "gl6", trial, 8) for trial in range(11, 11 + 2)] + [LocalConfig("dpp", "gl6", trial, 16)
                                                                                   for trial in range(11, 11 + 1)] + [
            LocalConfig("dpp", "gl6", trial, 32) for trial in range(11, 11 + 1)]

    def get_experiment_job_dependency(self):
        # dependency of last job of GL6_1 experiment
        return '43262'

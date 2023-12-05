from typing import List

from examples.domain import Config, LocalConfig
from examples.domain.Experiment import Experiment


class LocalExperimentGL6(Experiment):
    def get_ncores(self, config: LocalConfig):
        return config.ncores

    def get_create_job_script_name(self):
        return "create-local-job.sh"

    def create_configs(self) -> List[Config]:
        return [
            LocalConfig(workflow, "gl6", trial, ncores)
            for workflow in ["dpp", "daa"]
            for ncores in [2, 4, 8, 16, 32]
            for trial in range(1, 11)
        ]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "gl6", 1, 8, True)
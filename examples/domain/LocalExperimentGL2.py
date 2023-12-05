from typing import List

from examples.domain.Config import Config
from examples.domain.LocalConfig import LocalConfig
from examples.domain import Experiment


class LocalExperimentGL2(Experiment):
    def get_ncores(self, config: LocalConfig):
        return config.ncores

    def get_create_job_script_name(self):
        return "create-local-job.sh"

    def create_configs(self) -> List[Config]:
        return [
            LocalConfig(workflow, "gl2", trial, ncores)
            for workflow in ["dpp", "daa"]
            for ncores in [2, 4, 8]
            for trial in range(1, 11)
        ]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "gl2", 1, 8, True)
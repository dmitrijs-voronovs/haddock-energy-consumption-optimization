from typing import List

from examples.domain.Config import Config
from examples.domain.HPCConfig import HPCConfig
from examples.domain import Experiment

TOTAL_CORES = 72


class HPCExperiment(Experiment):
    def get_ncores(self, config: HPCConfig):
        return TOTAL_CORES

    def get_create_job_script_name(self):
        return "create-hpc-job.sh"

    def create_configs(self) -> List[Config]:
        return [
            # TODO: thing about node - maybe it should be array? or None should be allowed
            HPCConfig(workflow, "gl2", trial, concat, queue_limit)
            for workflow in ["dpp", "daa"]
            for concat in [1, 16, 32]
            for queue_limit in [50, 100, 4949]
            for trial in range(1, 11)
        ]

    def create_warmup_config(self) -> Config:
        return HPCConfig("dpp", "gl2", 1, 32, 4949, True)
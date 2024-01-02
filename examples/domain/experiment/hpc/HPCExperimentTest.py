from typing import List

from examples.domain.config.Config import Config
from examples.domain.config.HPCConfig import HPCConfig
from examples.domain.experiment.Experiment import Experiment

TOTAL_CORES = 72


class HPCExperimentTest(Experiment):
    ID = "test"

    def get_ncores(self, config: HPCConfig):
        return TOTAL_CORES

    def create_configs(self) -> List[Config]:
        return [
            HPCConfig(workflow, ["gl2", "gl5", "gl6"], trial, concat, queue_limit)
            for workflow in ["dpp", "daa"]
            for concat in [1, 5, 10]
            for queue_limit in [72, 72 // 2, 72 // 4, 72 // 8]
            for trial in range(1, 11)
        ]

    def create_warmup_config(self) -> Config:
        return HPCConfig("dpp", ["gl2", "gl5", "gl6"], 1, 10, 72, True)

from typing import List

from examples.domain.config.Config import Config
from examples.domain.config.HPCConfig import HPCConfig
from examples.domain.experiment.hpc.HPCExperiment import HPCExperiment


class Test_2(HPCExperiment):
    def create_configs(self) -> List[Config]:
        return [
            HPCConfig(workflow, ["gl2", "gl5", "gl6"], 11, concat, queue_limit)
            for workflow in ["dpp"]
            for concat in [1, 5, 10]
            for queue_limit in [72 // 4, 72 // 8]
            # for trial in range(1, 11)
        ]

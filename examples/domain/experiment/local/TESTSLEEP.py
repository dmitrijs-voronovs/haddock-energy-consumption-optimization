from typing import List

from examples.domain import LocalExperiment
from examples.domain.config.Config import Config
from examples.domain.config.LocalConfig import LocalConfig


class TESTSLEEP(LocalExperiment):
    def create_configs(self) -> List[Config]:
        return [LocalConfig("daa", "gl2", "test", 4)]

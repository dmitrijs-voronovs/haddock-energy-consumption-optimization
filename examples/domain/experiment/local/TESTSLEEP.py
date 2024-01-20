from typing import List

from examples.domain import LocalExperiment
from examples.domain.config.Config import Config
from examples.domain.config.LocalConfig import LocalConfig


class TESTSLEEP(LocalExperiment):
    def create_configs(self) -> List[Config]:
        return [LocalConfig("daa", "gl2", f"test-{trial}", 4) for trial in range(1, 40)]

    def create_warmup_config(self) -> Config | None:
        return LocalConfig("daa", "gl2", "test-warmup", 2, is_warmup=True)

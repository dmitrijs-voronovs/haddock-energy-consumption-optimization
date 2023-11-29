from abc import ABC, abstractmethod
from functools import cached_property


class Config(ABC):
    def __init__(self, mode, workflow, node, trial, is_warmup=False):
        self.mode = mode
        self.workflow = workflow
        self.node = node
        self.trial = trial
        self.is_warmup = is_warmup

    # @cached_property
    @property
    def name(self):
        return f"{self.workflow}-{self.mode}-{self._get_params_for_name()}_{self.node}-{self.trial}.{'warmup.' if self.is_warmup else ''}cfg"

    # @cached_property
    @property
    def run_dir(self):
        return f"run.{self.name}"

    # @cached_property
    @property
    def node_name(self):
        return "GreenLab-STF" if self.node == "gl2" else self.node

    @abstractmethod
    def _get_params_for_name(self) -> str:
        pass

    @abstractmethod
    def get_params_for_create_command(self) -> str:
        pass


class LocalConfig(Config):
    def __init__(self, workflow, node, trial, ncores, is_warmup=False):
        super().__init__("local", workflow, node, trial, is_warmup)
        self.ncores = ncores

    def _get_params_for_name(self):
        return f"nc{self.ncores}"

    def get_params_for_create_command(self):
        return self.ncores
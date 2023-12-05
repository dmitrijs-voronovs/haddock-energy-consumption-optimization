from abc import ABC, abstractmethod


class Config(ABC):
    def __init__(self, mode, workflow, node, trial, is_warmup=False):
        self.mode = mode
        self.workflow = workflow
        self.node = node
        self.trial = trial
        self.is_warmup = is_warmup

    @property
    def name(self):
        return f"{self.workflow}-{self.mode}-{self._get_params_for_name()}_{self.node}-{self.trial}.{'warmup.' if self.is_warmup else ''}cfg"

    @property
    def run_dir(self):
        return f"run.{self.name}"

    @property
    def node_name(self):
        return "GreenLab-STF" if self.node == "gl2" else self.node

    @abstractmethod
    def _get_params_for_name(self) -> str:
        pass

    @abstractmethod
    def get_params_for_create_command(self) -> str:
        pass
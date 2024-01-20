from abc import ABC, abstractmethod
from typing import List

NODE_NAME_MAP = {
    "gl2": "GreenLab-STF",
    "ss2": "superserver2",
    # Add other mappings here
}


class Config(ABC):
    def __init__(self, mode, workflow, nodes: str | List[str], trial, is_warmup=False):
        self.mode = mode
        self.workflow = workflow
        self.nodes: List[str] = [nodes] if isinstance(nodes, str) else sorted(nodes)
        self.trial = trial
        self.is_warmup = is_warmup

    @property
    def nodes_for_filename(self) -> str:
        return "-".join(self.nodes)

    @property
    def name(self):
        warmup_string = 'warmup.' if self.is_warmup else ''
        return f"{self.workflow}-{self.mode}-{self._get_params_for_filename()}_{self.nodes_for_filename}-{self.trial}.{warmup_string}cfg"

    @property
    def name_without_extension(self):
        return self.name.split(".")[0]

    @property
    def run_dir(self):
        return f"run.{self.name}"

    @property
    def node_names(self):
        return ",".join([NODE_NAME_MAP.get(node, node) for node in self.nodes])

    @abstractmethod
    def _get_params_for_filename(self) -> str:
        pass

    @abstractmethod
    def get_params_for_create_command(self) -> str:
        pass

from abc import ABC

from examples.domain.config.LocalConfig import LocalConfig
from examples.domain.experiment.Experiment import Experiment


class LocalExperiment(Experiment, ABC):
    def get_ncores(self, config: LocalConfig):
        return config.ncores

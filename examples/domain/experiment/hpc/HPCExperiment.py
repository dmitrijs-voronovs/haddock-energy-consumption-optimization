from examples.domain.config.HPCConfig import HPCConfig
from examples.domain.experiment.Experiment import Experiment

TOTAL_CORES = 72


class HPCExperiment(Experiment):
    def get_ncores(self, config: HPCConfig):
        return TOTAL_CORES

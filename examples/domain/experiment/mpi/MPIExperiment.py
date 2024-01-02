from examples.domain.config.MPIConfig import MPIConfig
from examples.domain.experiment.Experiment import Experiment

TOTAL_CORES = 72


class MPIExperiment(Experiment):
    def get_ncores(self, config: 'MPIConfig'):
        return TOTAL_CORES

    def get_command_for_haddock_execution(self, config: 'MPIConfig') -> str:
        return f'sh "{config.get_job_script()}"'

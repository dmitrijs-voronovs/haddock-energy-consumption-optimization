from abc import ABC

from examples.domain import Experiment
from examples.domain.config.LocalConfig import LocalConfig


class LocalExperiment(Experiment, ABC):
    def get_ncores(self, config: LocalConfig):
        return config.ncores

    def get_create_job_script_name(self):
        return "create-local-job.sh"

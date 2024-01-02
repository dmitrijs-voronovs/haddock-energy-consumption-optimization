from examples.domain.config.Config import Config


class MPIConfig(Config):
    def __init__(self, workflow, node, trial, ncores, is_warmup=False):
        super().__init__("local", workflow, node, trial, is_warmup)
        self.ncores = ncores

    def _get_params_for_filename(self):
        return f"nc{self.ncores}"

    def get_params_for_create_command(self):
        return self.ncores

    def get_job_script(self):
        return f"{self.name_without_extension}.job"

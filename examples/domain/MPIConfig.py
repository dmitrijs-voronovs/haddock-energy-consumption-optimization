from examples.domain import Config


class LocalConfig(Config):
    def __init__(self, workflow, node, trial, ncores, is_warmup=False):
        super().__init__("local", workflow, node, trial, is_warmup)
        self.ncores = ncores

    def _get_params_for_name(self):
        return f"nc{self.ncores}"

    def get_params_for_create_command(self):
        return self.ncores
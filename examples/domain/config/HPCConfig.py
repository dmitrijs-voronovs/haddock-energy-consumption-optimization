from examples.domain.config.Config import Config


class HPCConfig(Config):
    def __init__(self, workflow, node, trial, concat, queue_limit, is_warmup=False):
        super().__init__("hpc", workflow, node, trial, is_warmup)
        self.concat = concat
        self.queue_limit = queue_limit

    def _get_params_for_filename(self):
        return f"con{self.concat}-ql{self.queue_limit}"

    def get_params_for_create_command(self):
        return f"{self.concat} {self.queue_limit}"

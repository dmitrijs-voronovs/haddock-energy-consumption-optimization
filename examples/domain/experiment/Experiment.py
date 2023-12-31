import random
from abc import ABC, abstractmethod
from typing import List

from examples.domain.config.Config import Config

COLLECT_INFO_AFTER_SH = "collect-info.after.sh"
COLLECT_INFO_BEFORE_SH = "collect-info.before.sh"


class Experiment(ABC):
    def __init__(self):
        self.create_job_script_name = self.get_create_job_script_name()
        self.configs = self.create_configs()
        self.warmup_config = self.create_warmup_config()

    @classmethod
    @property
    @abstractmethod
    def ID(cls) -> str:
        pass

    @abstractmethod
    def create_configs(self) -> List[Config]:
        pass

    @abstractmethod
    def create_warmup_config(self) -> Config:
        pass

    @abstractmethod
    def get_create_job_script_name(self):
        pass

    @abstractmethod
    def get_ncores(self, config: Config) -> int:
        pass

    def get_generate_create_job_script_name(self):
        return f"create-jobs.{self.ID}.sh"

    def get_exp_name(self):
        return f"run.{self.ID}.sh"

    def get_check_job_command_name(self):
        return f"check.{self.ID}.sh"

    def get_data_file_name(self):
        return f"data.{self.ID}.txt"

    def convert_config_to_create_workflow_command(self, config: Config) -> str:
        warmup_suffix = ' warmup' if config.is_warmup else ''
        return f"sh {self.create_job_script_name} {config.workflow} {config.get_params_for_create_command()} {config.nodes_for_filename} {config.trial}{warmup_suffix}"

    def generate_create_job_script(self):
        name = self.get_generate_create_job_script_name()
        commands = [self.convert_config_to_create_workflow_command(config) for config in
                    self.configs + [self.warmup_config]]

        with open(name, "w", newline='\n') as file:
            file.writelines("#!/bin/bash \n")
            file.writelines("\n".join(commands))

        return self

    def get_experiment_job_dependency(self) -> str | None:
        """Define dependency for the current experiment in order to execute it right after the previous one is
        finished"""
        return None

    def generate_runner(self):
        configs = self.configs.copy()
        random.shuffle(configs)
        warmup_config = self.warmup_config
        warmup_config_idx = 0
        configs.insert(warmup_config_idx, warmup_config)

        commands = ["#!/bin/bash \n", f"rm -rf \"{warmup_config.run_dir}\"\n", ]

        job_ids = []
        for (job_idx, config) in enumerate(configs):
            job_prev_id = f"job{job_idx - 1}_2"
            job_check_before_id = f"job{job_idx}_0"
            job_id = f"job{job_idx}_1"
            job_check_after_id = f"job{job_idx}_2"

            if job_idx > warmup_config_idx:
                job_ids.append(f"${job_id}")

            dependent_job_id = job_prev_id if job_idx > warmup_config_idx else self.get_experiment_job_dependency()
            commands.append(
                self.__get_slurm_command(job_check_before_id, f"info.before.{config.name}", config.node_names,
                                         len(config.nodes), COLLECT_INFO_BEFORE_SH, dependent_job_id))
            commands.append(self.__get_slurm_command(job_id, config.name, config.node_names, self.get_ncores(config),
                                                     f'haddock3 "{config.name}"', job_check_before_id))
            commands.append(self.__get_slurm_command(job_check_after_id, f"info.after.{config.name}", config.node_names,
                                                     len(config.nodes), COLLECT_INFO_AFTER_SH, job_id))

        check_jobs_command = self.__get_check_jobs_command(",".join(job_ids))

        with open(self.get_exp_name(), "w", newline='\n') as file:
            file.write("\n".join(commands))
            file.write(check_jobs_command)

    def __get_formatted_dependency(self, dependent_job_id):
        dependency = ""
        if dependent_job_id:
            var_sign = "$"
            if dependent_job_id.isdigit():
                var_sign = ""
            dependency = f" --dependency=afterany:{var_sign}{dependent_job_id}"
        return dependency

    def __get_slurm_command(self, id: str, name: str, nodes: str, ncores: int, command, dependent_job_id: str = None):
        dependency = self.__get_formatted_dependency(dependent_job_id)

        job_id_extraction_pipe = "| awk '{{print $NF}}'"
        return f'{id}=$(sbatch --job-name="{name}" -w {nodes} -n {ncores}{dependency} {command} {job_id_extraction_pipe})'

    def __get_check_jobs_command(self, job_ids):
        experiment_name = self.get_check_job_command_name()
        data_file_name = self.get_data_file_name()
        return f'''
cat > {experiment_name} << EOF
#!/bin/bash
echo {job_ids}
sacct -o jobid,jobname%60,cluster,Node%24,state,start,end,ConsumedEnergy,AveRSS,AveDiskRead,AveDiskWrite,AveVMSize,SystemCPU,UserCPU,AveCPU,elapsed,NCPUS \
    -j {job_ids} \
    > {data_file_name}
cat {data_file_name}
EOF
'''

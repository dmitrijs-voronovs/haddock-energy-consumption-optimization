import random
from abc import ABC, abstractmethod
from typing import List
from Config import Config, LocalConfig

COLLECT_INFO_AFTER_SH = "collect-info.after.sh"
COLLECT_INFO_BEFORE_SH = "collect-info.before.sh"


class Experiment(ABC):
    def __init__(self):
        self.create_job_script_name = self.get_create_job_script_name()
        self.configs = self.create_configs()
        self.warmup_config = self.create_warmup_config()

    @abstractmethod
    def create_configs(self) -> List[Config]:
        pass

    @abstractmethod
    def create_warmup_config(self) -> Config:
        pass

    @abstractmethod
    def get_create_job_script_name(self):
        pass

    def convert_config_to_create_workflow_command(self, config: Config) -> str:
        warmup_suffix = ' warmup' if config.is_warmup else ''
        return f"sh {self.create_job_script_name} {config.workflow} {config.get_params_for_create_command()} {config.node} {config.trial}{warmup_suffix}"

    def generate_create_job_script(self, name: str):
        commands = [self.convert_config_to_create_workflow_command(config) for config in
                    self.configs + [self.warmup_config]]

        with open(f"{name}.sh", "w") as file:
            file.writelines("#!/bin/bash/ \n")
            file.writelines("\n".join(commands))

        return self

    def generate_runner(self, experiment_name: str):
        configs = self.configs.copy()
        random.shuffle(configs)
        warmup_config = self.warmup_config
        warmup_config_idx = 0
        configs.insert(warmup_config_idx, warmup_config)

        commands = [
            "#!/bin/bash/ \n",
            f"rm -rf \"{warmup_config.run_dir}\"\n",
        ]

        job_ids = []
        for (job_idx, config) in enumerate(configs):
            job_prev_id = f"job{job_idx - 1}_2"
            job_check_before_id = f"job{job_idx}_0"
            job_id = f"job{job_idx}_1"
            job_check_after_id = f"job{job_idx}_2"

            if job_idx > warmup_config_idx:
                job_ids.append(f"${job_id}")

            commands.append(
                self.__get_slurm_command(job_check_before_id, f"info.before.{config.name}", config.node_name, 1,
                                         COLLECT_INFO_BEFORE_SH,
                                         job_prev_id if job_idx > warmup_config_idx else None))
            commands.append(
                self.__get_slurm_command(job_id, config.name, config.node_name, config.ncores,
                                         f"haddock3 \"{config.name}\"",
                                         job_check_before_id))
            commands.append(
                self.__get_slurm_command(job_check_after_id, f"info.after.{config.name}", config.node_name, 1,
                                         COLLECT_INFO_AFTER_SH,
                                         job_id))

        check_jobs_command = self.__get_check_jobs_command(experiment_name, ",".join(job_ids))

        with open(f"run-{experiment_name}.sh", "w", newline='\n') as file:
            file.write("\n".join(commands))
            file.write(check_jobs_command)

    def __get_slurm_command(self, id: str, name: str, node_name: str, ncores: int, command,
                            dependent_job_id: str = None):
        dependency = f" --dependency=afterany:${dependent_job_id}" if dependent_job_id else ""
        return f"{id}=$(sbatch --job-name=\"{name}\" -w {node_name} -n {ncores}{dependency} {command} | awk '{{print $NF}}')"

    def __get_check_jobs_command(self, experiment_name, job_ids):
        return f'''
cat > check-{experiment_name}.sh << EOF
#!/bin/bash
echo {job_ids}
sacct -o jobid,jobname%50,cluster,Node,state,start,end,ConsumedEnergy,AveRSS,AveDiskRead,AveDiskWrite,AveVMSize,elapsed,NCPUS \
    -j {job_ids} \
    > {experiment_name}-data.txt
cat {experiment_name}-data.txt
EOF
'''


class LocalExperimentGL2(Experiment):
    def get_create_job_script_name(self):
        return "create-local-job.sh"

    def create_configs(self) -> List[Config]:
        return [
            LocalConfig(workflow, "gl2", trial, ncores)
            for workflow in ["dpp", "daa"]
            for ncores in [2, 4, 8]
            for trial in range(1, 11)
        ]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "gl2", 1, 8, True)


class LocalExperimentGL6(Experiment):
    def get_create_job_script_name(self):
        return "create-local-job.sh"

    def create_configs(self) -> List[Config]:
        return [
            LocalConfig(workflow, "gl6", trial, ncores)
            for workflow in ["dpp", "daa"]
            for ncores in [2, 4, 8, 16, 32]
            for trial in range(1, 11)
        ]

    def create_warmup_config(self) -> Config:
        return LocalConfig("dpp", "gl6", 1, 8, True)

# MPIExperimentGL2
# MPIExperimentGL6
# HPCExperiment
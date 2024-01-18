import random
from abc import ABC, abstractmethod
from typing import List

from examples.domain.config.Config import Config
from examples.domain.experiment.PathRegistry import PathRegistry


class Experiment(ABC):
    def __init__(self, base_dir: str = '.'):
        self.base_dir = base_dir
        self.configs = self.create_configs()
        self.warmup_config = self.create_warmup_config()

    @classmethod
    @property
    def ID(cls) -> str:
        return cls.__name__

    @abstractmethod
    def create_configs(self) -> List[Config]:
        pass

    def create_warmup_config(self) -> Config | None:
        '''Override this method if you want to create a warmup config to run before the actual experiment'''
        return None

    @abstractmethod
    def get_ncores(self, config: Config) -> int:
        pass

    def get_experiment_job_dependency(self) -> str | None:
        """Define dependency for the current experiment in order to execute it right after the previous one is
        finished"""
        return None

    def get_command_for_haddock_execution(self, config: 'Config') -> str:
        run_dir = f"{config.run_dir}.info"
        # return f'--wrap="(perf stat -e power/energy-pkg/,power/energy-ram/ haddock3 \'{config.name}\' > {run_dir}/haddock.output.log) > {run_dir}/perf_stat.txt 2>&1"'
        return f'--wrap="(perf stat -e power/energy-pkg/,power/energy-ram/ sleep 10 && echo 10 > {run_dir}/haddock.output.log) > {run_dir}/perf_stat.txt 2>&1"'

    def convert_config_to_create_workflow_command(self, config: Config) -> str:
        warmup_suffix = ' warmup' if config.is_warmup else ''
        return f"sh {PathRegistry.create_job_script()} {config.workflow} {config.get_params_for_create_command()} {config.nodes_for_filename} {config.trial}{warmup_suffix}"

    def generate_create_job_script(self):
        all_configs = self.configs.copy()

        if self.warmup_config:
            all_configs += [self.warmup_config]

        commands = [self.convert_config_to_create_workflow_command(config) for config in all_configs]

        file_name = f"{self.base_dir}/{PathRegistry.create_jobs_script(self.ID)}"
        with open(file_name, "w", newline='\n') as file:
            file.writelines("#!/bin/bash \n")
            file.writelines("\n".join(commands))

        return self

    def generate_commands_for_config(self, config: 'Config', job_idx: int):
        job_prev_id = f"job{job_idx - 1}_2"
        job_check_before_id = f"job{job_idx}_0"
        job_id = f"job{job_idx}_1"
        job_check_after_id = f"job{job_idx}_2"
        first_job_idx = 0

        dependent_job_id = job_prev_id if job_idx > first_job_idx else self.get_experiment_job_dependency()
        return [self.__get_slurm_command(job_check_before_id, f"info.before.{config.name}", config.node_names,
                                         len(config.nodes),
                                         f'{PathRegistry.COLLECT_INFO_BEFORE_SH} "{config.run_dir}"',
                                         dependent_job_id),
                self.__get_slurm_command(job_id, config.name, config.node_names, self.get_ncores(config),
                                         self.get_command_for_haddock_execution(config), job_check_before_id),
                self.__get_slurm_command(job_check_after_id, f"info.after.{config.name}", config.node_names,
                                         len(config.nodes),
                                         f'{PathRegistry.COLLECT_INFO_AFTER_SH} "{config.run_dir}"',
                                         job_id)]

    def generate_runner(self):
        configs = self.configs.copy()
        random.shuffle(configs)

        commands = ["#!/bin/bash \n"]

        warmup_config = self.warmup_config
        warmup_config_idx = -1

        if warmup_config:
            warmup_config_idx = 0
            configs.insert(warmup_config_idx, warmup_config)
            commands.append(f"rm -rf \"{warmup_config.run_dir}\"\n")

        commands += [command for job_idx, config in enumerate(configs) for command in
                     self.generate_commands_for_config(config, job_idx)]

        main_job_ids = ",".join([f"$job{job_idx}_1" for job_idx in range(warmup_config_idx + 1, len(configs))])
        all_job_ids = ",".join([id for job_idx in range(len(configs)) for id in
                                [f"$job{job_idx}_0", f"$job{job_idx}_1", f"$job{job_idx}_2"]])

        file_name = f"{self.base_dir}/{PathRegistry.run_experiment_script(self.ID)}"
        with open(file_name, "w", newline='\n') as file:
            file.write("\n".join(commands))
            file.write(self.__get_check_jobs_command(main_job_ids))
            file.write(self.__get_check_jobs_command(all_job_ids, full=True))

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

    @staticmethod
    def get_sacct_output_format(main_fields_only: bool = False):
        output_format_main_field = "jobid,jobname%60,cluster,Node%24,state,start,end,ConsumedEnergy,AveRSS,AveDiskRead,AveDiskWrite,AveVMSize,SystemCPU,UserCPU,AveCPU,elapsed,NCPUS"
        output_format_secondary_fields = "Account,AdminComment,AllocCPUS,AllocNodes,AllocTRES,AssocID,AveCPUFreq,AvePages,BlockID,Comment,Constraints,ConsumedEnergyRaw,Container,CPUTime,CPUTimeRAW,DBIndex,DerivedExitCode,ElapsedRaw,Eligible,ExitCode,FailedNode,Flags,GID,Group,JobIDRaw,Layout,MaxDiskRead,MaxDiskReadNode,MaxDiskReadTask,MaxDiskWrite,MaxDiskWriteNode,MaxDiskWriteTask,MaxPages,MaxPagesNode,MaxPagesTask,MaxRSS,MaxRSSNode,MaxRSSTask,MaxVMSize,MaxVMSizeNode,MaxVMSizeTask,McsLabel,MinCPU,MinCPUNode,MinCPUTask,NNodes,NodeList,NTasks,Partition,Planned,PlannedCPU,PlannedCPURAW,Priority,QOS,QOSRAW,Reason,ReqCPUFreq,ReqCPUFreqGov,ReqCPUFreqMax,ReqCPUFreqMin,ReqCPUS,ReqMem,ReqNodes,ReqTRES,Reservation,ReservationId,Suspended,SystemComment,Timelimit,TimelimitRaw,TotalCPU,TRESUsageInAve,TRESUsageInMax,TRESUsageInMaxNode,TRESUsageInMaxTask,TRESUsageInMin,TRESUsageInMinNode,TRESUsageInMinTask,TRESUsageInTot,TRESUsageOutAve,TRESUsageOutMax,TRESUsageOutMaxNode,TRESUsageOutMaxTask,TRESUsageOutMin,TRESUsageOutMinNode,TRESUsageOutMinTask,TRESUsageOutTot,UID,User,WCKey,WCKeyID,WorkDir,Submit,SubmitLine"
        return output_format_main_field if main_fields_only else f"{output_format_main_field},{'%100,'.join(output_format_secondary_fields.split(','))}%500"

    def __get_check_jobs_command(self, job_ids, full: bool = False):
        experiment_name = PathRegistry.check_job_script(self.ID, full)
        data_file_name = PathRegistry.experiment_data_filename(self.ID, full)
        return f'''
cat > {experiment_name} << EOF
#!/bin/bash
echo {job_ids}
sacct -o {self.get_sacct_output_format()} \
-j {job_ids} \
> {data_file_name}
cat {data_file_name}
EOF
'''

class PathRegistry:
    HOST_EXPERIMENT_FOLDER = "../examples"
    SHARED_DIR = "/mnt/nfs_share/greenBeansHaddock"

    @staticmethod
    def create_jobs_script(ID: str):
        return f"create-jobs.{ID}.sh"

    @staticmethod
    def create_job_script():
        return "create-job.sh"

    @staticmethod
    def run_experiment_script(ID: str):
        return f"run.{ID}.sh"

    @staticmethod
    def get_full_prefix(full):
        return "full." if full else ""

    @staticmethod
    def check_job_script(ID: str, full: bool = False):
        return f"check.{PathRegistry.get_full_prefix(full)}{ID}.sh"

    @staticmethod
    def experiment_data_filename(ID: str, full: bool = False):
        return f"data.{PathRegistry.get_full_prefix(full)}{ID}.txt"

    @staticmethod
    def script_folder():
        return f"{PathRegistry.HOST_EXPERIMENT_FOLDER}/scripts"

    @staticmethod
    def clean_script():
        return f"{PathRegistry.script_folder()}/clean.sh"

    DATA_ANALYSIS_FOLDER = "."
    EXECUTION_ANALYSIS_SCRIPT_FILENAME = "execution-analysis.py"

    @staticmethod
    def execution_analysis_script():
        return f"{PathRegistry.DATA_ANALYSIS_FOLDER}/run_analysis/{PathRegistry.EXECUTION_ANALYSIS_SCRIPT_FILENAME}"

    COLLECT_INFO_AFTER_SH = "collect-info.after.sh"
    COLLECT_INFO_BEFORE_SH = "collect-info.before.sh"
    COLLECT_HARDWARE_INFO = "measure_hardware.sh"

    @staticmethod
    def info_scripts():
        return [f"{PathRegistry.script_folder()}/{PathRegistry.COLLECT_INFO_AFTER_SH}",
                f"{PathRegistry.script_folder()}/{PathRegistry.COLLECT_INFO_BEFORE_SH}",
                f"{PathRegistry.script_folder()}/{PathRegistry.COLLECT_HARDWARE_INFO}"]

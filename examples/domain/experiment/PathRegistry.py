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
    def check_job_script(ID: str):
        return f"check.{ID}.sh"

    @staticmethod
    def experiment_data_filename(ID: str):
        return f"data.{ID}.txt"

    @staticmethod
    def script_folder():
        return f"{PathRegistry.HOST_EXPERIMENT_FOLDER}/scripts"

    @staticmethod
    def clean_script():
        return f"{PathRegistry.script_folder()}/clean.sh"

    COLLECT_INFO_AFTER_SH = "collect-info.after.sh"
    COLLECT_INFO_BEFORE_SH = "collect-info.before.sh"

    @staticmethod
    def info_scripts():
        return [f"{PathRegistry.script_folder()}/{PathRegistry.COLLECT_INFO_AFTER_SH}",
                f"{PathRegistry.script_folder()}/{PathRegistry.COLLECT_INFO_BEFORE_SH}"]
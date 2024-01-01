class NameRegistry:
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

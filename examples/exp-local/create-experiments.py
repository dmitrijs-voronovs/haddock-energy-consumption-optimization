from examples.domain.experiment.local.LocalExperimentGL2_3 import LocalExperimentGL2_3
from examples.domain.experiment.local.LocalExperimentGL5_2 import LocalExperimentGL5_2
from examples.domain.experiment.local.LocalExperimentGL6_3 import LocalExperimentGL6_3


def main():
    # LocalExperimentGL2().generate_create_job_script("all.create-local-jobs.gl2").generate_runner("local-exp-gl2")
    # LocalExperimentGL6().generate_create_job_script("all.create-local-jobs.gl6").generate_runner("local-exp-gl6")
    # LocalExperimentGL6_2().generate_create_job_script("all.create-local-jobs.gl6_2").generate_runner("local-exp-gl6_2")
    # LocalExperimentGL2_2().generate_create_job_script("all.create-local-jobs.gl2_2").generate_runner("local-exp-gl2_2")
    LocalExperimentGL2_3().generate_create_job_script().generate_runner()
    LocalExperimentGL5_2().generate_create_job_script().generate_runner()
    LocalExperimentGL6_3().generate_create_job_script().generate_runner()

    # LocalExperimentGL5().generate_create_job_script("all.create-local-jobs.gl5").generate_runner("local-exp-gl5")


if __name__ == '__main__':
    main()

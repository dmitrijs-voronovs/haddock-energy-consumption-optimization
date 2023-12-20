from examples.domain import LocalExperimentGL2_3, LocalExperimentGL5_2, LocalExperimentGL6_3


def main():
    # LocalExperimentGL2().generate_create_job_script("all.create-local-jobs.gl2").generate_runner("local-exp-gl2")
    # LocalExperimentGL6().generate_create_job_script("all.create-local-jobs.gl6").generate_runner("local-exp-gl6")
    # LocalExperimentGL6_2().generate_create_job_script("all.create-local-jobs.gl6_2").generate_runner("local-exp-gl6_2")
    # LocalExperimentGL2_2().generate_create_job_script("all.create-local-jobs.gl2_2").generate_runner("local-exp-gl2_2")
    LocalExperimentGL2_3().generate_create_job_script("all.create-local-jobs.gl2_3").generate_runner("local-exp-gl2_3")
    LocalExperimentGL5_2().generate_create_job_script("all.create-local-jobs.gl5_2").generate_runner("local-exp-gl5_2")
    LocalExperimentGL6_3().generate_create_job_script("all.create-local-jobs.gl6_3").generate_runner("local-exp-gl6_3")

    # LocalExperimentGL5().generate_create_job_script("all.create-local-jobs.gl5").generate_runner("local-exp-gl5")


if __name__ == '__main__':
    main()

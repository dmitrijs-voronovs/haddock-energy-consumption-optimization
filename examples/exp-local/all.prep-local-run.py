from examples.domain import LocalExperimentGL2_2, LocalExperimentGL5


def main():
    # LocalExperimentGL2().generate_create_job_script("all.create-local-jobs.gl2").generate_runner("local-exp-gl2")
    # LocalExperimentGL6().generate_create_job_script("all.create-local-jobs.gl6").generate_runner("local-exp-gl6")
    LocalExperimentGL2_2().generate_create_job_script("all.create-local-jobs.gl2_2").generate_runner("local-exp-gl2_2")
    LocalExperimentGL5().generate_create_job_script("all.create-local-jobs.gl5").generate_runner("local-exp-gl5")


if __name__ == '__main__':
    main()

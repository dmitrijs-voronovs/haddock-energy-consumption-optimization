from examples.domain import HPCExperimentTest


def main():
    HPCExperimentTest().generate_create_job_script("all.create-local-jobs.gl2_3").generate_runner("local-exp-gl2_3")


if __name__ == '__main__':
    main()

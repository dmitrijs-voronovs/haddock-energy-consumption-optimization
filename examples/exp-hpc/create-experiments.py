from examples.domain import HPCExperimentTest


def main():
    HPCExperimentTest().generate_create_job_script().generate_runner()


if __name__ == '__main__':
    main()

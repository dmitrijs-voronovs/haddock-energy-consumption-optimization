from examples.domain import LocalExperimentGL2


def main():
    LocalExperimentGL2().generate_create_job_script("all.create-hpc-jobs").generate_runner(
        "exp-hpc")


if __name__ == '__main__':
    main()
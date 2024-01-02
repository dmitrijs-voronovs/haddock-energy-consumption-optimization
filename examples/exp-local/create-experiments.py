from examples.domain.experiment.local.GL2_3 import GL2_3
from examples.domain.experiment.local.GL5_2 import GL5_2
from examples.domain.experiment.local.GL6_3 import GL6_3


def main():
    GL2_3().generate_create_job_script().generate_runner()
    GL5_2().generate_create_job_script().generate_runner()
    GL6_3().generate_create_job_script().generate_runner()


if __name__ == '__main__':
    main()

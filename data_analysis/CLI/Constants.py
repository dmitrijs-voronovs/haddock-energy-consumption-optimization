from enum import Enum

HOST_EXPERIMENT_FOLDER = "../examples"


class ExperimentType(Enum):
    LOCAL = "exp-local"


SHARED_DIR = "/mnt/nfs_share/greenBeansHaddock"


def get_exp_dir(exp: 'ExperimentType'):
    return f"{SHARED_DIR}/{exp.value}"


LOCAL_EXP_DIR = get_exp_dir(ExperimentType.LOCAL)

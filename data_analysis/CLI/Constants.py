from enum import Enum

HOST_EXPERIMENT_FOLDER = "../examples"


class Mode(Enum):
    LOCAL = "local"
    HPC = "hpc"
    MPI = "mpi"


class Workflow(Enum):
    DAA = "daa"
    DPP = "dpp"


class Node(Enum):
    gl2 = "gl2"
    gl4 = "gl4"
    gl5 = "gl5"
    gl6 = "gl6"


class ExperimentFolder(Enum):
    LOCAL = "exp-local"
    HPC = "exp-hpc"
    MPI = "exp-mpi"

    @staticmethod
    def value_to_enum(value):
        try:
            return next(member for member in ExperimentFolder if member.value == value)
        except StopIteration:
            raise ValueError(f"{value} is not a valid value in ExperimentType")


SHARED_DIR = "/mnt/nfs_share/greenBeansHaddock"


def get_abs_remote_exp_dir(exp: 'ExperimentFolder'):
    return f"{SHARED_DIR}/{exp.value}"

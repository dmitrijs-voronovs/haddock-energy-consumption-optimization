from enum import Enum

from examples import PathRegistry


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


SHARED_DIR = PathRegistry.SHARED_DIR
HOST_EXPERIMENT_FOLDER = PathRegistry.HOST_EXPERIMENT_FOLDER


class ExperimentFolder(Enum):
    LOCAL = "exp-local"
    HPC = "exp-hpc"
    MPI = "exp-mpi"

    @staticmethod
    def value_to_enum(value):
        try:
            return next(member for member in ExperimentFolder if member.value == value)
        except StopIteration:
            all_values = [member.value for member in ExperimentFolder]
            raise ValueError(
                f"{value} is not a valid value in ExperimentType, should be one of {all_values}")

    @staticmethod
    def dir(exp: 'ExperimentFolder', *path: str):
        return ExperimentFolder.__get_dir(exp, SHARED_DIR, *path)

    @staticmethod
    def host_dir(exp: 'ExperimentFolder', *path: str):
        return ExperimentFolder.__get_dir(exp, HOST_EXPERIMENT_FOLDER, *path)

    @staticmethod
    def analysis_dir(exp: 'ExperimentFolder', *path: str):
        return ExperimentFolder.__get_dir(exp, ".", *path)

    @staticmethod
    def __get_dir(exp: 'ExperimentFolder', base_dir_path=SHARED_DIR, *path: str):
        if path is None:
            path = []
        return f"{base_dir_path}/{exp.value}/{'/'.join(path)}"

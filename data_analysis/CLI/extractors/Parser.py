import os
from abc import ABC, abstractmethod
from typing import List, Tuple, Callable


class Parser(ABC):
    @staticmethod
    @abstractmethod
    def extract(file_path: str):
        pass


class CombinedParser(Parser, ABC):
    @staticmethod
    @abstractmethod
    def extract_into_file(src: List[Tuple[str, str]], destination_path: str):
        pass


class IndividualParser(Parser, ABC):
    @classmethod
    def extract_into_file(cls, src: List[Tuple[str, str]], get_destination_path: Callable[[Tuple[str, str]], str]):
        for job_name, file in src:
            try:
                df = cls.extract(file)
                dest_path = get_destination_path((job_name, file))
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                df.to_csv(dest_path, index=False)
            except FileNotFoundError as e:
                pass
            except Exception as e:
                print(f"{cls.__name__}: Failed to extract data from file {file}", e)

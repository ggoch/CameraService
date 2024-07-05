from abc import ABC, abstractmethod
import numpy as np

class ModelDetect(ABC):
    @abstractmethod
    def detect(self, image: np.ndarray) -> bool | None:
        pass
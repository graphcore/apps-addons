# Copyright (c) 2023 Graphcore Ltd. All rights reserved.
import abc
from typing import Union, List, Any


class Trainer(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        super().__init__()

    @abc.abstractmethod
    def train(self) -> None:
        pass

    @abc.abstractmethod
    def evaluate(self) -> None:
        pass

    @abc.abstractmethod
    def save_hf_checkpoint(self) -> None:
        pass


class Pipeline(abc.ABC):
    @abc.abstractmethod
    def __init__(
        self,
        config: "ModelConfig",  # Model configuration and hyper parameters
        hf_checkpoint: Union[str, "TransformersModel"],  # Model weights (either string or model)
        *args,
        **kwargs,
    ) -> None:
        """ """
        super().__init__(*args, **kwargs)
        # Download checkpoints and do other preparation steps (but do not compile the model)
        # ...

    @abc.abstractmethod
    def __call__(
        self,
        prompt: Union[str, List[str], "Dataset"],
        *args,
        # Standard arguments which we expect the user to change can also be exposed here
        **kwargs,
    ):
        pass

    @abc.abstractmethod
    def detach(self):
        pass

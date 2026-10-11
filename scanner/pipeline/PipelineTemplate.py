from abc import ABC, abstractmethod


class PipelineTemplate(ABC):

    @abstractmethod
    def extract() -> None:
        pass

    @abstractmethod
    def transform() -> None:
        pass

    @abstractmethod
    def load() -> None:
        pass

    def run(self):
        self.extract()
        self.transform()
        self.load()
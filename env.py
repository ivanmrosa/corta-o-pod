import os
import sys
from typing import TextIO


baseDir = os.path.dirname(__file__)


class Env:
    def __init__(self) -> None:
        with open(os.path.join(baseDir, '.env')) as f:
            lines = f.read().split('\n')
            for line in lines:
                keyValue = line.split("=")
                self.__setattr__(keyValue[0], keyValue[1])

    def getEnvValue(self, name: str) -> str:
        return self.__getattribute__(name)

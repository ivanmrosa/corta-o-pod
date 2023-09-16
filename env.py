import os, sys
from  typing import TextIO


baseDir = os.path.dirname(__file__)
class Env:    
    __File : TextIO
    def __init__(self) -> None:
        if not self.__File:
            with open(os.path.join(baseDir, '.env')) as f:
                lines = f.readlines()
                for line in lines:
                    keyValue = line.split("=")
                    self.__setattr__(keyValue[0], keyValue[1])
    
    def getEnvValue(self, name: str) -> str:
        return self.__getattribute__(name)
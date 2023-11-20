import os
import shutil
import sys
from typing import TextIO


baseDir = os.path.dirname(__file__)


class Env:
    def __init__(self) -> None:
        self.loadAttributes()

    def loadAttributes(self):
        if not os.path.exists(os.path.join(baseDir, '.env')):
            shutil.copy(os.path.join(baseDir, '.env_example'), 
                        os.path.join(baseDir, '.env'))
        with open(os.path.join(baseDir, '.env')) as f:
            lines = f.read().split('\n')
            for line in lines:
                keyValue = line.split("=")
                if len(keyValue) > 1:
                    paramName = keyValue.pop(0)
                    self.__setattr__(paramName, "=".join(keyValue))
    
    def getEnvValue(self, name: str) -> str:
        return self.__getattribute__(name)
    
    def getEnvPath(self):
        return os.path.join(baseDir, '.env')
    
    def getKeyValueAttributes(self):
        return self.__dict__
    
    def saveConfig(self, config: dict) -> None:
        with open(os.path.join(baseDir, '.env'), 'w') as f:
            f.truncate()
            for key, value in config.items():
                f.write(f'{key}={value}\n')
        
        self.loadAttributes()
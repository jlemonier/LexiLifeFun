from lexi import Lexi

import enum

class Settings(enum.Enum):
    ByGroup = 1
    ByLight = 2

class LexiInfo(Lexi):
    
    def lights(self, ):
        """ List lights by Group """
        # self.registeredByType
        pass
    
    

from .instructions import INSTRUCTIONS

from src.models import Fields

class SystemInstructions:
    "The system instructions in the prompt to the model"
    def __init__(self):
        self.instructions = ""

    def get_instructions(self):
        return self.instructions

class SystemInstructionsBuilder:
    "Builds the system instructions buy adding to its string representation"
    def __init__(self, instructions_obj=None):
        self.instructions_obj = instructions_obj or SystemInstructions()
    
    def add_instructions(self, target_info:str|Fields):
        "Creates instructions based on the given enum target info"
        if isinstance(target_info, Fields):
            target_info = target_info.value
        self.instructions_obj.instructions = INSTRUCTIONS[target_info]
        return self
    
    def get_obj(self):
        return self.instructions_obj
        
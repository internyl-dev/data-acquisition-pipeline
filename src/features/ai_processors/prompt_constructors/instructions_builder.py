
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

    def legacy_add_instructions(self, target_info:str):
        "Creates instructions based on the given string target info"
        self.instructions_obj.instructions = INSTRUCTIONS[target_info]
        return self
    
    def add_instructions(self, target_info:Fields):
        "Creates instructions based on the given enum target info"
        self.instructions_obj.instructions = INSTRUCTIONS[target_info.value]
    
    def get_obj(self):
        return self.instructions_obj
        
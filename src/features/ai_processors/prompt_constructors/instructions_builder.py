
from .instructions import INSTRUCTIONS

class SystemInstructions:
    def __init__(self):
        self.instructions = ""

    def get_instructions(self):
        return self.instructions

class SystemInstructionsBuilder:
    def __init__(self, instructions_obj=None):
        self.instructions_obj = instructions_obj or SystemInstructions()

    def add_instructions(self, required_info):
        self.instructions_obj.instructions = INSTRUCTIONS[required_info]
        return self
    
    def get_obj(self):
        return self.instructions_obj
        
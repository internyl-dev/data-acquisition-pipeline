
from typing import Literal
from pydantic import BaseModel, ConfigDict

# Type aliases
OptionalBool = bool | Literal["not provided"]
OptionalInt = int | Literal["not provided"]
OptionalFloat = float | Literal["not provided"]

class BaseModelConfig(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

#==========#
# OVERVIEW #
#==========#
class Overview(BaseModelConfig):
    title: str = "not provided"
    provider: str = "not provided"
    description: str = "not provided"
    link: None = None
    subject: list[str] = ["not provided"]
    tags: list[str] = ["not provided"]

#=============#
# ELIGIBILITY #
#=============#
class Requirements(BaseModelConfig):
    essay_required: OptionalBool = "not provided"
    recommendation_required: OptionalBool = "not provided"
    transcript_required: OptionalBool = "not provided"
    other: list[str] = ["not provided"]

class Age(BaseModelConfig):
    minimum: OptionalInt = "not provided"
    maximum: OptionalInt = "not provided"

class Grades(BaseModelConfig):
    grades: list[str] = ["not provided"]
    age: Age = Age()

class Eligibility(BaseModelConfig):
    requirements: Requirements = Requirements()
    eligibility: Grades = Grades()

#=======#
# DATES #
#=======#
class Deadline(BaseModelConfig):
    name: str = "not provided"
    priority: str = "not provided"
    term: str = "not provided"
    date: str = "not provided"
    rolling_basis: OptionalBool = "not provided"
    time: str = "not provided"

class Date(BaseModelConfig):
    term: str = "not provided"
    start: str = "not provided"
    end: str = "not provided"

class Dates(BaseModelConfig):
    deadlines: list[Deadline] = [Deadline()]
    dates: list[Date] = [Date()]
    duration_weeks: OptionalInt = "not provided"

#===========#
# LOCATIONS #
#===========#
class Location(BaseModelConfig):
    virtual: OptionalBool = "not provided"
    state: str = "not provided"
    city: str = "not provided"
    address: str = "not provided"

class Locations(BaseModelConfig):
    locations: list[Location] = [Location()]

#=======#
# COSTS #
#=======#
class Cost(BaseModelConfig):
    name: str = "not provided"
    free: OptionalBool = "not provided"
    lowest: OptionalFloat = "not provided"
    highest: OptionalFloat = "not provided"
    financial_aid_available: OptionalBool = "not provided"

class Stipend(BaseModelConfig):
    available: OptionalBool = "not provided"
    amount: float | str = "not provided"

class Costs(BaseModelConfig):
    costs: list[Cost] = "not provided"
    stipend: Stipend = Stipend()

#=========#
# CONTACT #
#=========#
class ContactOptions(BaseModelConfig):
    email: str = "not provided"
    phone: str = "not provided"

class Contact(BaseModelConfig):
    contact: ContactOptions = ContactOptions()

#=============#
# ROOT SCHEMA #
#=============#
class RootSchema(BaseModelConfig):
    overview: Overview = Overview()
    eligibility: Eligibility = Eligibility()
    dates: Dates = Dates()
    locations: Locations = Locations()
    costs: Costs = Costs()
    contact: Contact = Contact()

class SchemaModelFactory:
    @staticmethod
    def make_overview():
        return Overview
    
    @staticmethod
    def make_eligibility():
        return Eligibility
    
    @staticmethod
    def make_dates():
        return Dates
    
    @staticmethod
    def make_locations():
        return Locations
    
    @staticmethod
    def make_costs():
        return Costs

    @staticmethod
    def make_contact():
        return Contact
    
    def make(self, s:str):
        sections = {
            "overview": self.make_overview,
            "eligibility": self.make_eligibility,
            "dates": self.make_dates,
            "locations": self.make_locations,
            "costs": self.make_costs,
            "contact": self.make_contact,
        }

        return sections[s]() if s != "all" else RootSchema
    
if __name__ == "__main__":

    root_schema = RootSchema()
    root_schema.overview.title = "fffff"
    print(root_schema.overview.title)
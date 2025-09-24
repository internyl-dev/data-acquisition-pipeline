
from typing import Literal
from pydantic import BaseModel, ConfigDict
from abc import ABC

from .schema_fields import Fields

# Type aliases
OptionalBool = bool | Literal["not provided"]
OptionalInt = int | Literal["not provided"]
OptionalFloat = float | Literal["not provided"]

class BaseModelConfig(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

class BaseSchemaSection(BaseModelConfig, ABC):
    pass

#==========#
# OVERVIEW #
#==========#
class Overview(BaseSchemaSection):
    title: str = "not provided"
    provider: str = "not provided"
    description: str = "not provided"
    link: str = None
    favicon: str = "not provided"
    subject: list[str] = ["not provided"]
    tags: list[str] = ["not provided"]

#=============#
# ELIGIBILITY #
#=============#
class Requirements(BaseSchemaSection):
    essay_required: OptionalBool = "not provided"
    recommendation_required: OptionalBool = "not provided"
    transcript_required: OptionalBool = "not provided"
    other: list[str] = ["not provided"]

class Age(BaseSchemaSection):
    minimum: OptionalInt = "not provided"
    maximum: OptionalInt = "not provided"

class Grades(BaseSchemaSection):
    grades: list[str] = ["not provided"]
    age: Age = Age()

class Eligibility(BaseSchemaSection):
    requirements: Requirements = Requirements()
    eligibility: Grades = Grades()

#=======#
# DATES #
#=======#
class Deadline(BaseSchemaSection):
    name: str = "not provided"
    priority: str = "not provided"
    term: str = "not provided"
    date: str = "not provided"
    rolling_basis: OptionalBool = "not provided"
    time: str = "not provided"

class Date(BaseSchemaSection):
    term: str = "not provided"
    start: str = "not provided"
    end: str = "not provided"

class Dates(BaseSchemaSection):
    deadlines: list[Deadline] = [Deadline()]
    dates: list[Date] = [Date()]
    duration_weeks: OptionalInt = "not provided"

#===========#
# LOCATIONS #
#===========#
class Location(BaseSchemaSection):
    virtual: OptionalBool = "not provided"
    state: str = "not provided"
    city: str = "not provided"
    address: str = "not provided"

class Locations(BaseSchemaSection):
    locations: list[Location] = [Location()]

#=======#
# COSTS #
#=======#
class Cost(BaseSchemaSection):
    name: str = "not provided"
    free: OptionalBool = "not provided"
    lowest: OptionalFloat = "not provided"
    highest: OptionalFloat = "not provided"
    financial_aid_available: OptionalBool = "not provided"

class Stipend(BaseSchemaSection):
    available: OptionalBool = "not provided"
    amount: float | str = "not provided"

class Costs(BaseSchemaSection):
    costs: list[Cost] = [Cost()]
    stipend: Stipend = Stipend()

#=========#
# CONTACT #
#=========#
class ContactOptions(BaseSchemaSection):
    email: str = "not provided"
    phone: str = "not provided"

class Contact(BaseSchemaSection):
    contact: ContactOptions = ContactOptions()

#=============#
# ROOT SCHEMA #
#=============#
class RootSchema(BaseSchemaSection):
    overview: Overview = Overview()
    eligibility: Eligibility = Eligibility()
    dates: Dates = Dates()
    locations: Locations = Locations()
    costs: Costs = Costs()
    contact: Contact = Contact()

    def get(self, section):
        if section == Fields.OVERVIEW:
            return self.overview
        if section == Fields.ELIGIBILITY:
            return self.eligibility
        if section == Fields.DATES:
            return self.dates
        if section == Fields.COSTS:
            return self.costs
        if section == Fields.CONTACT:
            return self.contact

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
    
    def make(self, s:str|Fields):
        if isinstance(s, Fields):
            s = s.value
            
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

    print(isinstance(RootSchema().overview, BaseSchemaSection))

from typing import Literal
from pydantic import BaseModel, HttpUrl

# Type aliases
OptionalBool = bool | Literal["not provided"]
OptionalInt = int | Literal["not provided"]
OptionalFloat = float | Literal["not provided"]

#==========#
# OVERVIEW #
#==========#
class Overview(BaseModel):
    title: str
    provider: str
    description: str
    link: None
    subject: list[str]
    tags: list[str]

#=============#
# ELIGIBILITY #
#=============#
class Requirements(BaseModel):
    essay_required: OptionalBool
    recommendation_required: OptionalBool
    transcript_required: OptionalBool
    other: list[str]

class Age(BaseModel):
    minimum: OptionalInt
    maximum: OptionalInt

class Grades(BaseModel):
    grades: list[str]
    age: Age

class Eligibility(BaseModel):
    requirements: Requirements
    eligibility: Grades

#=======#
# DATES #
#=======#
class Deadline(BaseModel):
    name: str
    priority: str
    term: str
    date: str
    rolling_basis: OptionalBool

class Date(BaseModel):
    term: str
    start: str
    end: str

class Dates(BaseModel):
    deadlines: list[Deadline]
    dates: list[Date]
    duration_weeks: OptionalInt

#===========#
# LOCATIONS #
#===========#
class Location(BaseModel):
    virtual: OptionalBool
    state: str
    city: str
    address: str

class Locations(BaseModel):
    locations: list[Location]

#=======#
# COSTS #
#=======#
class Cost(BaseModel):
    name: str
    free: OptionalBool
    lowest: OptionalFloat
    highest: OptionalFloat
    financial_aid_available: OptionalBool

class Stipend(BaseModel):
    available: OptionalBool
    amount: float | str

class Costs(BaseModel):
    costs: list[Cost]
    stipend: Stipend

#=========#
# CONTACT #
#=========#
class ContactOptions(BaseModel):
    email: str
    phone: str

class Contact(BaseModel):
    contact: ContactOptions

#=============#
# ROOT SCHEMA #
#=============#
class RootSchema(BaseModel):
    overview: Overview
    eligibility: Eligibility
    dates: Dates
    locations: Locations
    costs: Costs
    contact: Contact

class ResponseModelFactory:
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
            "overview": self.make_overview(),
            "eligibility": self.make_eligibility(),
            "dates": self.make_dates(),
            "locations": self.make_locations(),
            "costs": self.make_costs(),
            "contact": self.make_contact(),
            "all": RootSchema
        }

        return sections[s]
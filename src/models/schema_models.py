
from typing import Literal, Optional, Union, Self
from pydantic import BaseModel, ConfigDict
from abc import ABC

from .schema_fields import Fields

# Type aliases
OptionalBool = bool | Literal["not provided"]
OptionalInt = int | Literal["not provided"]
OptionalFloat = float | Literal["not provided"] | None

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
    link: str = "not provided"
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
    virtual: OptionalBool | Literal["both available"] = "not provided"
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
    amount: Optional[Union[float, str]] = "not provided"

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

#==========#
# METADATA #
#==========#
class Metadata(BaseSchemaSection):
    date_added: str = ""
    time_added: str = ""
    favicon: str = ""
    total_input_tokens: int = 0
    total_output_tokens: int = 0

    def get_total_tokens(self) -> int:
        return self.total_input_tokens + self.total_output_tokens

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
    metadata: Metadata = Metadata()

    def get(self, section: Fields | str):
        if isinstance(section, str):
            section = Fields[section.upper()]
        match section:
            case Fields.OVERVIEW:
                return self.overview
            case Fields.ELIGIBILITY:
                return self.eligibility
            case Fields.DATES:
                return self.dates
            case Fields.LOCATIONS:
                return self.locations
            case Fields.COSTS:
                return self.costs
            case Fields.CONTACT:
                return self.contact
            case Fields.METADATA:
                return self.metadata

    def clear(self) -> Self:
        raise NotImplementedError("`clear` method has not been implemented for `RootSchema`")

class SchemaModelFactory:
    "Returns the the class representation of a section of the schema"
    @staticmethod
    def make_overview() -> type[Overview]:
        "Returns the Overview class"
        return Overview
    
    @staticmethod
    def make_eligibility() -> type[Eligibility]:
        "Returns the Eligibility class"
        return Eligibility
    
    @staticmethod
    def make_dates() -> type[Dates]:
        "Returns the Dates class"
        return Dates
    
    @staticmethod
    def make_locations() -> type[Locations]:
        "Returns the Locations class"
        return Locations
    
    @staticmethod
    def make_costs() -> type[Costs]:
        "Returns the Costs class"
        return Costs

    @staticmethod
    def make_contact() -> type[Contact]:
        "Returns the Contact class"
        return Contact

    @staticmethod
    def make_metadata() -> type[Metadata]:
        "Returns the Metadata class"
        return Metadata
    
    @staticmethod 
    def make_root() -> type[RootSchema]:
        "Returns the RootSchema class"
        return RootSchema
    
    def make(self, s:str|Fields):
        "Returns the specified class based on the given string"
        if isinstance(s, Fields):
            s = s.value

        sections = {
            "overview": self.make_overview,
            "eligibility": self.make_eligibility,
            "dates": self.make_dates,
            "locations": self.make_locations,
            "costs": self.make_costs,
            "contact": self.make_contact,
            "metadata": self.make_metadata,
            "all": self.make_root
        }

        return sections[s]()
    
if __name__ == "__main__":

    root_schema = RootSchema()
    root_schema.overview.title = "fffff"
    print(root_schema.overview.title)

    print(isinstance(RootSchema().overview, BaseSchemaSection))
    print(root_schema.model_dump())
    print(root_schema.get("overview"))

from .state_abbrev import STATE_ABBREVIATIONS
from .base_schema_cleaner import SchemaCleaner
from src.models.schema_models import Overview, \
                       Eligibility, \
                       Dates, \
                       Locations, \
                       Costs, \
                       Contact

class OverviewCleaner(SchemaCleaner):
    @staticmethod
    def _fix_no_subjects_dict(section: dict) -> None:
        # If no subjects were found but for some reason
        # the model didn't include "Various"
        if not section["subject"]:
            section["subject"] = ["Various"]

    @staticmethod
    def _fix_no_subjects_obj(section: Overview) -> None:
        if not section.subject:
            section.subject = ["Various"]

    def clean(self, section: dict | Overview) -> None:
        if isinstance(section, dict):
            self._fix_no_subjects_dict(section)
        else:
            self._fix_no_subjects_obj(section)



class EligibilityCleaner(SchemaCleaner):
    def clean(self, section: dict | Eligibility) -> None:
        pass



class DatesCleaner(SchemaCleaner):
    def clean(self, section: dict | Dates) -> None:
        pass



class LocationsCleaner(SchemaCleaner):
    @staticmethod
    def _fix_state_abbrevs_dict(section: dict) -> None:
        for location in section["locations"]:
            for abbr, full in STATE_ABBREVIATIONS.items():
                location["state"] = location["state"].replace(abbr, full)

    @staticmethod
    def _fix_state_abbrevs_obj(section: Locations) -> None:
        for location in section.locations:
            for abbr, full in STATE_ABBREVIATIONS.items():
                location.state = location.state.replace(abbr, full)

    def clean(self, section: dict | Locations) -> None:
        if isinstance(section, dict):
            self._fix_state_abbrevs_dict(section)
        else:
            self._fix_state_abbrevs_obj(section)



class CostsCleaner(SchemaCleaner):
    @staticmethod
    def _fix_free_dict(section: dict) -> None:
        for cost in section["costs"]:
            if not cost:
                return
            if cost["lowest"] == 0 and cost["highest"] == 0:
                cost["lowest"] = None
                cost["highest"] = None
                cost["free"] = True

    @staticmethod
    def _fix_not_free_dict(section: dict) -> None:
        for cost in section["costs"]:
            if any(isinstance(x, (float, int)) for x in (cost["lowest"], cost["highest"])):
                cost["free"] = False

    @staticmethod
    def _fix_null_stipend_dict(section: dict) -> None:
        stipend = section["stipend"]
        if stipend["available"] is True and stipend["amount"] is None:
            stipend["amount"] = "not provided"

    # Same logic for object model
    @staticmethod
    def _fix_free_obj(section: Costs) -> None:
        for cost in section.costs:
            if not cost:
                return
            if cost.lowest == 0 and cost.highest == 0:
                cost.lowest = None
                cost.highest = None
                cost.free = True

    @staticmethod
    def _fix_not_free_obj(section: Costs) -> None:
        for cost in section.costs:
            if any(isinstance(x, (float, int)) for x in (cost.lowest, cost.highest)):
                cost.free = False

    @staticmethod
    def _fix_null_stipend_obj(section: Costs) -> None:
        if section.stipend.available is True and section.stipend.amount is None:
            section.stipend.amount = "not provided"

    def clean(self, section: dict | Costs) -> None:
        if isinstance(section, dict):
            self._fix_free_dict(section)
            self._fix_not_free_dict(section)
            self._fix_null_stipend_dict(section)
        else:
            self._fix_free_obj(section)
            self._fix_not_free_obj(section)
            self._fix_null_stipend_obj(section)



class ContactCleaner(SchemaCleaner):
    def clean(self, section: dict | Contact) -> None:
        pass

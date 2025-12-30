
import unittest

from src.models import SchemaModelFactory, RootSchema, Fields
from src.models.schema_models import Overview, \
                                     Eligibility, \
                                     Dates, \
                                     Locations, \
                                     Costs, \
                                     Contact, \
                                     Metadata

class TestSchemaFactoryStaticMethods(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = SchemaModelFactory()

    def test_make_overview(self):
        model = self.factory.make_overview()

        self.assertIs(model, Overview)

    def test_make_eligibility(self):
        model = self.factory.make_eligibility()
        
        self.assertIs(model, Eligibility)

    def test_make_dates(self):
        model = self.factory.make_dates()

        self.assertIs(model, Dates)

    def test_make_locations(self):
        model = self.factory.make_locations()

        self.assertIs(model, Locations)

    def test_make_costs(self):
        model = self.factory.make_costs()
        
        self.assertIs(model, Costs)

    def test_make_contact(self):
        model = self.factory.make_contact()

        self.assertIs(model, Contact)

    def test_make_metadata(self):
        model = self.factory.make_metadata()

        self.assertIs(model, Metadata)

    def test_make_root(self):
        model = self.factory.make_root()
        
        self.assertIs(model, RootSchema)

class TestSchemaFactoryMakeField(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = SchemaModelFactory()

    def test_make_overview(self):
        model = self.factory.make(Fields.OVERVIEW)

        self.assertIs(model, Overview)

    def test_make_eligibility(self):
        model = self.factory.make(Fields.ELIGIBILITY)
        
        self.assertIs(model, Eligibility)

    def test_make_dates(self):
        model = self.factory.make(Fields.DATES)

        self.assertIs(model, Dates)

    def test_make_locations(self):
        model = self.factory.make(Fields.LOCATIONS)

        self.assertIs(model, Locations)

    def test_make_costs(self):
        model = self.factory.make(Fields.COSTS)
        
        self.assertIs(model, Costs)

    def test_make_contact(self):
        model = self.factory.make(Fields.CONTACT)

        self.assertIs(model, Contact)

    def test_make_metadata(self):
        model = self.factory.make(Fields.METADATA)

        self.assertIs(model, Metadata)

    def test_make_root(self):
        model = self.factory.make(Fields.ALL)
        
        self.assertIs(model, RootSchema)

class TestSchemaFactoryMakeString(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = SchemaModelFactory()

    def test_make_overview(self):
        model = self.factory.make("overview")

        self.assertIs(model, Overview)

    def test_make_eligibility(self):
        model = self.factory.make("eligibility")
        
        self.assertIs(model, Eligibility)

    def test_make_dates(self):
        model = self.factory.make("dates")

        self.assertIs(model, Dates)

    def test_make_locations(self):
        model = self.factory.make("locations")

        self.assertIs(model, Locations)

    def test_make_costs(self):
        model = self.factory.make("costs")
        
        self.assertIs(model, Costs)

    def test_make_contact(self):
        model = self.factory.make("contact")

        self.assertIs(model, Contact)

    def test_make_metadata(self):
        model = self.factory.make("metadata")

        self.assertIs(model, Metadata)

    def test_make_root(self):
        model = self.factory.make("all")
        
        self.assertIs(model, RootSchema)

class TestSchemaFactoryExceptions(unittest.TestCase):
    def setUp(self):
        self.factory = SchemaModelFactory()

    def test_make_empty_str(self):
        with self.assertRaises(ValueError):
            self.factory.make("")

    def test_make_invalid_str(self):
        with self.assertRaises(ValueError):
            self.factory.make("IDoNotExist")

unittest.main()
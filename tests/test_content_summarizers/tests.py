
import unittest
import re

from src.features.content_summarizers import ContentTrimmer, EmailExtractor, DateExtractor, PhoneNumberExtractor

class TestHTMLCleaners(unittest.TestCase):
    def setUp(self):
        self.trimmer = ContentTrimmer()

    def test_pluralize(self):
        plural_test_cases = {
            "intern": "interns",
            "city": "cities",
            "batch": "batches",
            "wish": "wishes",
            "kiss": "kisses",
            "essay": "essays",
            "person": "people"
        }

        for case in plural_test_cases:
            pattern = re.compile(self.trimmer._pluralize(case))
            self.assertIsNotNone(
                pattern.search(case),
                msg=f"Failed to match singular: {case} with pattern {pattern.pattern}"
            )
            self.assertIsNotNone(
                pattern.search(plural_test_cases[case]),
                msg=f"Failed to match plural: {plural_test_cases[case]} with pattern {pattern.pattern}"
            )

    def test_plural_matching(self):
        pattern = re.compile(rf'\b(intern|interns)\b')
        matching_test_cases = {
            "Become an intern at X": True,
            "Become an intern, X": True,
            "Become one, (intern)": True,
            "Become anintern at X": False,
            "Become an internat X": False,
            "Become aninternat X": False,
            "Become interns at X": True,
            "Become interns, X": True,
            "Become one, (interns)": True,
            "Becomeinterns at X": False,
            "Become internsat X": False,
            "Becomeinternsat X": False
        }

        for case in matching_test_cases:
            matched = pattern.search(case) is not None
            self.assertEqual(
                matched, matching_test_cases[case],
                msg=f"Fail: matched {matched} in {case}"
            )

    def test_capital_matching(self):
        pattern = re.compile(rf'\b(intern|interns)\b', re.I)
        capital_test_cases = {
            "Become an Intern at X": True,
            "Become an Intern, X": True,
            "Become one, (Intern)": True,
            "Become anIntern at X": False,
            "Become an Internat X": False,
            "Become anInternat X": False,
            "Become Interns at X": True,
            "Become Interns, X": True,
            "Become one, (Interns)": True,
            "BecomeInterns at X": False,
            "Become Internsat X": False,
            "BecomeInternsat X": False
        }

        for case in capital_test_cases:
            matched = pattern.search(case) is not None
            self.assertEqual(
                matched, capital_test_cases[case],
                msg=f"Fail: matched {matched} in {case}"
            )

    def test_all_caps_matching(self):
        pattern = re.compile(rf'\b(intern|interns)\b', re.I)
        all_caps_test_cases = {
            "Become an INTERN at X": True,
            "Become an INTERN, X": True,
            "Become one, (INTERN)": True,
            "Become anINTERN at X": False,
            "Become an INTERNat X": False,
            "Become anINTERNat X": False,
            "Become INTERNS at X": True,
            "Become INTERNS, X": True,
            "Become one, (INTERNS)": True,
            "BecomeINTERNS at X": False,
            "Become INTERNSat X": False,
            "BecomeINTERNSat X": False 
        }

        for case in all_caps_test_cases:
            matched = pattern.search(case) is not None
            self.assertEqual(
                matched, all_caps_test_cases[case],
                msg=f"Fail: matched {matched} in {case}"
            )

    def test_truncont_detection(self):
        keywords = ["keyword", "buzzword"]

        cases = [
            [["Sample", "control", "group"], 0, 
             []],

            [["Test", "keyword", "found"], 0, 
             ["keyword"]],

            [["Test", "buzzword", "found"], 0,
             ["buzzword"]]
        ]

        for case in cases:
            self.assertEqual(
                self.trimmer._truncont('\n'.join(case[0]), keywords, case[1]), '\n'.join(case[2])
            )

    def test_truncont_area(self):
        keywords = ["keyword", "buzzword"]

        cases = [
            [["ignored", "Area", "keyword", "one", "ignored"], 1, 
             ["Area", "keyword", "one"]],
             
            [["ignored", "Test", "area", "keyword", "two", "works", "ignored"], 2, 
             ["Test", "area", "keyword", "two", "works"]],

            [["ignored", "Multiple", "keyword", "keyword", "works", "ignored"], 1,
             ["Mutliple", "keyword", "keyword", "works"]],
        ]

        for case in cases:
            self.assertEqual(
                self.trimmer._truncont('\n'.join(case[0]), keywords, case[1]), '\n'.join(case[2])
            )

    def test_truncont_keywords(self):
        keywords = ["keyword", "buzzword"]

        cases = [
            [["Test", "keyword", "buzzword", "found"], 0,
             ["keyword", "buzzword"]],

            [["keyword", "edge", "ignored"], 1,
             ["keyword", "edge"]],
            
            [["ignored", "edge", "keyword"], 1,
             ["edge", "keyword"]]
        ]

        for case in cases:
            self.assertEqual(
                self.trimmer._truncont('\n'.join(case[0]), keywords, case[1]), '\n'.join(case[2])
            )

unittest.main()
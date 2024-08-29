import pytest
from django.db.models import Q
from goats_tom.tests.factories import DRAGONSFileFactory
from goats_tom.filters import AstrodataFilter
from goats_tom.models import DRAGONSFile
from django.test import TestCase
from datetime import datetime

class TestAstrodataFilter(TestCase):
    def setUp(self):
        self.astrodata_filter = AstrodataFilter()
    
    def test_greater_than_central_wavelength(self):
        # Create specific file for this test
        DRAGONSFileFactory.create(astrodata_descriptors={
            "central_wavelength": 1500,
            "exposure_time": 100,
            "ut_date": "2023-08-01"
        })
        DRAGONSFileFactory.create(astrodata_descriptors={
            "central_wavelength": 900,
            "exposure_time": 200,
            "ut_date": "2023-07-01"
        })

        filter_expression = 'central_wavelength>1000'
        query_filter = self.astrodata_filter.parse_expression_to_query(filter_expression)

        queryset = DRAGONSFile.objects.filter(query_filter)
        self.assertEqual(queryset.count(), 1)

    def test_exact_match_filter_name(self):
        # Create files with specific descriptors
        DRAGONSFileFactory.create(astrodata_descriptors={"filter_name": "Blue"})
        DRAGONSFileFactory.create(astrodata_descriptors={"filter_name": "Red"})

        filter_expression = 'filter_name=="Blue"'
        query_filter = self.astrodata_filter.parse_expression_to_query(filter_expression)

        queryset = DRAGONSFile.objects.filter(query_filter)
        self.assertEqual(queryset.count(), 1)

    def test_date_range_filter(self):
        # Create files with dates
        DRAGONSFileFactory.create(astrodata_descriptors={"ut_date": "2023-08-01"})
        DRAGONSFileFactory.create(astrodata_descriptors={"ut_date": "2023-08-15"})

        filter_expression = 'ut_date>="2023-08-01" AND ut_date<="2023-08-10"'
        query_filter = self.astrodata_filter.parse_expression_to_query(filter_expression)

        queryset = DRAGONSFile.objects.filter(query_filter)
        self.assertEqual(queryset.count(), 1)

    def test__parse_datetime(self):
        test_cases = [
            ("ut_time", "12:34:56.789", "12:34:56.789000"),
            ("ut_time", "12:34:56", "12:34:56"),
            ("local_time", "23:59:59.999", "23:59:59.999000"),
            ("local_time", "23:59:59", "23:59:59"),
            ("ut_date", "2023-01-01", "2023-01-01"),
            ("ut_datetime", "2023-01-01 12:34:56.789", "2023-01-01T12:34:56.789000"),
            ("ut_datetime", "2023-01-01T12:34:56.789", "2023-01-01T12:34:56.789000"),
            ("ut_datetime", "2023-01-01 12:34:56", "2023-01-01T12:34:56"),
            ("ut_datetime", "2023-01-01T12:34:56", "2023-01-01T12:34:56"),
            ("ut_datetime", "incorrect-format", None)
        ]

        for field, value, expected in test_cases:
            with self.subTest(field=field, value=value):
                result = self.astrodata_filter._parse_datetime(value, field)
                self.assertEqual(result, expected, f"Failed for field {field} with value {value}")

    def test__normalize_value(self):
        # Test cases should have a proper field specified to check normalization.
        test_cases = [
            ("test", "1.0", 1.0),  # General field with float in string form.
            ("ut_date", "2023-01-01", datetime.strptime("2023-01-01", "%Y-%m-%d").date().isoformat()),  # Date field with ISO date string.
            ("test", "\"true\"", True),  # String explicitly quoted boolean true.
            ("test", "false", False),  # Boolean false in plain string.
            ("test", "\"null\"", None),  # String explicitly quoted null.
            ("test", "None", None)  # String None treated as null.
        ]

        for field, input_value, expected_output in test_cases:
            with self.subTest(field=field, input_value=input_value):
                normalized = self.astrodata_filter._normalize_value(input_value, field)
                self.assertEqual(normalized, expected_output, f"Failed for field '{field}' with value '{input_value}'")
                
    def test__apply_logical_operations(self):
        # Define test cases for different logical operations and expected outcomes.
        test_cases = [
            ("AND", Q(name="test"), Q(value=123), (Q(name="test") & Q(value=123)).children),
            ("OR", Q(name="test"), Q(value=123), (Q(name="test") | Q(value=123)).children),
            ("NOT", Q(name="test"), Q(value=123), (Q(name="test") & ~Q(value=123)).children),
        ]

        for operation, q1, q2, expected_children in test_cases:
            with self.subTest(operation=operation):
                result = self.astrodata_filter._apply_logical_operation(q1, q2, operation)
                self.assertEqual(result.children, expected_children)
                
    def test__build_descriptor_key(self):
        # Define test cases including typical, empty, and special characters
        test_cases = [
            ("central_wavelength", "__exact", "astrodata_descriptors__central_wavelength__exact"),
            ("exposure_time", "__lt", "astrodata_descriptors__exposure_time__lt"),
        ]

        for field, operator, expected_key in test_cases:
            with self.subTest(field=field, operator=operator):
                result_key = self.astrodata_filter._build_descriptor_key(field, operator)
                self.assertEqual(result_key, expected_key, f"Failed for field '{field}' with operator '{operator}'")
                
    def test__handle_numeric_tolerance(self):
        test_cases = [
            ("central_wavelength", 2.166e-06, 2.1659783400000003e-06, 2.16602166e-06),
            ("exposure_time", 100.0, 99.0, 101.0),
        ]

        for field, value, expected_lower, expected_upper in test_cases:
            with self.subTest(field=field, value=value):
                result = self.astrodata_filter._handle_numeric_tolerance(field, value)
                print(result)
                # Extract conditions from Q object to compare values accurately
                conditions = {child[0]: child[1] for child in result.children}
                self.assertAlmostEqual(conditions[self.astrodata_filter._build_descriptor_key(field, "__gte")], expected_lower, places=5,
                                       msg=f"Lower bound mismatch for field '{field}'")
                self.assertAlmostEqual(conditions[self.astrodata_filter._build_descriptor_key(field, "__lte")], expected_upper, places=5,
                                       msg=f"Upper bound mismatch for field '{field}'")
    
    def test__construct_query_numeric_tolerance(self):
        field = 'central_wavelength'
        operator_match = '__exact'
        value = "500.0"
        query = self.astrodata_filter._construct_query(field, operator_match, value)
        self.assertIsInstance(query, Q)
        # Check for the presence of both bounds in the query
        keys = {child[0] for child in query.children}
        expected_keys = {
            self.astrodata_filter._build_descriptor_key(field, '__gte'),
            self.astrodata_filter._build_descriptor_key(field, '__lte')
        }
        self.assertTrue(keys >= expected_keys, "Query does not include both gte and lte conditions for numeric tolerance")

    def test__construct_query_partial_match(self):
        field = 'filter_name'
        operator_match = '__icontains'
        value = 'G-400'
        query = self.astrodata_filter._construct_query(field, operator_match, value)
        self.assertIsInstance(query, Q)
        self.assertIn((self.astrodata_filter._build_descriptor_key(field, operator_match), value), query.children)

    def test__construct_query_exact_match(self):
        field = 'object_name'
        operator_match = '__exact'
        value = 'NGC 1234'
        query = self.astrodata_filter._construct_query(field, operator_match, value)
        self.assertIsInstance(query, Q)
        self.assertIn((self.astrodata_filter._build_descriptor_key(field, operator_match), value), query.children)

    def test__construct_query_none_value_handling(self):
        field = 'detector_name'
        operator_match = '__exact'
        value = "None"
        query = self.astrodata_filter._construct_query(field, operator_match, value)
        self.assertIsInstance(query, Q)
        self.assertIn((self.astrodata_filter._build_descriptor_key(field, operator_match), None), query.children)

    def test__construct_query_datetime_handling_invalid_input(self):
        field = 'ut_datetime'
        operator_match = '__gte'
        value = 'invalid-datetime-format'
        query = self.astrodata_filter._construct_query(field, operator_match, value)
        self.assertIsInstance(query, Q)
        # Expecting no effective conditions if normalization fails
        self.assertTrue(all(x[1] is None for x in query.children), "Invalid datetime should result in no effective conditions")
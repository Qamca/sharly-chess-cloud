from unittest import TestCase

import pytest

from web.controllers.admin.player_admin_controller import PlayerAdminController

preprocess = PlayerAdminController._preprocess_csv_rows


@pytest.mark.unit
class TestPreprocessCsvRows(TestCase):
    def test_empty_input(self):
        self.assertEqual(preprocess([]), [])

    def test_all_single_column_rows_returns_empty(self):
        self.assertEqual(preprocess([['only one'], ['also one']]), [])

    def test_skips_preamble_single_column_rows(self):
        rows = [['Export date: 2024-01-01'], ['last_name', 'first_name', 'rating']]
        result = preprocess(rows)
        self.assertEqual(result[0], ['last_name', 'first_name', 'rating'])

    def test_basic_snake_case_header(self):
        rows = [['Last Name', 'First Name', 'Rating'], ['Smith', 'John', '1800']]
        result = preprocess(rows)
        self.assertEqual(result[0], ['last_name', 'first_name', 'rating'])

    def test_email_mapped_to_mail(self):
        rows = [['Email', 'Last Name'], ['a@b.com', 'Smith']]
        result = preprocess(rows)
        self.assertEqual(result[0][0], 'mail')

    def test_rating_column_any_variant(self):
        for header in ['Elo Rating', 'FIDE Rating', 'national_rating', 'Rating Elo']:
            with self.subTest(header=header):
                rows = [[header, 'last_name'], ['1850', 'Smith']]
                result = preprocess(rows)
                self.assertEqual(result[0][0], 'rating')

    def test_rating_extracts_bare_integer(self):
        rows = [['rating', 'last_name'], ['Elo: 2034 (nat)', 'Jones']]
        result = preprocess(rows)
        self.assertEqual(result[1][0], '2034')

    def test_rating_unrated_gives_empty(self):
        rows = [['rating', 'last_name'], ['Unrated', 'Smith']]
        result = preprocess(rows)
        self.assertEqual(result[1][0], '')

    def test_registration_date_column_dropped(self):
        rows = [['last_name', 'registration_date', 'rating'], ['Smith', '2024-01-01', '1800']]
        result = preprocess(rows)
        self.assertNotIn('registration_date', result[0])
        self.assertEqual(result[0], ['last_name', 'rating'])
        self.assertEqual(result[1], ['Smith', '1800'])

    def test_registered_column_dropped(self):
        rows = [['last_name', 'Registered', 'rating'], ['Smith', 'yes', '1800']]
        result = preprocess(rows)
        self.assertNotIn('registered', result[0])

    def test_date_of_registration_dropped(self):
        rows = [['last_name', 'Date of Registration'], ['Smith', '2024-05-01']]
        result = preprocess(rows)
        self.assertEqual(result[0], ['last_name'])

    def test_multiple_drop_columns(self):
        rows = [
            ['first_name', 'registration_date', 'last_name', 'signup_date'],
            ['John', '2024', 'Smith', '2024'],
        ]
        result = preprocess(rows)
        self.assertEqual(result[0], ['first_name', 'last_name'])
        self.assertEqual(result[1], ['John', 'Smith'])

    def test_data_rows_aligned_after_column_drop(self):
        rows = [
            ['last_name', 'registration_date', 'rating'],
            ['Smith', '2024-01-01', '1800'],
            ['Jones', '2024-02-01', '2000'],
        ]
        result = preprocess(rows)
        self.assertEqual(result[1], ['Smith', '1800'])
        self.assertEqual(result[2], ['Jones', '2000'])

    def test_no_mutation_of_original(self):
        original = [['Last Name', 'Rating'], ['Smith', '1800']]
        copy = [list(r) for r in original]
        preprocess(original)
        self.assertEqual(original, copy)

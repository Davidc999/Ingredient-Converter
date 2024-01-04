import unittest

from business_logic import bl_convert, bl_calculate, bl_pinches
from utils import set_conversion_rates


class TestAPI(unittest.TestCase):
    BASE_URL = 'http://localhost:5000'
    CONVERSION_JSON = {
      "cup": "16 tablespoon",
      "tablespoon": "3 teaspoon",
      "pound": "10 ounce",
      "teaspoon": "8 dash, 16 pinch"
    }

    def setUp(self):
        set_conversion_rates(conversion_rates=self.CONVERSION_JSON)

    # -------------- conversion success --------------
    def test_conversion_success_one_step_as_in_json(self):
        data = {
            "servingAmount": 2.5,
            "servingUnit": "cup",
            "convertTo": "tablespoon"
        }
        expected_res = {'servingUnit': 'tablespoon', 'servingAmount': 40.0}
        response_body = bl_convert(data)[0]
        self.assertEqual(expected_res, response_body)

    def test_conversion_success_reverse_step(self):
        data = {
            "servingAmount": 32,
            "servingUnit": "tablespoon",
            "convertTo": "cup"
        }
        expected_res = {'servingUnit': 'cup', 'servingAmount': 2.0}
        response_body = bl_convert(data)[0]
        self.assertEqual(expected_res, response_body)

    def test_conversion_success_compound_conversion(self):
        data = {
            "servingAmount": 1,
            "servingUnit": "cup",
            "convertTo": "pinch"
        }
        expected_res = {'servingUnit': 'pinch', 'servingAmount': 768.0}
        response_body = bl_convert(data)[0]
        self.assertEqual(expected_res, response_body)

    def test_conversion_success_big_number(self):
        data = {
            "servingAmount": 100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000,
            "servingUnit": "cup",
            "convertTo": "pinch"
        }
        response_code = bl_convert(data)[1]
        self.assertEqual(200, response_code)

    # -------------- conversion fail --------------
    def test_conversion_fail_missing_field(self):
        data = {
            "servingAmount": '2.5',
            "servingUnit": "cup",
        }
        response_code = bl_convert(data)[1]
        self.assertEqual(400, response_code)

    def test_conversion_fail_extra_field(self):
        data = {
            "servingAmount": 2.5,
            "servingUnit": "cup",
            "convertTo": "tablespoon",
            "extra": True
        }
        response_code = bl_convert(data)[1]
        self.assertEqual(400, response_code)

    def test_conversion_fail_invalid_serving_amount(self):
        data = {
            "servingAmount": '2.5',
            "servingUnit": "cup",
            "convertTo": "tablespoon"
        }
        response_code = bl_convert(data)[1]
        self.assertEqual(400, response_code)

    def test_conversion_fail_unfamiliar_serving_amount(self):
        data = {
            "servingAmount": 2.5,
            "servingUnit": "cups",
            "convertTo": "tablespoon"
        }
        response_code = bl_convert(data)[1]
        self.assertEqual(400, response_code)

    def test_conversion_fail_convert_to_is_true(self):
        data = {
            "servingAmount": 2.5,
            "servingUnit": "cup",
            "convertTo": True
        }
        response_code = bl_convert(data)[1]
        self.assertEqual(400, response_code)

    def test_conversion_fail_impossible_conversion(self):
        data = {
            "servingAmount": 32,
            "servingUnit": "pound",
            "convertTo": "cup"
        }
        response_code = bl_convert(data)[1]
        self.assertEqual(400, response_code)

    def test_conversion_fail_conflicting_rates_in_json(self):
        try:
            set_conversion_rates(conversion_rates={
              "cup": "16 tablespoon, 8 dash",
              "tablespoon": "3 teaspoon",
              "pound": "10 ounce",
              "teaspoon": "8 dash, 16 pinch"
            })
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))
            self.assertEqual('Conflicting ratios', e.args[0])

    # -------------- calculate success --------------
    def test_calculate_success(self):
        data = {
            "foodName": 'Peach',
            "servingUnit": "teaspoon",
            "amount": 96
        }
        expected_res = {'sugar grams': 8.0}
        response_body = bl_calculate(data)[0]
        self.assertEqual(expected_res, response_body)

    # -------------- calculate fail --------------
    def test_calculate_fail_missing_field(self):
        data = {
            "foodName": 'Peach',
            "servingUnit": "teaspoon",
        }
        response_code = bl_calculate(data)[1]
        self.assertEqual(400, response_code)

    def test_calculate_fail_extra_field(self):
        data = {
            "foodName": 'Peach',
            "servingUnit": "teaspoon",
            "amount": 96,
            "extra": True
        }
        response_code = bl_calculate(data)[1]
        self.assertEqual(400, response_code)

    def test_calculate_fail_unfamiliar_food_name(self):
        data = {
            "foodName": 'grape',
            "servingUnit": "teaspoon",
            "amount": 48
        }
        response_code = bl_calculate(data)[1]
        self.assertEqual(400, response_code)

    def test_calculate_fail_unfamiliar_serving_unit(self):
        data = {
            "foodName": 'Grape',
            "servingUnit": "Teaspoon",
            "amount": 48
        }
        response_code = bl_calculate(data)[1]
        self.assertEqual(400, response_code)

    def test_calculate_fail_invalid_amount(self):
        data = {
            "foodName": 'Grape',
            "servingUnit": "Teaspoon",
            "amount": 'x'
        }
        response_code = bl_calculate(data)[1]
        self.assertEqual(400, response_code)

    # -------------- pinches success --------------
    def test_pinches_success(self):
        data = {
            "pinchNum": 3,
            "servingUnit": "tablespoon"
        }
        expected_res = {'pinch': 0.0625}
        response_body = bl_pinches(data)[0]
        self.assertEqual(expected_res, response_body)

    # -------------- pinches fail --------------
    def test_pinches_fail_unreachable_serving_unit(self):
        data = {
            "pinchNum": 3,
            "servingUnit": "pound"
        }
        response_code = bl_pinches(data)[1]
        self.assertEqual(400, response_code)

    def test_pinches_fail_pinch_num_field_wrong_type(self):
        data = {
            "pinchNum": '3',
            "servingUnit": "tablespoon"
        }
        response_code = bl_pinches(data)[1]
        self.assertEqual(400, response_code)

    def test_pinches_fail_serving_unit_field_wrong_type(self):
        data = {
            "pinchNum": '3',
            "servingUnit": 3
        }
        response_code = bl_pinches(data)[1]
        self.assertEqual(400, response_code)

    def test_pinches_fail_no_pinch_num_field(self):
        data = {
            "teaspoonNum": 3,
            "servingUnit": "tablespoon"
        }
        response_code = bl_pinches(data)[1]
        self.assertEqual(400, response_code)

    def test_pinches_fail_extra_field(self):
        data = {
            "extra": True,
            "teaspoonNum": 3,
            "servingUnit": "tablespoon"
        }
        response_code = bl_pinches(data)[1]
        self.assertEqual(400, response_code)

    def test_pinches_fail_missing_field(self):
        data = {
            "servingUnit": "tablespoon"
        }
        response_code = bl_pinches(data)[1]
        self.assertEqual(400, response_code)

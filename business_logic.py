from utils import convert, get_conversion_rates, get_sugar_conversions


def bl_convert(data):
    serving_unit = data.get('servingUnit', False)
    final_unit = data.get('convertTo', False)
    serving_amount = data.get('servingAmount', False)

    if not all([
        len(data.keys()) == 3,
        type(serving_amount) == float or type(serving_amount) == int,
        type(serving_unit) == str,
        serving_unit in get_conversion_rates(),
        type(final_unit) == str
    ]):
        return 'Validation error', 400

    try:
        serving_amount = convert(serving_unit, serving_amount, final_unit)
        return {'servingAmount': serving_amount, 'servingUnit': final_unit}, 200
    except ValueError:
        return "Conversion can't be made", 400


def bl_calculate(data):
    food_name = data.get('foodName', False)
    serving_unit = data.get('servingUnit', False)
    serving_amount = data.get('amount', False)

    if not all([
        len(data.keys()) == 3,
        type(serving_amount) == float or type(serving_amount) == int,
        type(serving_unit) == str,
        serving_unit in get_conversion_rates(),
        food_name in get_sugar_conversions()
    ]):
        return 'Validation error', 400

    try:
        cup_amounts = convert(serving_unit, serving_amount, 'cup')
    except ValueError:
        return "Conversion can't be made", 400

    sugar_grams_per_cup = float(get_sugar_conversions()[food_name]['1 cup'].split(' ')[0])
    total_sugar_grams = sugar_grams_per_cup * cup_amounts

    return {'sugar grams': total_sugar_grams}, 200


def bl_pinches(data):
    """json body example:
    {
        "pinchNum": 3,
        "servingUnit": "teaspoons"
    }
    """
    serving_unit = data.get('servingUnit', False)
    pinch_num = data.get('pinchNum', False)

    if not all([
        len(data.keys()) == 2,
        type(pinch_num) == float or type(pinch_num) == int,
        type(serving_unit) == str,
    ]):
        return 'Validation error', 400

    try:
        pinch_amount = convert('pinch', pinch_num, serving_unit)
        return {'pinch': pinch_amount}, 200
    except ValueError:
        return "Conversion can't be made", 400

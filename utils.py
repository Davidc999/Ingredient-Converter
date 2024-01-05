import json

from config import JSON_CONVERSION_PATH, JSON_SUGAR_CALC


CONVERSION_RATES = {}
SUGAR_CONVERSIONS = {}


def set_conversion_rates(file_path=JSON_CONVERSION_PATH, conversion_rates=None):
    global CONVERSION_RATES
    if conversion_rates:
        CONVERSION_RATES = load_conversion_rates(conversion_rates)
    else:
        with open(file_path) as f:
            json_body = json.loads(f.read())

        CONVERSION_RATES = load_conversion_rates(json_body)


def set_sugar_conversions():
    global SUGAR_CONVERSIONS
    SUGAR_CONVERSIONS = load_sugar_conversions()


def validate_ratios(conversion_rates):
    for converted_ratios in conversion_rates.values():
        for i, (unit_a, amount_a) in enumerate(converted_ratios.items()):
            for unit_b, amount_b in list(converted_ratios.items())[i+1:]:
                if conversion_rates[unit_a][unit_b] != amount_b / amount_a:
                    raise ValueError('Conflicting ratios')


def get_inferred_conversion_rate(base_unit, converted_unit, visited, conversion_rates):
    if base_unit in visited:
        return

    visited.add(base_unit)

    if converted_unit in conversion_rates[base_unit]:
        return conversion_rates[base_unit][converted_unit]

    if base_unit == converted_unit:
        return 1

    for known_unit in [x for x in conversion_rates[base_unit]]:
        x = get_inferred_conversion_rate(known_unit, converted_unit, visited=visited, conversion_rates=conversion_rates)
        if x:
            return x * conversion_rates[base_unit][known_unit]


def get_amount_unit_list_from_string(in_str):
    str_list = in_str.split(",")
    amount_unit_list = [x.strip().split() for x in str_list]
    return amount_unit_list


def load_conversion_rates(json_body):
    all_units = set()
    for unit, amount_converted_units in json_body.items():
        all_units.add(unit)
        amount_unit_list = get_amount_unit_list_from_string(amount_converted_units)
        equal_measurements = [unit for measurement, unit in amount_unit_list]
        all_units.update(equal_measurements)

    raw_rates = dict()
    for unit in all_units:
        raw_rates[unit] = {}

    for unit, amount_converted_units in json_body.items():
        equal_measurements = get_amount_unit_list_from_string(amount_converted_units)
        for measurement in equal_measurements:
            amount_a, converted_unit_a = measurement

            raw_rates[unit][converted_unit_a] = float(amount_a)
            raw_rates[converted_unit_a][unit] = float(1) / float(amount_a)

    # inferring indirect rates
    for base_unit in all_units:
        for converted_unit in all_units:
            conversion_rate = get_inferred_conversion_rate(base_unit=base_unit, visited=set(),
                                         converted_unit=converted_unit,
                                         conversion_rates=raw_rates)
            if conversion_rate:
                raw_rates[base_unit][converted_unit] = conversion_rate

    # checking for rate conflicts
    validate_ratios(raw_rates)

    return raw_rates


def load_sugar_conversions(path=JSON_SUGAR_CALC):
    with open(path) as f:
        json_body = json.loads(f.read())

    return json_body


def convert(serving_unit, serving_amount, final_unit):
    serving_amount = float(serving_amount)

    if serving_unit not in CONVERSION_RATES or final_unit not in CONVERSION_RATES:
        raise ValueError("Invalid units")

    if final_unit not in CONVERSION_RATES[serving_unit]:
        raise ValueError("No conversion path found")

    return CONVERSION_RATES[serving_unit][final_unit] * serving_amount


def calculate_sugar_grams_per_cup(food_name):
    return float(SUGAR_CONVERSIONS[food_name]['1 cup'].split(' ')[0])


set_conversion_rates()
set_sugar_conversions()

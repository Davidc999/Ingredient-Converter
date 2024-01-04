import json

from config import JSON_CONVERSION_PATH, JSON_SUGAR_CALC


CONVERSION_RATES = {}
SUGAR_CONVERSIONS = {}


def get_conversion_rates():
    return CONVERSION_RATES


def get_sugar_conversions():
    return SUGAR_CONVERSIONS


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

    if converted_unit in conversion_rates[base_unit] and conversion_rates[base_unit][converted_unit] != {}:
        return conversion_rates[base_unit][converted_unit]

    for known_unit in [x for x in conversion_rates[base_unit] if conversion_rates[base_unit][x] != {}]:
        x = get_inferred_conversion_rate(known_unit, converted_unit, visited=visited, conversion_rates=conversion_rates)
        if x and conversion_rates[base_unit][known_unit]:
            return x * conversion_rates[base_unit][known_unit]


def load_conversion_rates(json_body):
    all_units = set()
    for unit, amount_converted_unites in json_body.items():
        all_units.add(unit)
        equal_measurements = amount_converted_unites.split(', ')
        equal_measurements = [x.split(' ')[1] for x in equal_measurements]
        all_units.update(equal_measurements)

    raw_rates = dict()
    for j, unit in enumerate(all_units):
        raw_rates[unit] = {k: {} for k in (list(all_units)[:j] + list(all_units)[j+1:])}

    for unit, amount_converted_units in json_body.items():
        equal_measurements = amount_converted_units.split(', ')
        equal_measurements = [x.split(' ') for x in equal_measurements]
        equal_measurements.append([1, unit])
        for j, measurement in enumerate(equal_measurements):
            for next_measurement in equal_measurements[j+1:]:
                amount_a, converted_unit_a = measurement
                amount_b, converted_unit_b = next_measurement

                raw_rates[converted_unit_a][converted_unit_b] = float(amount_b) / float(amount_a)
                raw_rates[converted_unit_b][converted_unit_a] = float(amount_a) / float(amount_b)

    # inferring indirect rates
    for unit, conversion_rates in raw_rates.items():
        for converted_unit, amount in conversion_rates.items():
            if amount != {}:
                continue
            raw_rates[unit][converted_unit] = get_inferred_conversion_rate(base_unit=unit, converted_unit=converted_unit, visited=set(), conversion_rates=raw_rates)

    clean_rates = dict()
    for k, v in raw_rates.items():
        clean_rates[k] = {x: y for x, y in v.items() if y is not None}

    # checking for rate conflicts
    validate_ratios(clean_rates)
    return clean_rates


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

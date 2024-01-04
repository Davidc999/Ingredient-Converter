from flask import Flask
from flask import request

from business_logic import bl_convert, bl_calculate, bl_pinches

app = Flask(__name__)


@app.route("/convert", methods=['POST'])
def convert():
    """
    request example
    {
        "servingAmount": 2.5,
        "servingUnit": "cup",
        "convertTo": "tablespoon"
    }
    """
    return bl_convert(request.get_json())
    

@app.route("/calculate", methods=['POST'])
def calculate():
    """
    request example
    {
        "foodName": 'Peach',
        "servingUnit": "teaspoon",
        "amount": 96
    }
    """
    return bl_calculate(request.get_json())


@app.route("/pinches", methods=['POST'])
def pinch_converter():
    """
    request example
    {
        "pinchNum": 3,
        "servingUnit": "tablespoon"
    }
    """
    return bl_pinches(request.get_json())

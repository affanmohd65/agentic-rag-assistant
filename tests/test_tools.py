from app.tools import calculator

def test_calculator_basic():
    assert calculator("2 + 2") == "4"

def test_calculator_order_of_ops():
    assert calculator("2 + 3 * 4") == "14"

def test_calculator_invalid_expression_returns_error_string():
    result = calculator("import os")
    assert result.startswith("error")

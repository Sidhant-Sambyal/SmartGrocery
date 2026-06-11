from app.services.quantity_service import (
    parse_quantity,
    calculate_shade,
)


def test_parse_grams():

    amount, unit, base, name = parse_quantity(
        "250 g pasta"
    )

    assert amount == 250.0
    assert unit == "g"
    assert base == 250.0
    assert name == "pasta"


def test_parse_kg():

    amount, unit, base, name = parse_quantity(
        "2 kg rice"
    )

    assert amount == 2.0
    assert unit == "kg"
    assert base == 2000.0
    assert name == "rice"


def test_parse_liters():

    amount, unit, base, name = parse_quantity(
        "1 l milk"
    )

    assert amount == 1.0
    assert unit == "l"
    assert base == 1000.0
    assert name == "milk"


def test_invalid_input():

    assert parse_quantity("banana") is None


def test_bare_quantity_no_name():
    """A bare quantity like '500g' with no item name should return None."""

    assert parse_quantity("500g") is None
    assert parse_quantity("2 kg") is None


def test_shade_clamped():

    assert calculate_shade(10000) == 1.0
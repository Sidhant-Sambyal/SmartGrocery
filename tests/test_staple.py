from app.services.staple_service import (
    is_staple
)


def test_salt():

    assert is_staple("salt")


def test_sugar():

    assert is_staple("sugar")


def test_rice():

    assert is_staple("rice")


def test_not_staple():

    assert not is_staple("banana")


def test_case_insensitive():

    assert is_staple("SALT")
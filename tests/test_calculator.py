"""Tests for the Calculator API utility service."""

from fastapi.testclient import TestClient

from calculator.main import app

client = TestClient(app)


def test_add():
    assert client.get("/add", params={"a": 2, "b": 3}).json() == {"result": 5}


def test_divide():
    assert client.get("/divide", params={"a": 9, "b": 3}).json() == {"result": 3.0}


def test_divide_by_zero_is_a_clean_400():
    assert client.get("/divide", params={"a": 1, "b": 0}).status_code == 400


def test_modulo_by_zero_is_a_clean_400():
    assert client.get("/modulo", params={"a": 1, "b": 0}).status_code == 400


def test_missing_parameter_is_422():
    assert client.get("/add", params={"a": 1}).status_code == 422


def test_subtract_and_multiply():
    assert client.get("/subtract", params={"a": 7, "b": 4}).json() == {"result": 3}
    assert client.get("/multiply", params={"a": 6, "b": 7}).json() == {"result": 42}


def test_calculator_root():
    assert client.get("/").json()["status"] == "online"

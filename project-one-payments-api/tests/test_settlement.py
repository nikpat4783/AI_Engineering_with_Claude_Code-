import pytest
from src.settlement.rules import settlement_window


def test_india_settlement_window():
    """Verify India (IN) uses T+1 settlement"""
    assert settlement_window("IN") == "T+1"


def test_uae_settlement_window():
    """Verify UAE (AE) uses T+1 settlement"""
    assert settlement_window("AE") == "T+1"


def test_default_settlement_window():
    """Verify unmapped regions use T+2 settlement"""
    assert settlement_window("US") == "T+2"
    assert settlement_window("GB") == "T+2"
    assert settlement_window("SG") == "T+2"


def test_empty_region():
    """Verify empty string defaults to T+2"""
    assert settlement_window("") == "T+2"


def test_none_region():
    """Verify None region defaults to T+2"""
    assert settlement_window(None) == "T+2"


def test_case_sensitivity():
    """Verify region codes are case-sensitive"""
    assert settlement_window("in") == "T+2"
    assert settlement_window("ae") == "T+2"
    assert settlement_window("IN") == "T+1"
    assert settlement_window("AE") == "T+1"

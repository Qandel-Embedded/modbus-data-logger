"""Unit tests for ModbusLogger (using mock client)."""
import pytest, tempfile, os, csv, sqlite3
from unittest.mock import MagicMock


def make_mock_client(value=250):
    client = MagicMock()
    rr = MagicMock()
    rr.isError.return_value = False
    rr.registers = [value]
    client.read_holding_registers.return_value = rr
    return client


def make_registers():
    return [{'address': 0, 'count': 1, 'name': 'temperature', 'scale': 0.1}]


def test_poll_returns_dict():
    from modbus_data_logger import ModbusLogger
    logger = ModbusLogger(make_mock_client(250), registers=make_registers())
    row = logger._poll()
    assert 'temperature' in row
    assert abs(row['temperature'] - 25.0) < 0.01


def test_poll_on_error_returns_none():
    from modbus_data_logger import ModbusLogger
    client = MagicMock()
    err = MagicMock(); err.isError.return_value = True
    client.read_holding_registers.return_value = err
    logger = ModbusLogger(client, registers=make_registers())
    row = logger._poll()
    assert row['temperature'] is None


def test_log_csv_creates_file():
    from modbus_data_logger import ModbusLogger
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        path = f.name
    logger = ModbusLogger(make_mock_client(), registers=make_registers(), interval_s=0)
    logger.log_csv(path, duration_s=0.01)
    with open(path) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 1
    os.unlink(path)

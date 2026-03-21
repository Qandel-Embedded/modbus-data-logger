# modbus-data-logger

[![CI](https://github.com/Qandel-Embedded/modbus-data-logger/actions/workflows/ci.yml/badge.svg)](https://github.com/Qandel-Embedded/modbus-data-logger/actions)
[![PyPI](https://img.shields.io/badge/pypi-modbus--data--logger-blue)](https://pypi.org/project/modbus-data-logger)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Log **any Modbus RTU or TCP device** to CSV or SQLite with a single command.  
Works with PLCs, VFDs, power meters, sensors — any Modbus-compliant hardware.

## Install

```bash
pip install modbus-data-logger
```

## Quick Start (CLI)

```bash
# Log 2 registers from a TCP device every second for 1 hour
modbus-log tcp \
  --host 192.168.1.10 \
  --registers "0:1:temperature:0.1,1:1:pressure:0.01" \
  --interval 1.0 \
  --output plant_data.csv \
  --duration 3600
```

## Python API

```python
from pymodbus.client import ModbusTcpClient
from modbus_data_logger import ModbusLogger

registers = [
    {'address': 0, 'count': 1, 'name': 'temperature', 'scale': 0.1},
    {'address': 1, 'count': 1, 'name': 'pressure',    'scale': 0.01},
]

client = ModbusTcpClient('192.168.1.10')
client.connect()

logger = ModbusLogger(client, slave_id=1, registers=registers, interval_s=1.0)
logger.log_csv('data.csv', duration_s=3600)        # CSV output
logger.log_sqlite('plant.db', duration_s=3600)     # SQLite output
```

---
Made by **[Ahmed Qandel](https://ahmedqandel.com)** — Industrial Automation & Embedded Systems Engineer  
Available for freelance contracts via Upwork.

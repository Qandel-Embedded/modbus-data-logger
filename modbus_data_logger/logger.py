"""Core Modbus polling and storage engine."""
import time, csv, sqlite3, datetime, logging
from io import StringIO

log = logging.getLogger(__name__)


class ModbusLogger:
    """Polls Modbus registers and stores data to CSV or SQLite.

    Args:
        client: a connected pymodbus client (RTU or TCP)
        slave_id: Modbus device address (1-247)
        registers: list of dicts with keys: address, count, name, scale
        interval_s: poll interval in seconds

    Example::

        from pymodbus.client import ModbusTcpClient
        from modbus_data_logger import ModbusLogger

        client = ModbusTcpClient('192.168.1.10', port=502)
        client.connect()

        registers = [
            {'address': 0, 'count': 1, 'name': 'temperature', 'scale': 0.1},
            {'address': 1, 'count': 1, 'name': 'pressure',    'scale': 0.01},
        ]

        logger = ModbusLogger(client, slave_id=1, registers=registers)
        logger.log_csv('output.csv', duration_s=3600)
    """

    def __init__(self, client, slave_id: int = 1,
                 registers: list = None, interval_s: float = 1.0):
        self._client    = client
        self._slave     = slave_id
        self._regs      = registers or []
        self._interval  = interval_s

    def _poll(self) -> dict:
        row = {'timestamp': datetime.datetime.now().isoformat()}
        for reg in self._regs:
            rr = self._client.read_holding_registers(
                address=reg['address'], count=reg.get('count', 1), slave=self._slave)
            if not rr.isError():
                raw = rr.registers[0]
                row[reg['name']] = raw * reg.get('scale', 1.0)
            else:
                row[reg['name']] = None
        return row

    def log_csv(self, path: str, duration_s: float = None):
        """Log to CSV file. Runs indefinitely if duration_s is None."""
        start = time.monotonic()
        with open(path, 'w', newline='') as f:
            writer = None
            while True:
                row = self._poll()
                if writer is None:
                    writer = csv.DictWriter(f, fieldnames=row.keys())
                    writer.writeheader()
                writer.writerow(row)
                f.flush()
                log.info(row)
                time.sleep(self._interval)
                if duration_s and (time.monotonic() - start) >= duration_s:
                    break

    def log_sqlite(self, db_path: str, table: str = 'readings',
                   duration_s: float = None):
        """Log to SQLite database."""
        conn  = sqlite3.connect(db_path, check_same_thread=False)
        start = time.monotonic()
        initialized = False
        while True:
            row = self._poll()
            if not initialized:
                cols = ', '.join(
                    f'{k} TEXT' if k == 'timestamp' else f'{k} REAL'
                    for k in row)
                conn.execute(f'CREATE TABLE IF NOT EXISTS {table} ({cols})')
                conn.commit()
                initialized = True
            placeholders = ', '.join(['?'] * len(row))
            conn.execute(
                f'INSERT INTO {table} VALUES ({placeholders})',
                list(row.values()))
            conn.commit()
            log.info(row)
            time.sleep(self._interval)
            if duration_s and (time.monotonic() - start) >= duration_s:
                break
        conn.close()

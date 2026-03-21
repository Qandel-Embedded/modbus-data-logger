"""CLI entry-point for modbus-data-logger."""
import click, logging, sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')


@click.group()
def main():
    """modbus-log — CLI tool to log Modbus registers to CSV or SQLite."""
    pass


@main.command()
@click.option('--host',      required=True,      help='Modbus TCP host/IP')
@click.option('--port',      default=502,         show_default=True)
@click.option('--slave',     default=1,           show_default=True)
@click.option('--registers', default='0:1:value:1.0', show_default=True,
              help='Comma-separated addr:count:name:scale, e.g. 0:1:temp:0.1,1:1:pressure:0.01')
@click.option('--interval',  default=1.0,         show_default=True)
@click.option('--output',    default='data.csv',  show_default=True)
@click.option('--duration',  default=None, type=float)
@click.option('--format',    'fmt', default='csv', type=click.Choice(['csv','sqlite']))
def tcp(host, port, slave, registers, interval, output, duration, fmt):
    """Log registers from a Modbus TCP device."""
    try:
        from pymodbus.client import ModbusTcpClient
        from modbus_data_logger import ModbusLogger
    except ImportError:
        click.echo('Install pymodbus: pip install pymodbus'); sys.exit(1)

    reg_list = []
    for r in registers.split(','):
        parts = r.split(':')
        reg_list.append({'address': int(parts[0]), 'count': int(parts[1]),
                         'name': parts[2], 'scale': float(parts[3])})

    client = ModbusTcpClient(host, port=port)
    client.connect()
    click.echo(f'Connected to {host}:{port}  slave={slave}')

    logger = ModbusLogger(client, slave_id=slave, registers=reg_list, interval_s=interval)
    if fmt == 'sqlite':
        logger.log_sqlite(output, duration_s=duration)
    else:
        logger.log_csv(output, duration_s=duration)
    client.close()


if __name__ == '__main__':
    main()

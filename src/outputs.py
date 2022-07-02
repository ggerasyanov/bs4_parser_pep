import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


def control_output(results, cli_args):
    output = cli_args.output
    if output in operating_modes.keys():
        operating_modes[output](results, cli_args)
    else:
        default_output(results)


def default_output(results):
    for row in results:
        print(*row)


def pretty_output(results, cli_args):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    result_dir = BASE_DIR / 'results'
    result_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode

    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)

    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = result_dir / file_name

    with open(file_path, 'w', encoding='utf-8') as f:
        write = csv.writer(f, dialect='unix')
        write.writerows(results)
    logging.info(f'Файл с резултатами был сохранён: {file_path}')


operating_modes = {
    'pretty': pretty_output,
    'file': file_output,
}

import logging
import re
from urllib.parse import urljoin
from collections import defaultdict

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, DOWNLOADS_URL, EXPECTED_STATUS, MAIN_DOC_URL,
                       MAIN_PEP_URL, WHATS_NEW_URL)
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    response = get_response(session, WHATS_NEW_URL)
    soup = BeautifulSoup(response.text, 'lxml')

    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'})

    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(WHATS_NEW_URL, href)
        response = get_response(session, version_link)
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        result.append(
            (version_link, h1.text, dl_text)
        )

    return result


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    soup = BeautifulSoup(response.text, 'lxml')

    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]

    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = re.search(pattern, a_tag.text).groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))

    return results


def download(session):
    response = get_response(session, DOWNLOADS_URL)
    soup = BeautifulSoup(response.text, 'lxml')

    table = find_tag(soup, 'table', attrs={'class': 'docutils'})

    pdf_a4_tag = find_tag(table, 'a', attrs={
        'href': re.compile(r'.+pdf-a4\.zip$')
    })
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(DOWNLOADS_URL, pdf_a4_link)

    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def collecion_data(count_status, total_count, result):
    for status, count in count_status.items():
        # если использовать extend ломается prettytable
        result.append(
            (status, count)
        )

    result.append(
        ('Total', total_count)
    )
    return result


def pep(session):
    response = get_response(session, MAIN_PEP_URL)
    soup = BeautifulSoup(response.text, 'lxml')
    table_pep = find_tag(soup, 'section', {'id': 'numerical-index'})
    pep_doc = find_tag(table_pep, 'tbody')
    lines_table = pep_doc.find_all('tr')
    result = [
        ('Статус', 'Количество')
    ]
    logs = []
    count_status = defaultdict(int)
    total_count = 0

    for line in tqdm(lines_table):
        columns = line.find_all('td')
        status = columns[0].text
        number_pep = find_tag(columns[1], 'a')

        pep_page_url = urljoin(MAIN_PEP_URL, number_pep['href'])
        response = get_response(session, pep_page_url)
        soup = BeautifulSoup(response.text, 'lxml')
        table_pep_page = find_tag(soup, 'dl', {
            'class': 'rfc2822 field-list simple'
        })
        dt_table = table_pep_page.find_all('dt')
        status_page = ''
        for item in dt_table:
            if item.text == 'Status:':
                status_page = item.find_next_sibling('dd').text

        if len(status) > 1:
            status = list(status)[1]
        else:
            status = ''
        full_status = EXPECTED_STATUS[status]

        if status_page not in full_status:
            logs.append(f"""
            Несовпадающие статусы:
            {pep_page_url}
            Статус в карточке: {status_page}
            Ожидаемы статус: {full_status}
            """)

        # if status_page in count_status.keys():
        count_status[status_page] += 1
        total_count += 1

    for i in logs:
        logging.info(i)

    return collecion_data(count_status, total_count, result)


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командой строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode

    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()

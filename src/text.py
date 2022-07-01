import requests_cache
from bs4 import BeautifulSoup

session = requests_cache.CachedSession()
response = session.get('https://peps.python.org/pep-0001/')
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'lxml')
table_pep_page = soup.find('dl', {'class': 'rfc2822 field-list simple'})
dt_table = table_pep_page.find_all('dt')
status_page = ''
for item in dt_table:
    if item.text == 'Status:':
        status_page = item.find_next_sibling('dd')
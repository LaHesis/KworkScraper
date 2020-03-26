import requests
from bs4 import BeautifulSoup
from re import sub, findall
import os


NO_DATA = '-'
TASKS_AT_ONE_PAGE = 12
BASE_URL = 'https://kwork.ru/projects'
OUTPUT_FILES_DIR = 'output'


# Their order is very important. Data rows are being added in the same order.
field_names = [
    'TITLE',
    'DESCRIPTION',
    'PRICE_UP_TO',
]
STORAGE = {
    '3d': {'code': '29', 'data': {}},
    #'all_IT': {'code': '11', 'data': {}},
    'PC_programs': {'code': '80', 'data': {}},
    'scripts_and_bots': {'code': '41', 'data': {}},
}
for cat_name in STORAGE.keys():
    STORAGE[cat_name]['data'] = {label + 'S': [] for label in field_names}


def scrape_page(url, task_lists_dict):
    """Scrapes a page and returns whether there is next."""
    print('scraping', url)
    with requests.get(url) as resp:
        page_soup = BeautifulSoup(resp.text, 'html.parser')

    labels = tuple(task_lists_dict.keys())
    for task in page_soup.find_all('div', class_='want-card'):
        title = task.find('div', class_='wants-card__header-title').a.text
        task_lists_dict[labels[0]].append(title)

        try:
            # When a description is partial with show/hide feature.
            description = task.find(
                'div', class_='breakwords first-letter f14 js-want-block-toggle js-want-block-toggle-full lh22 hidden').text
        except AttributeError:
            # When a description has no show/hide feature.
            description = task.find('div', class_='mt10').text
        description = sub(r'\n{2,}', '\n', description)
        task_lists_dict[labels[1]].append(description)

        price = task.find('div', class_='wants-card__header-price').text
        price = ''.join(findall(r'\d+', price))
        task_lists_dict[labels[2]].append(price)

    next_page_anchor = page_soup.find('a', class_='next')
    return bool(next_page_anchor) and next_page_anchor['href']


def scrape_some_categories(cat_name):
    cat_storage = STORAGE[cat_name]['data']
    cat_code = STORAGE[cat_name]['code']
    next_page_url = scrape_page(f'{BASE_URL}?c={cat_code}', cat_storage)
    while next_page_url:
        next_page_url = scrape_page(next_page_url, cat_storage)


def save_data_to_txt(cat_name):
    print(f'saving {cat_name}')
    f_name = os.path.join(OUTPUT_FILES_DIR, f'{cat_name}_scraped_data.txt')
    with open(f_name, 'w', encoding='utf-8') as out_file:
        lists = STORAGE[cat_name]['data'].values()
        text = ''
        for fields in zip(*lists):
            rows = list(zip(field_names, fields))
            rows = list(map(lambda row: ':\n'.join(row), rows))
            text += '\n\n'.join(rows)
            text += '\n' + '='*40 + '\n'*3
        out_file.write(text)


for cat_name in STORAGE.keys():
    print(f'scraping {cat_name}\n{"="*40}')
    scrape_some_categories(cat_name)
    save_data_to_txt(cat_name)
    print()

import requests
from bs4 import BeautifulSoup
import re
import os
import datetime
import PySimpleGUI as sg
import subprocess


MARGIN = ' '*25
NO_DATA = '-'
TASKS_AT_ONE_PAGE = 12
BASE_URL = 'https://kwork.ru/projects'
OUTPUT_FILES_DIR = 'output'
# Their order is very important. Data rows are being added in the same order.
FIELD_NAMES = [
    'TITLE',
    'DESCRIPTION',
    'TIMEOUT',
    'OFFERS',
    'PRICE_UP_TO',
]
CATEGORIES = []
PROJECTS = []
with open('CATEGORIES.dat', 'r') as cats:
    for line in cats:
        CATEGORIES.append(line.strip())


def scrape_category(cat_name, necessaryText, window: sg.Window):
    cat_code = cat_name.split()[1]
    status = scrape_page(f'{BASE_URL}?c={cat_code}', necessaryText, 1)
    window.refresh()
    while status['next_page_url']:
        status = scrape_page(
            status['next_page_url'], necessaryText, status['last_pr_num']
        )
    print('The category has been scraped.')


def scrape_page(url, necessaryText, last_pr_num):
    """Scrapes a page and returns scraping status."""
    print(MARGIN + 'scraping', url, end='\n\n')
    with requests.get(url) as resp:
        page_soup = BeautifulSoup(resp.text, 'html.parser')

    for pr_num, prj in enumerate(
        page_soup.find_all('div', class_='want-card'), last_pr_num
    ):
        scraped_prj = {}
        title = prj.find('div', class_='wants-card__header-title').a.text
        scraped_prj[FIELD_NAMES[0]] = title

        # When a description is partial with show/hide feature.
        d_cls = 'breakwords first-letter f14 js-want-block-toggle ' \
                'js-want-block-toggle-full lh22 hidden'
        description = prj.find('div', class_=d_cls)
        if not description:
            # When a description has no show/hide feature.
            description = prj.find('div', class_='mt10')

        anchors = description.find_all('a')
        description = re.sub(r'\n{2,}', '\n', description.text).strip()
        for anchor in anchors:
            anc_text = anchor.text.strip()
            anc_text_and_href = f'[{anc_text}] (< {anchor["href"]} >)'
            description = description.replace(anc_text, anc_text_and_href)
        scraped_prj[FIELD_NAMES[1]] = description
        # Project title or description should contain necessary text.
        if necessaryText and necessaryText not in scraped_prj[FIELD_NAMES[0]] \
                and necessaryText not in scraped_prj[FIELD_NAMES[1]]:
            continue

        info = prj.find('div', class_='query-item__info mb10 ta-left')
        timeout, offers = info.text.split(' \xa0\xa0\xa0')
        timeout = timeout[timeout.find(' ') + 1:]
        offers = re.search(r'\d+', offers).group()
        scraped_prj[FIELD_NAMES[2]] = timeout
        scraped_prj[FIELD_NAMES[3]] = offers

        price = prj.find('div', class_='wants-card__header-price').text
        price = re.search(r'\d[\d ]+', price).group()
        scraped_prj[FIELD_NAMES[4]] = price
        PROJECTS.append(scraped_prj)

        print(get_project_as_text(scraped_prj, pr_num))
        window.refresh()

    next_page_anchor = page_soup.find('a', class_='next')
    return {
        'next_page_url': bool(next_page_anchor) and next_page_anchor['href'],
        'last_pr_num': pr_num
    }


def get_project_as_text(project, item_number):
    text = ''
    fields = list(project.items())
    title = f'{MARGIN}№ {str(item_number)}: {fields[0][1].upper()}'
    desc = f'{MARGIN + fields[1][0]}:\n{fields[1][1]}'
    price = f'{MARGIN + fields[2][0]}: {fields[2][1]}'
    timeout = f'{MARGIN + fields[3][0]}: {fields[3][1]}'
    offers = f'{MARGIN + fields[4][0]}: {fields[4][1]}'
    text += '\n'.join((title, desc, price, timeout, offers))
    text += '\n'*3
    return text


def save_projects_to_file(cat_name):
    print(f'saving {cat_name}')
    f_name = os.path.join(OUTPUT_FILES_DIR, f'{cat_name}_scraped_data.txt')
    with open(f_name, 'w', encoding='utf-8') as out_file:
        for project in print_projects_of_cat_as_texts(cat_name, PROJECTS):
            out_file.write(project)


def print_projects_of_cat_as_texts(cat_name, projects):
    yield get_scraping_title(cat_name)
    for item_number, project in enumerate(projects, 1):
        yield get_project_as_text(project, item_number)


def get_scraping_title(cat_name):
    date = datetime.datetime.now()
    return f'{MARGIN}Projects at "{cat_name}" scraped on {date}\n\n'


sg.theme('DarkAmber')
# All the stuff inside your window.
prjs_out = sg.Output(size=(160, 30))
buttons = [
    sg.Button('Scrape projects'),
    sg.Button('Save scraped projects to file'),
    sg.Button('Open saved files directory'),
    sg.Button('Exit'),
]
layout = [
    [sg.Text('Select category:'), sg.Combo(CATEGORIES, key='Category', default_value=CATEGORIES[0]), sg.Text('Project must contain text:'), sg.Input(key='NecessaryText')],
    [*buttons],
    [sg.Text('Projects in the category:')],
    [prjs_out],
]
# Create the Window.
window = sg.Window('Kwork Projects Scraper', layout, resizable=True, size=(1200, 600), finalize=True)
window.Maximize()
prjs_out.expand(expand_x=True, expand_y=True)
for btn in buttons:
    btn.set_cursor('hand2')

# Event Loop to process "events" and get the "values" of the inputs.
while True:
    event, values = window.read()
    if event in (None, 'Exit'):   # if user closes window or clicks cancel.
        break
    if event == 'Scrape projects':
        prjs_out.update(get_scraping_title(values["Category"]))
        date = datetime.datetime.now()
        PROJECTS.clear()
        scrape_category(values['Category'], values['NecessaryText'], window)
    elif event == 'Save scraped projects to file':
        if not PROJECTS:
            sg.popup_error('Nothing to save yet.')
        else:
            save_projects_to_file(values['Category'])
    elif event == 'Open saved files directory':
        subprocess.Popen(r'explorer /open ' + OUTPUT_FILES_DIR)

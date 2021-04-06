import datetime
import os
import re
import subprocess

import PySimpleGUI as sg
import requests
from bs4 import BeautifulSoup

import consts as c

category_names = []
category_ids = []
# Kwork projects (orders).
parsed_projects = []

with open('CATEGORIES.dat', 'r') as cats:
    for line in cats:
        line = line.strip()
        cat_name, cat_id = line.rsplit(maxsplit=1)
        category_names.append(cat_name)
        category_ids.append(cat_id)


def scrape_category(cat_name: str, required_text, window: sg.Window):
    cat_index = category_names.index(cat_name)
    cat_code = category_ids[cat_index]
    status = scrape_page(f'{c.BASE_URL}?c={cat_code}', required_text, 1)
    window.refresh()
    while status['next_page_url']:
        status = scrape_page(
            status['next_page_url'], required_text, status['last_pr_num']
        )
    print('The category has been scraped.')


def scrape_page(url, required_text, last_pr_num):
    """Scrapes a page and returns scraping status."""
    print(c.MARGIN + 'scraping', url, end='\n\n')
    resp = requests.get(url)
    page_soup = BeautifulSoup(resp.text, 'html.parser')
    scraped_projects = page_soup.find_all('div', class_='want-card')
    for pr_num, prj in enumerate(scraped_projects, last_pr_num):
        scraped_prj = {}
        title = prj.find('div', class_=c.TITLE_CSS_CLASS).a.text
        scraped_prj[c.FIELD_NAMES[0]] = title

        description = prj.find('div', class_=c.DESC_CSS_CLASS)
        if not description:
            # When a description has no show/hide feature.
            description = prj.find('div', class_=c.SHORT_DESC_CSS_CLASS)

        anchors = description.find_all('a')
        description = re.sub(r'\n{2,}', '\n', description.text).strip()
        for anchor in anchors:
            anc_text = anchor.text.strip()
            anc_text_and_href = f'[{anc_text}] (< {anchor["href"]} >)'
            description = description.replace(anc_text, anc_text_and_href)
        scraped_prj[c.FIELD_NAMES[1]] = description
        # Project title or description should contain required text.
        if required_text and required_text not in title.lower() \
                and required_text not in description.lower():
            continue

        info = prj.find('div', class_=c.TIME_AND_OFFERS_CSS_CLASS)
        if c.TIME_AND_OFFERS_DELIM_CSS_CLASS in info.text:
            timeout, offers = info.text.split(c.TIME_AND_OFFERS_DELIM_CSS_CLASS)
        else:
            timeout = 'No data'
            offers = info.text
        timeout = timeout[timeout.find(' ') + 1:]
        offers = re.search(r'\d+', offers).group()
        scraped_prj[c.FIELD_NAMES[2]] = timeout
        scraped_prj[c.FIELD_NAMES[3]] = offers

        price = prj.find('div', class_=c.PRICE_CSS_CLASS).text
        price = re.search(r'\d[\d ]+', price).group()
        scraped_prj[c.FIELD_NAMES[4]] = price
        parsed_projects.append(scraped_prj)

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
    title = f'{c.MARGIN}№ {str(item_number)}: {fields[0][1].upper()}'
    desc = f'{c.MARGIN + fields[1][0]}:\n{fields[1][1]}'
    price = f'{c.MARGIN + fields[2][0]}: {fields[2][1]}'
    timeout = f'{c.MARGIN + fields[3][0]}: {fields[3][1]}'
    offers = f'{c.MARGIN + fields[4][0]}: {fields[4][1]}'
    text += '\n'.join((title, desc, price, timeout, offers))
    text += '\n'*3
    return text


def save_projects_to_file(cat_name):
    print(f'saving {cat_name}')
    f_name = os.path.join(c.OUTPUT_FILES_DIR, f'{cat_name}_scraped_data.txt')
    with open(f_name, 'w', encoding='utf-8') as out_file:
        for project in print_projects_of_cat_as_texts(cat_name, parsed_projects):
            out_file.write(project)


def print_projects_of_cat_as_texts(cat_name, projects):
    yield get_scraping_title(cat_name)
    for item_number, project in enumerate(projects, 1):
        yield get_project_as_text(project, item_number)


def get_scraping_title(cat_name):
    date = datetime.datetime.now()
    return f'{c.MARGIN}Projects at "{cat_name}" scraped on {date}\n\n'


sg.theme(c.USED_THEME)
prjs_out = sg.Output(size=(160, 30))
buttons = [
    sg.Button(c.SCRAPE_PRJCTS_BTN_NM),
    sg.Button(c.SAVE_PRJCTS_BTN_NM),
    sg.Button(c.OPEN_SAVED_PRJCTS_BTN_NM),
    sg.Button(c.CLOSE_PROGRAM_BTN_NM),
]
layout = [
    [
        sg.Text('Select category:'),
        sg.Combo(category_names, key=c.CAT_COMBO_KEY, default_value=category_names[0]),
        sg.Text('Project must contain text:'), sg.Input(key=c.REQUIRED_TEXT_INPUT_KEY)
    ],
    [*buttons],
    [sg.Text('Projects in the category:')],
    [prjs_out],
]
window = sg.Window(
    'Kwork Scraper', layout, resizable=True, size=(1200, 600),
    finalize=True
)
window.Maximize()
prjs_out.expand(expand_x=True, expand_y=True)
for btn in buttons:
    btn.set_cursor('hand2')

# Event loop.
while True:
    event, values = window.read()
    # Stop loop when user closes window or clicks c.CLOSE_PROGRAM_BTN_NM button.
    if event in (None, c.CLOSE_PROGRAM_BTN_NM):
        break
    if event == c.SCRAPE_PRJCTS_BTN_NM:
        prjs_out.update(get_scraping_title(values[c.CAT_COMBO_KEY]))
        date = datetime.datetime.now()
        parsed_projects.clear()
        scrape_category(values[c.CAT_COMBO_KEY], values[c.REQUIRED_TEXT_INPUT_KEY].lower(), window)
    elif event == c.SAVE_PRJCTS_BTN_NM:
        if not parsed_projects:
            sg.popup_error('Nothing to save yet.')
        else:
            save_projects_to_file(values[c.CAT_COMBO_KEY])
    elif event == c.OPEN_SAVED_PRJCTS_BTN_NM:
        subprocess.Popen(r'explorer /open ' + c.OUTPUT_FILES_DIR)

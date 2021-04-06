import requests
from bs4 import BeautifulSoup

import category_controller as cat_contr
import consts as c
import kw_project_controller as prj_contr
import kw_project_formatter as prj_fmt
import ui_controller as ui_contr
from kw_project_parser import parse_project


def scrape_category(cat_name: str, required_text):
    cat_index = cat_contr.category_names.index(cat_name)
    cat_code = cat_contr.category_ids[cat_index]
    status = scrape_page(f'{c.BASE_URL}?c={cat_code}', required_text, 1)
    ui_contr.refresh()
    while status['next_page_url']:
        status = scrape_page(
            status['next_page_url'], required_text,
            status['last_pr_num']
        )
    print('The category has been scraped.')


def scrape_page(url, required_text, last_prj_num):
    """Scrapes a page and returns scraping status."""
    print(c.MARGIN + 'scraping', url, end='\n\n')
    resp = requests.get(url)
    page_soup = BeautifulSoup(resp.text, 'html.parser')
    scraped_projects = page_soup.find_all('div', class_='want-card')
    for prj_num, prj_div in enumerate(scraped_projects, last_prj_num):
        parsed_prj = parse_project(prj_div, required_text)
        if parsed_prj:
            prj_contr.parsed_projects.append(parsed_prj)
            print(prj_fmt.get_project_as_text(parsed_prj, prj_num))
            ui_contr.refresh()

    next_page_anchor = page_soup.find('a', class_='next')
    if next_page_anchor:
        next_page_url = next_page_anchor['href']
    else:
        next_page_url = None
    return {
        'next_page_url': next_page_url,
        'last_pr_num': prj_num
    }

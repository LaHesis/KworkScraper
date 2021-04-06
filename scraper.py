import PySimpleGUI as sg
import requests
from bs4 import BeautifulSoup

import category_controller as cat_contr
import consts as c
import kw_project_formatter as prj_fmt
import kw_project_controller as prj_contr
from kw_project_parser import parse_project


def scrape_category(cat_name: str, required_text, window: sg.Window):
    cat_index = cat_contr.category_names.index(cat_name)
    cat_code = cat_contr.category_ids[cat_index]
    status = scrape_page(f'{c.BASE_URL}?c={cat_code}', required_text, 1)
    window.refresh()
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
            window.refresh()

    next_page_anchor = page_soup.find('a', class_='next')
    if next_page_anchor:
        next_page_url = next_page_anchor['href']
    else:
        next_page_url = None
    return {
        'next_page_url': next_page_url,
        'last_pr_num': prj_num
    }


def create_UI_window_and_output():
    sg.theme(c.USED_THEME)
    app_output = sg.Output(size=(160, 30))
    buttons = [
        sg.Button(c.SCRAPE_PRJCTS_BTN_NM),
        sg.Button(c.SAVE_PRJCTS_BTN_NM),
        sg.Button(c.OPEN_SAVED_PRJCTS_BTN_NM),
        sg.Button(c.CLOSE_PROGRAM_BTN_NM),
    ]
    category_selector = sg.Combo(
        cat_contr.category_names,
        key=c.CAT_COMBO_KEY,
        default_value=cat_contr.category_names[0]
    )
    layout = [
        [
            sg.Text('Select category:'),
            category_selector,
            sg.Text('Project must contain text:'),
            sg.Input(key=c.REQUIRED_TEXT_INPUT_KEY)
        ],
        [*buttons],
        [sg.Text('Projects in the category:')],
        [app_output],
    ]
    window = sg.Window(
        'Kwork Scraper', layout, resizable=True, size=(1200, 600),
        finalize=True
    )
    window.Maximize()
    app_output.expand(expand_x=True, expand_y=True)
    for btn in buttons:
        btn.set_cursor('hand2')
    return window, app_output


if __name__ == '__main__':
    window, app_output = create_UI_window_and_output()
    # Event loop.
    while True:
        event, values = window.read()
        # Stop loop when user closes window or clicks c.CLOSE_PROGRAM_BTN_NM
        # button.
        if event in (None, c.CLOSE_PROGRAM_BTN_NM):
            break
        if event == c.SCRAPE_PRJCTS_BTN_NM:
            # Show scraping title in output.
            selected_category_nm = values[c.CAT_COMBO_KEY]
            app_output.update(prj_fmt.get_scraping_title(selected_category_nm))
            # Remove previously scraped project.
            prj_contr.parsed_projects.clear()
            required_text = values[c.REQUIRED_TEXT_INPUT_KEY].lower()
            scrape_category(selected_category_nm, required_text, window)
        elif event == c.SAVE_PRJCTS_BTN_NM:
            if not prj_contr.parsed_projects:
                sg.popup_error('Nothing to save yet.')
            else:
                prj_contr.save_projects_to_file(selected_category_nm)
        elif event == c.OPEN_SAVED_PRJCTS_BTN_NM:
            prj_contr.show_output_dir_in_explorer()

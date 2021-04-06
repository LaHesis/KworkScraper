import datetime

import consts as c


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


def format_projects(cat_name, projects):
    yield get_scraping_title(cat_name)
    for item_number, project in enumerate(projects, 1):
        yield get_project_as_text(project, item_number)


def get_scraping_title(cat_name):
    date = datetime.datetime.now()
    return f'{c.MARGIN}Projects at "{cat_name}" scraped on {date}\n\n'

import os
import webbrowser

import consts as c
import kw_project_formatter as prj_fmr


def save_projects_to_file(cat_name):
    print(f'saving {cat_name}')
    f_name = os.path.join(c.OUTPUT_FILES_DIR, f'{cat_name}_scraped_data.txt')
    with open(f_name, 'w', encoding='utf-8') as out_file:
        formatted_projects = prj_fmr.format_projects(cat_name, parsed_projects)
        for project in formatted_projects:
            out_file.write(project)


def show_output_dir_in_explorer():
    webbrowser.open('file:///' + path_to_save)


# Kwork projects (orders).
parsed_projects = []
cur_dir = os.path.dirname(os.path.abspath(__file__))
path_to_save = os.path.join(cur_dir, c.OUTPUT_FILES_DIR)

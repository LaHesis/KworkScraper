import consts as c
import kw_project_controller as prj_contr
import kw_project_formatter as prj_fmt
import scraper
import ui_controller as ui_contr

if __name__ == '__main__':
    # Event loop.
    while True:
        event, values = ui_contr.window.read()
        # Stop loop when user closes window or clicks c.CLOSE_PROGRAM_BTN_NM
        # button.
        if event in (None, c.CLOSE_PROGRAM_BTN_NM):
            break
        if event == c.SCRAPE_PRJCTS_BTN_NM:
            # Show scraping title in output.
            selected_categ_nm = values[c.CAT_COMBO_KEY]
            scr_title = prj_fmt.get_scraping_title(selected_categ_nm)
            ui_contr.app_output.update(scr_title)
            # Remove previously scraped project.
            prj_contr.parsed_projects.clear()
            required_text = values[c.REQUIRED_TEXT_INPUT_KEY].lower()
            scraper.scrape_category(selected_categ_nm, required_text)
        elif event == c.SAVE_PRJCTS_BTN_NM:
            if not prj_contr.parsed_projects:
                ui_contr.message_saying_nothing_to_save()
            else:
                prj_contr.save_projects_to_file(selected_categ_nm)
        elif event == c.OPEN_SAVED_PRJCTS_BTN_NM:
            prj_contr.show_output_dir_in_explorer()

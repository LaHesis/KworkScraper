import PySimpleGUI as sg

# It is imported by other modules then.
import category_controller as cat_contr
import consts as c


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


def message_saying_nothing_to_save():
    sg.popup_error('Nothing to save yet.')


def refresh():
    window.refresh()


window, app_output = create_UI_window_and_output()

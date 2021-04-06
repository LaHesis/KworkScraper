MARGIN = ' '*25
NO_DATA = '-'
TASKS_AT_ONE_PAGE = 12
BASE_URL = 'https://kwork.ru/projects'
OUTPUT_FILES_DIR = 'output'

# CSS classes used to find HTML elements having project (order) info.
# This class is used when a description is partial with show/hide feature.
DESC_CSS_CLASS = 'js-want-block-toggle-full'
TITLE_CSS_CLASS = 'wants-card__header-title'
SHORT_DESC_CSS_CLASS = 'wants-card__description-text'
TIME_AND_OFFERS_CSS_CLASS = 'query-item__info'
TIME_AND_OFFERS_DELIM_CSS_CLASS = ' \xa0\xa0\xa0'
PRICE_CSS_CLASS = 'wants-card__header-price'

# Their order is very important. Data rows are being added in the same order.
FIELD_NAMES = [
    'TITLE',
    'DESCRIPTION',
    'TIMEOUT',
    'OFFERS',
    'PRICE_UP_TO',
]

USED_THEME = 'LightGreen1'
SCRAPE_PRJCTS_BTN_NM = 'Scrape projects'
SAVE_PRJCTS_BTN_NM = 'Save scraped projects to file'
OPEN_SAVED_PRJCTS_BTN_NM = 'Open saved files directory'
CLOSE_PROGRAM_BTN_NM = 'Exit'
CAT_COMBO_KEY = 'category'
REQUIRED_TEXT_INPUT_KEY = 'required_text'

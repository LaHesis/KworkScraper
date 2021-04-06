import re

import consts as c


def parse_project(prj_div, required_text):
    parsed_prj = {}
    title = _parse_title(prj_div)
    parsed_prj[c.FIELD_NAMES[0]] = title
    description = _parse_prj_desc(prj_div)
    description = _replace_links_in_desc(description)
    parsed_prj[c.FIELD_NAMES[1]] = description
    # Project title or description should contain required text.
    if required_text and required_text not in title.lower() \
            and required_text not in description.lower():
        return False
    info = prj_div.find('div', class_=c.TIME_AND_OFFERS_CSS_CLASS)
    timeout, offers = _parse_timeout_and_offers(info)
    parsed_prj[c.FIELD_NAMES[2]] = timeout
    parsed_prj[c.FIELD_NAMES[3]] = offers
    parsed_prj[c.FIELD_NAMES[4]] = _parse_price(prj_div)
    return parsed_prj


def _parse_timeout_and_offers(info_div):
    if c.TIME_AND_OFFERS_DELIM in info_div.text:
        timeout, offers = info_div.text.split(c.TIME_AND_OFFERS_DELIM)
    else:
        timeout = 'No data'
        offers = info_div.text
    timeout = timeout[timeout.find(' ') + 1:]
    offers = re.search(r'\d+', offers).group()
    return timeout, offers


def _parse_prj_desc(prj_div):
    description = prj_div.find('div', class_=c.DESC_CSS_CLASS)
    if not description:
        # When a description has no show/hide feature.
        description = prj_div.find('div', class_=c.SHORT_DESC_CSS_CLASS)
    return description


def _replace_links_in_desc(description):
    anchors = description.find_all('a')
    description = re.sub(r'\n{2,}', '\n', description.text).strip()
    for anchor in anchors:
        anc_text = anchor.text.strip()
        anc_text_and_href = f'[{anc_text}] (< {anchor["href"]} >)'
        description = description.replace(anc_text, anc_text_and_href)
    return description


def _parse_price(prj_div):
    price = prj_div.find('div', class_=c.PRICE_CSS_CLASS).text
    price = re.search(r'\d[\d ]+', price).group()
    return price


def _parse_title(prj_div):
    title_div = prj_div.find('div', class_=c.TITLE_CSS_CLASS)
    return title_div.a.text

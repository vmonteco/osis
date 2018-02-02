from PIL._imaging import draw
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pyvirtualdisplay
from selenium.webdriver.support.ui import Select


# !/usr/bin/env python
import random

from selenium import webdriver
from selenium.webdriver.support.ui import Select

import pyvirtualdisplay


def fill_by_id(driver, element_id, value):
    element = driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(value)


def click_on(driver, element_id):
    element = driver.find_element_by_id(element_id)
    element.click()


display = pyvirtualdisplay.Display(size=(1920, 1080))
# Ne pas lancer le navigateur web
# display.start()

driver = webdriver.Chrome()
# driver = webdriver.Firefox()
driver.implicitly_wait(5)
driver.set_window_size(1920, 1080)
values_justification  = {'T': 'Tricherie', 'A': 'Absence injustifiée'}

try:
    driver.get('http://localhost:8000')
    fill_by_id(driver, 'id_username', 'user0')
    fill_by_id(driver, 'id_password', 'password123')

    click_on(driver, 'post_login_btn')

    click_on(driver, 'lnk_home_studies')
    click_on(driver, 'lnk_assessments')
    click_on(driver, 'lnk_score_encoding')

    # elements = driver.find_elements_by_css_selector(
    #     '#pnl_learning_units #tab_online table tbody tr'
    # )
    # first_element = elements[0]

    row = driver.find_element_by_css_selector(
        '#pnl_learning_units #tab_online table tbody tr:nth-child(1)'
    )

    learning_unit_sigle = row.find_element_by_css_selector('td:nth-child(2)').text
    learning_unit_name = row.find_element_by_css_selector('td:nth-child(3)').text

    print(learning_unit_sigle)
    print(learning_unit_name)

    learning_unit_link = row.find_element_by_css_selector('td:nth-child(3) a')
    learning_unit_link.click()

    encoding_link = driver.find_element_by_id('lnk_encode')
    encoding_link.click()

    # for row in driver.find_elements_by_css_selector('#form_online_encoding table tbody tr'):
    elements = driver.find_elements_by_css_selector('#form_online_encoding table tbody tr')
    nb_exam_enrollments = len(elements)
    for counter in range(0, nb_exam_enrollments):
        # row = driver.find_element_by_css_selector('#form_online_encoding table tbody tr:nth-child(1)')
        # offer = row.find_element_by_css_selector('td:nth-child(2)').text
        # noma = row.find_element_by_css_selector('td:nth-child(3)').text
        # first_name = row.find_element_by_css_selector('td:nth-child(4)').text
        # last_name = row.find_element_by_css_selector('td:nth-child(5)').text
        row = elements[counter]
        offer = row.find_element_by_css_selector('td:nth-child(2)').text
        noma = row.find_element_by_css_selector('td:nth-child(3)').text
        first_name = row.find_element_by_css_selector('td:nth-child(4)').text
        last_name = row.find_element_by_css_selector('td:nth-child(5)').text

        print(offer, noma, first_name, last_name)

        if random.getrandbits(1):
            score_element = row.find_element_by_css_selector('td:nth-child(6) input')
            score_element.clear()
            score_element.send_keys(random.randrange(0, 21))
        else:
            justification_element = row.find_element_by_css_selector('td:nth-child(7) select')
            select = Select(justification_element)
            selected = 'T' if random.getrandbits(1) else 'A'
            value = values_justification.get(selected)
            select.select_by_visible_text(value)

    # driver.execute_script("scroll(0, 250)")
    driver.execute_script("scroll(0, document.body.scrollHeight)")
    click_on(driver, 'bt_save_online_encoding_down')

    progression = driver.find_element_by_id('luy_progression').text
    prog_min, prog_max = [int(p) for p in progression.split('/')]
    print('progression: {}/{}'.format(prog_min, prog_max))

    element = driver.find_element_by_css_selector(
        'div.panel.panel-default div.panel-body .row div.col-md-3:nth-child(4)'
    )
    nombre_inscrits = int(element.text.split('\n')[-1])
    print('nombre_inscrits: {}'.format(nombre_inscrits))

    assert prog_max == nombre_inscrits

    learning_unit_name = driver.find_element_by_class_name('panel-title').text.rsplit(' - ')[-1]

    first_row = driver.find_element_by_css_selector('div.panel-body table tbody tr:nth-child(1)')

    offer = first_row.find_element_by_css_selector('td:nth-child(2)').text
    noma = first_row.find_element_by_css_selector('td:nth-child(3)').text
    last_name = first_row.find_element_by_css_selector('td:nth-child(4)').text
    first_name = first_row.find_element_by_css_selector('td:nth-child(5)').text

    note = first_row.find_element_by_css_selector('td:nth-child(6)').text
    justification = first_row.find_element_by_css_selector('td:nth-child(7)').text

    print(learning_unit_name, offer, noma, first_name, last_name, note, justification)

    click_on(driver, 'lnk_scores_encoding')
    click_on(driver, 'lnk_justifications')

    fill_by_id(driver, 'txt_registration_id', noma)
    click_on(driver, 'bt_submit_offer_year_search')

    for row in driver.find_elements_by_css_selector('#tab_justifications #form_justification table tbody tr'):
        l_program = row.find_element_by_css_selector('td:nth-child(2)').text
        l_luy_name = row.find_element_by_css_selector('td:nth-child(3)').text.split(' - ')[0]
        l_noma = row.find_element_by_css_selector('td:nth-child(4)').text
        l_note = row.find_element_by_css_selector('td:nth-child(7) input').get_attribute('value')
        l_justification = Select(row.find_element_by_css_selector('td:nth-child(8) select')).first_selected_option.text

        print(l_luy_name, l_program, l_noma, l_note, l_justification)

        if l_noma == noma and l_luy_name == learning_unit_name and l_program == offer:
            print("matching")
            assert l_note == note or l_justification == justification

    fill_by_id(driver, 'txt_registration_id', '')
    fill_by_id(driver, 'txt_last_name', last_name)
    click_on(driver, 'bt_submit_offer_year_search')

    for row in driver.find_elements_by_css_selector('#tab_justifications #form_justification table tbody tr'):
        l_program = row.find_element_by_css_selector('td:nth-child(2)').text
        l_luy_name = row.find_element_by_css_selector('td:nth-child(3)').text.split(' - ')[0]
        l_noma = row.find_element_by_css_selector('td:nth-child(4)').text
        l_note = row.find_element_by_css_selector('td:nth-child(7) input').get_attribute('value')
        l_justification = Select(row.find_element_by_css_selector('td:nth-child(8) select')).first_selected_option.text

        print(l_luy_name, l_program, l_noma, l_note, l_justification)

        if l_noma == noma and l_luy_name == learning_unit_name and l_program == offer:
            print("matching")
            assert l_note == note or l_justification == justification

    select = Select(driver.find_element_by_id('slt_justification'))
    select.select_by_visible_text(justification)

    fill_by_id(driver, 'txt_last_name', '')
    click_on(driver, 'bt_submit_offer_year_search')

    for row in driver.find_elements_by_css_selector('#tab_justifications #form_justification table tbody tr'):
        l_program = row.find_element_by_css_selector('td:nth-child(2)').text
        l_luy_name = row.find_element_by_css_selector('td:nth-child(3)').text.split(' - ')[0]
        l_noma = row.find_element_by_css_selector('td:nth-child(4)').text
        l_note = row.find_element_by_css_selector('td:nth-child(7) input').get_attribute('value')
        l_justification = Select(row.find_element_by_css_selector('td:nth-child(8) select')).first_selected_option.text

        print(l_luy_name, l_program, l_noma, l_note, l_justification)

        if l_noma == noma and l_luy_name == learning_unit_name and l_program == offer:
            print("matching")
            assert l_note == note or l_justification == justification

    # lance le mode debug
    # import pdb; pdb.set_trace()
    # print('salut')


finally:
    driver.close()
    driver.quit()
    # display.stop()

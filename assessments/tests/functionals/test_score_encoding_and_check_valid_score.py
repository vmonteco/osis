from PIL._imaging import draw
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pyvirtualdisplay
from selenium.webdriver.support.ui import Select
from random import *


user_name = 'username_0'
password = 'password123'
url = 'http://localhost:8000'
possible_values_justification  = {'T': 'Tricherie', 'A': 'Absence injustifiée'}

def put_value_in_inputField(element, value):
    element.clear()
    element.send_keys(value)


def open_browser_and_log_on_user(url, user_name, password):
    driver = webdriver.Chrome()  #Firefox()
    driver.get(url)
    assert 'OSIS' in driver.title
    element = driver.find_element_by_id('id_username')
    put_value_in_inputField(element, user_name)
    element = driver.find_element_by_id('id_password')
    put_value_in_inputField(element, password)
    return driver


def clic_on_button(driver, buttonId):
    element = driver.find_element_by_id(buttonId)
    element.click()


def select_value_in_select_options(driver, id_element, value):
    select = Select(driver.find_element_by_id(id_element))
    select.select_by_visible_text(value)


def select_element_by_css(driver, css, sigle_cours, num_column):
    for row in driver.find_elements_by_css_selector(css):
        sigle = row.find_element_by_css_selector('td:nth-child({})'.format(num_column)).text
        if sigle == sigle_cours:
            element_buton = row.find_element_by_css_selector('td:nth-child(6)  a')
            element_buton.click()
            #index = int(sigle.split('-')[-1]) + 1;
            #clic_on_button(driver, 'lnk_encode_{}'.format(index))
            #clic_on_button(driver, element_buton)
            # assert driver.find_element_by_id('bt_save_online_encoding_up')
            break


def encode_scores(driver, css,decimal_score_auth):
    encoded_scores = {}
    encoded_justifications ={}
    score_decimal =False
    for row in driver.find_elements_by_css_selector(css):
        noma = row.find_element_by_css_selector('td:nth-child({})'.format(3)).text
        input_field = row.find_element_by_css_selector('td:nth-child({}) input'.format(6))
        score = randint(0, 20)
        #pour pouvoir verifier que l'information n'a pas été encodée : voir affichage
        encoded_justifications[noma] = '-'
        encoded_scores[noma]='-'
        if(decimal_score_auth and score %  3 == 0):
           encoded_scores[noma] = "%.1f" % uniform(0, 20)
           score_decimal = True
        elif (score %  7 == 0) :
            key = 'T' if (score % 2) == 0 else 'A'
            value_justification = possible_values_justification.get(key)
            justification_element = row.find_element_by_css_selector('td:nth-child({}) select'.format(7))
            select_field = Select(justification_element)
            select_field.select_by_visible_text(value_justification)
            encoded_justifications[noma] = value_justification
        else:
            encoded_scores[noma] = score

        if(encoded_scores.get(noma) != '-'):
            put_value_in_inputField(input_field,encoded_scores.get(noma))
    driver.execute_script("scroll(0, 250)")
    #driver.execute_script("scroll(0, document.body.scrollHeight)")
    id_element_button_save = 'bt_save_online_encoding_up'
    element_button_save = driver.find_element_by_id(id_element_button_save)
    if(decimal_score_auth == False):
        assert score_decimal == False and element_button_save.is_enabled()

    print('Encoding OK')
    clic_on_button(driver,id_element_button_save)

    element_table_css = 'body  div:nth-child(4)  div.panel.panel-default  div.panel-body  table  tbody  tr'

    for row in driver.find_elements_by_css_selector(element_table_css):
        noma = row.find_element_by_css_selector('td:nth-child({})'.format(3)).text
        score_saved = row.find_element_by_css_selector('td:nth-child({})'.format(6)).text
        justification_saved = row.find_element_by_css_selector('td:nth-child({})'.format(7)).text
        assert str(encoded_scores.get(noma)) == str(score_saved) and encoded_justifications.get(noma) ==justification_saved


display = pyvirtualdisplay.Display(size=(1920, 1080))
# Ne pas lancer le navigateur web
# display.start()

driver = open_browser_and_log_on_user(url, user_name, password)
driver.implicitly_wait(5)
driver.set_window_size(1920, 1080)

try:
    clic_on_button(driver, 'post_login_btn')
    clic_on_button(driver, 'lnk_home_studies')
    clic_on_button(driver, 'lnk_assessments')
    clic_on_button(driver, 'lnk_score_encoding')
    driver.implicitly_wait(5)
    select_value_in_select_options(driver, 'slt_offer_list_selection', 'ECON2M1')
    clic_on_button(driver, 'bt_submit_offer_search')
    driver.implicitly_wait(8)
    select_element_by_css(driver, '#pnl_learning_units #tab_online table tbody tr', 'LUY-13', 2)
    element_info = driver.find_element_by_css_selector('body.localmode div.container div.panel.panel-default div.panel-body div.alert.alert-info').text
    decimal_score_auth = element_info != 'Les notes de ce cours ne peuvent PAS recevoir de valeurs décimales.'
    # on commence à encoder
    css_table_form = '#form_online_encoding table tbody tr'
    encode_scores(driver, css_table_form, decimal_score_auth)
    element_progress_bar_css = 'body div:nth-child(4)  div.panel.panel-default  div.panel-body  div.form-group  div  div span b'
    element_progress_bar = driver.find_elements_by_css_selector(element_progress_bar_css)
    #print(element_progress_bar)



finally:
    driver.implicitly_wait(20)
     #driver.close()
     #driver.quit()


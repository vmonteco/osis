import pdb
from behave import given, when, then
from django.utils.text import slugify
from selenium.common.exceptions import NoSuchElementException
from django.contrib.auth.models import User

@given('Je suis sur la page "{page_name}"')
def step(context, page_name):
    assert context.browser.find_element_by_tag_name('h2').text == page_name

@given('Je click sur la page "{page_name}"')
def step(context, page_name):
    context.browser.find_element_by_link_text(page_name).click()
    if page_name == 'Profile':
        assert context.browser.current_url.endswith('/my_osis/profile/')
    elif page_name == 'Messages':
        assert context.browser.current_url.endswith('/my_osis/my_messages/')

@then('Je vais sur la page "{page_name}"')
@given('Je vais sur la page "{page_name}"')
def step(context, page_name):
    pdb.set_trace()
    if page_name == 'Profile':
        context.browser.get(context.get_url('my_osis'))
    elif page_name == 'Messages':
        context.browser.get(context.get_url('my_messages'))
    else:
        raise Exception("Page not managed")

@then('Je vois {count_of_tabulations:d} onglets')
def step(context, count_of_tabulations):
    assert isinstance(count_of_tabulations, int)
    items = context.browser.find_elements_by_css_selector('ul.nav-tabs > li')
    assert len(items) == count_of_tabulations

@then('Onglet {number_of_tabulation:d} avec "{tabulation_name}"')
def step(context, number_of_tabulation, tabulation_name):
    items = context.browser.find_elements_by_css_selector('ul.nav-tabs > li')
    if len(items) < number_of_tabulation:
        raise Exception("Could you check your pattern")
    # try:
    item = items[number_of_tabulation-1].find_element_by_link_text(tabulation_name)

@given('Je selectionne l\'onglet "{tabulation_name}"')
def step(context, tabulation_name):
    try:
        item = context.browser.find_element_by_link_text(tabulation_name)
        item.click()
    except Exception as ex:
        pdb.post_mortem()

@then('Je vois "{value}" comme titre')
def step(context, value):
    assert context.browser.find_element_by_id('person_name').text == value

@then('Je vois les champs suivants avec leur valeur')
def step(context):
    for field_name, value in context.table:
        element = context.browser.find_element_by_id(field_name)
        assert element.text == value

@given('Je vais dans la page d\'administration "{admin_path}"')
def step(context, admin_path):
    context.browser.get(context.get_url(admin_path))

@then('J\'ajoute une personne')
def step(context):
    pass
    # import pdb; pdb.set_trace()
    # driver = context.browser
    # driver.find_element_by_id('id_user').send_keys('1')
    # driver.find_element_by_id('id_first_name').send_keys('Stephane')
    # driver.find_element_by_id('id_last_name').send_keys('Wirtel')
    # driver.find_element_by_xpath('//input[@type="submit" and @name="_continue"]').click()

@then('La langue est "{language}"')
def step(context, language):
    driver = context.browser
    driver.find_element_by_id('slt_ui_language').find_element_by_xpath('option[@selected]').text == language


@then('Je vais dans "{section_name}"')
@given('Je vais dans "{section_name}"')
def step(context, section_name):
    driver = context.browser
    # pdb.set_trace()
    # original_section_name = section_name
    section_name = section_name.lower()

    if section_name == 'institution':
        driver.find_element_by_id('lnk_home_institution').click()
    elif section_name == 'my osis':
        driver.get(context.get_url('my_osis'))
    else:
        raise Exception('unmanaged')

    scenario_name = slugify(context.scenario.name)
    section_name = slugify(section_name)
    filename = '%s-%s.%s' % (scenario_name, section_name, 'png')

    driver.save_screenshot(filename.lower())

@then('Il y a "{section_name}"')
def step(context, section_name):
    driver = context.browser
    found = False
    try:
        driver.find_element_by_link_text(section_name)
        found = True
    except NoSuchElementException as ex:
        pdb.post_mortem()

    assert found

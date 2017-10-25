import pdb
from behave import given, when, then
from selenium.common.exceptions import NoSuchElementException
from django.contrib.auth.models import User

@given('User "{username}"/"{password}" créé')
def step(context, username, password):
    user = User.objects.filter(username=username).first()
    if not user:
        User.objects.create_user(username=username, password=password)


def has_loging_errors(driver):
    try:
        driver.find_element_by_id('login-errors')
        return True
    except NoSuchElementException:
        return False

@given('Je me connecte avec "{username}"/"{password}"')
@then('Je me connecte avec "{username}"/"{password}"')
def step(context, username, password):
    driver = context.browser
    driver.get(context.get_url())
    driver.find_element_by_id('id_username').send_keys(username)
    driver.find_element_by_id('id_password').send_keys(password)
    # driver.find_element_by_xpath('//input[@type="submit" and @value="Log-in"]').click()
    driver.find_element_by_id('id_password').submit()

    # if has_loging_errors(driver):
    #     raise AssertionError("Can't connect to the server")
    # driver.find_element_by_id('login-errors')
    # pdb.set_trace()



@then('Je vois l\'option Logout')
def step_impl(context):
    context.browser.save_screenshot('/tmp/demo.png')
    try:
        context.browser.find_element_by_id('lnk_logout')
    except Exception as ex:
        pdb.post_mortem()


@then('Je me deconnecte')
def step_impl(context):
    driver = context.browser
    try:
        item = driver.find_element_by_id('id_username')
    except NoSuchElementException:
        driver.get(context.get_url() + '/logged_out/')
        driver.find_element_by_id('redirect_to_login').click()


@then('J\'ai le message "{message}"')
def step_impl(context, message):
    driver = context.browser
    p_tag = driver.find_element_by_xpath('//p[@class="text-danger"]')
    # pdb.set_trace()
    assert p_tag.text == message

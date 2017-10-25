import logging
import pdb
from selenium import webdriver

BEHAVE_DEBUG_ON_ERROR = False


def setup_debug_on_error(userdata):
    global BEHAVE_DEBUG_ON_ERROR
    BEHAVE_DEBUG_ON_ERROR = userdata.getbool("BEHAVE_DEBUG_ON_ERROR")


def before_all(context):
    # from pyvirtualdisplay import Display
    # display = Display(visible=0, size=(1280, 1024))
    # context.display = display

    # display.start()

    if not context.config.log_capture:
        logging.basicConfig(level=logging.DEBUG)

    setup_debug_on_error(context.config.userdata)

    # browser = webdriver.Chrome()
    browser = webdriver.Firefox()
    # browser.implicitly_wait(10)
    browser.set_window_size(1280, 1024)
    context.browser = browser


def after_all(context):
    context.browser.quit()
    # context.display.stop()

def after_step(context, step):
    if BEHAVE_DEBUG_ON_ERROR and step.status == 'failed':
        pdb.post_mortem(step.exc_traceback)

def before_feature(context, feature):
    print(feature.name)

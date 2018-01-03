import logging

import pyvirtualdisplay
from selenium import webdriver

from base.tests.factories.academic_calendar import AcademicCalendarFactory

BEHAVE_DEBUG_ON_ERROR = False
SIZE = (1280, 1024)


def setup_debug_on_error(userdata):
    global BEHAVE_DEBUG_ON_ERROR
    BEHAVE_DEBUG_ON_ERROR = userdata.getbool('behave_debug_on_error')



def before_all(context):
    if not context.config.log_capture:
        logging.basicConfig(level=logging.DEBUG)

    display = pyvirtualdisplay.Display(visible=0, size=SIZE)
    context.display = display
    # display.start()

    setup_debug_on_error(context.config.userdata)

    driver = webdriver.Chrome()
    driver.set_window_size(*SIZE)
    context.driver = driver


def after_all(context):
    context.driver.quit()
    # context.display.stop()


def after_step(context, step):
    if BEHAVE_DEBUG_ON_ERROR and step.status == 'failed':
        import pdb
        pdb.post_mortem(step.exc_traceback)


def before_scenario(context, scenario):
    pass


def after_scenario(context, scenario):
    pass


def before_feature(context, feature):
    from base.tests.factories.user import UserFactory

    user = UserFactory()

    from base.tests.factories.academic_year import AcademicYearFactory

    academic_year = AcademicYearFactory()

    academic_calendar = AcademicCalendarFactory.build(academic_year=academic_year)
    academic_calendar.save(functions=[])

    print(feature.name)
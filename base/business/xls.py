##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from collections import OrderedDict

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from attribution.models import attribution
from base import models as mdl_base
from base.business.entity import get_entity_calendar
from base.business.learning_unit_year_with_context import volume_learning_component_year
from base.models import entity_container_year
from base.models import learning_achievement
from base.models.academic_year import find_academic_year_by_year
from base.models.entity_component_year import EntityComponentYear
from base.models.enums import entity_container_year_link_type, academic_calendar_type
from cms import models as mdl_cms
from cms.enums import entity_name
from cms.enums.entity_name import LEARNING_UNIT_YEAR
from cms.models import translated_text
from osis_common.document import xls_build
from osis_common.utils.datetime import convert_date_to_datetime


def get_name_or_username(a_user):
    person = mdl_base.person.find_by_user(a_user)
    return "{}, {}".format(person.last_name, person.first_name) if person else a_user.username
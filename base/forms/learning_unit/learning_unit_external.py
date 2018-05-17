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
from abc import ABCMeta
from collections import OrderedDict

from django.db import transaction
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from base.business.utils.model import merge_two_dicts
from base.forms.learning_unit.learning_unit_create import LearningUnitModelForm, LearningUnitYearModelForm, \
    LearningContainerModelForm, LearningContainerYearModelForm, EntityContainerBaseForm
from base.forms.utils.acronym_field import split_acronym
from base.models import learning_unit_year
from base.models.campus import Campus
from base.models.enums import learning_unit_year_subtypes
from base.models.learning_unit import LearningUnit
from reference.models import language
from base.models.enums import learning_container_year_types
from base.models import academic_year


class LearningUnitExternalForm:
    learning_unit_instance = None
    subtype = None
    person = None
    _forms_to_upsert = []

    def __init__(self, person, start_postponement, end_postponement=None, data=None, check_consistency=True):

        self.start_postponement = start_postponement
        self.person = person
        self.check_consistency = check_consistency
        self.end_postponement = end_postponement
        self._init_forms(data)

    def _init_forms(self, data=None):
        """This function will init two forms var:
           forms_to_upsert: LearningUnitBaseForm which must be created/updated
           forms_to_delete: LearningUnitBaseForm which must be deleted
        """

        # Creation case
        start_year = self.start_postponement.year
        end_year = self.end_postponement.year if self.end_postponement else None
        self._forms_to_upsert = self._get_forms_to_insert(start_year, end_year, data)


    def _get_forms_to_insert(self, start_insert_year, end_year=None, data=None):
        luy_base_form_insert = []
        max_postponement_year = academic_year.compute_max_academic_year_adjournment()
        end_year = min(end_year,  max_postponement_year) if end_year else max_postponement_year

        if start_insert_year <= end_year:
            ac_years = academic_year.find_academic_years(start_year=start_insert_year, end_year=end_year)
            luy_base_form_insert = [self._get_learning_unit_base_form(ac_year, data=data, start_year=start_insert_year)
                                    for ac_year in ac_years]

        return luy_base_form_insert
##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from copy import deepcopy

from base.forms.learning_unit.learning_unit_create import LearningUnitYearModelForm, LearningUnitModelForm
from base.forms.learning_unit.learning_unit_create_2 import LearningUnitBaseForm, PartimForm, FullForm
from base.models import academic_year
from base.models import learning_unit_year
from base.models.enums import learning_unit_year_subtypes


class LearningUnitPostponementForm:
    instance = None
    person = None
    check_consistency = True
    _forms_to_upsert = []
    _forms_to_delete = []

    def __init__(self, instance, person, check_consistency=True):
        if instance and not isinstance(instance, LearningUnitBaseForm):
            raise AttributeError('instance arg should be an instance of {}'.format(LearningUnitBaseForm))
        self.instance = instance
        self.person = person
        self.check_consistency = check_consistency
        self._init_forms()

    def _get_start_postpone_academic_year(self):
        """This function return the academic year which will start the postponement"""
        learning_unit_year_instance = self.instance.forms[LearningUnitYearModelForm].instance
        start_academic_year = learning_unit_year_instance.academic_year
        return academic_year.find_academic_year_by_year(start_academic_year.year + 1)

    def _get_end_postpone_academic_year(self):
        """This function return the academic year which will end the postponement"""
        learning_unit_instance = self.instance.forms[LearningUnitModelForm].instance
        end_year = learning_unit_instance.end_year
        return academic_year.find_academic_year_by_year(end_year) if end_year else None

    def _init_forms(self):
        """This function will init two forms var:
           forms_to_upsert: LearningUnitBaseForm which must be created/updated
           forms_to_delete: LearningUnitBaseForm which must be deleted
        """
        learning_unit_instance = self.instance.forms[LearningUnitModelForm].instance
        start_academic_year = self._get_start_postpone_academic_year()
        end_academic_year = self._get_end_postpone_academic_year()

        if end_academic_year:
            # CASE end year specify in learning unit
            self._forms_to_delete = self._get_forms_to_delete(learning_unit_instance, end_academic_year)

        self._forms_to_upsert = self._get_forms_to_upsert(learning_unit_instance, start_academic_year,
                                                          end_academic_year)

    def _get_forms_to_upsert(self, learning_unit, start_academic_year, end_academic_year):
        luy_to_upsert_qs = learning_unit_year.find_by_learning_unit(learning_unit) \
                                             .filter(academic_year__year__gte=start_academic_year.year)\
                                             .order_by('academic_year__year')
        if end_academic_year:
            luy_to_upsert_qs = luy_to_upsert_qs.filter(academic_year__year__lte=end_academic_year.year)
        # Learning unit base form with instance [TO UPDATE]
        luy_base_form_update = [self._get_learning_unit_base_form(learning_unit_year_instance=luy_to_upsert)
                                for luy_to_upsert in luy_to_upsert_qs]

        # Learning unit base form without instance [TO INSERT]
        lastest_luy = luy_to_upsert_qs.last()
        start_insert_year = lastest_luy.academic_year.year + 1 if lastest_luy else start_academic_year.year
        end_insert_year = end_academic_year.year if end_academic_year else None
        luy_base_form_insert = self._get_forms_to_insert(start_insert_year, end_insert_year)

        return luy_base_form_update + luy_base_form_insert

    def _get_forms_to_insert(self, start_year, end_year=None):
        luy_base_form_insert = []
        max_postponement_year = academic_year.compute_max_academic_year_adjournment()
        end_year = min(end_year,  max_postponement_year) if end_year else max_postponement_year

        if start_year < end_year:
            ac_years = academic_year.find_academic_years(start_year=start_year, end_year=end_year)
            luy_base_form_insert = [self._get_learning_unit_base_form(academic_year=ac_year) for ac_year in ac_years]
        return luy_base_form_insert

    def _get_forms_to_delete(self, learning_unit, end_academic_year):
        luy_to_delete_qs = learning_unit_year.find_by_learning_unit(learning_unit)\
                                             .filter(academic_year__year__gt=end_academic_year.year)
        return [self._get_learning_unit_base_form(learning_unit_year_instance=luy_to_delete)
                for luy_to_delete in luy_to_delete_qs]

    def _get_learning_unit_base_form(self, learning_unit_year_instance=None, academic_year=None):
        form = FullForm if self.instance.subtype == learning_unit_year_subtypes.FULL else PartimForm
        data = deepcopy(self.instance.data)
        if learning_unit_year_instance:
            # Update case
            form_args = {'instance': learning_unit_year_instance,
                         'learning_unit_year_full': learning_unit_year_instance.parent}
        else:
            # Creation case
            form_args = {'default_ac_year': academic_year}
            data.update({'academic_year': academic_year.id})
        form_args.update({'data': data, 'person': self.person})
        return form(**form_args)

    def is_valid(self):
        if any([not form_instance.is_valid() for form_instance in self._forms_to_upsert]):
            return False
        if self.check_consistency:
            return self._check_consistency()
        return True

    def save(self):
        luy_created = []
        for form in self._forms_to_upsert:
            luy_created.append(form.save())
        return luy_created

    def _check_consistency(self):
        """This function will check all field"""
        return True

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
from base.forms.learning_unit.learning_unit_create import LearningUnitModelForm
from base.forms.learning_unit.learning_unit_create_2 import PartimForm, FullForm
from base.models import academic_year, learning_unit_year
from base.models.learning_unit import LearningUnit
from base.models.enums import learning_unit_year_subtypes, entity_container_year_link_type


# @TODO: Use LearningUnitPostponementForm to manage END_DATE of learning unit year
# TODO :: This form should be the LearningUnitModelForm ==> should move code to LearningUnitModelForm class?
class LearningUnitPostponementForm:
    learning_unit_instance = None
    subtype = None
    person = None
    check_consistency = True
    _forms_to_upsert = []
    _forms_to_delete = []

    def __init__(self, person, start_postponement, end_postponement=None, learning_unit_instance=None,
                 learning_unit_full_instance=None, data=None, check_consistency=True):
        """
        :param person: The person who make action form
        :param start_postponement: Start academic year postponement
        :param end_postponement: End academic year postponement [If None, get end_year from learning_unit_instance]
        :param learning_unit_instance: The instance on which modification will be done each year
        :param learning_unit_full_instance: The FULL instance on which modification will be done each year [Used when Partim]
        :param data: Data which will be applied on each FORM (PartimForm/FullForm)
        :param check_consistency: Enable check consitency [Default TRUE]
        """
        if learning_unit_instance and not isinstance(learning_unit_instance, LearningUnit):
            raise AttributeError('learning_unit_instance arg should be an instance of {}'.format(LearningUnit))
        if learning_unit_full_instance and not isinstance(learning_unit_full_instance, LearningUnit):
            raise AttributeError('learning_unit_full_instance arg should be an instance of {}'.format(LearningUnit))

        self.learning_unit_instance = learning_unit_instance
        self.learning_unit_full_instance = learning_unit_full_instance
        self.subtype = learning_unit_year_subtypes.PARTIM if learning_unit_full_instance else \
            learning_unit_year_subtypes.FULL
        self.start_postponement = start_postponement
        self.person = person
        self.check_consistency = check_consistency
        if end_postponement is None and self.learning_unit_instance and self.learning_unit_instance.end_year:
            end_postponement = academic_year.find_academic_year_by_year(self.learning_unit_instance.end_year)
        self.end_postponement = end_postponement
        self._init_forms(data)

    # def _compute_max_postponement_year(self):
    #     max_postponement_year = academic_year.compute_max_academic_year_adjournment()
    #     end_year = self.end_postponement.year if self.end_postponement else None
    #     return min(end_year,  max_postponement_year) if end_year else max_postponement_year
    #
    # def _split_academic_years_to_delete_and_to_upserts(self):
    #     academic_years = academic_year.find_academic_years(start_year=self.start_postponement.year)
    #     to_delete = to_insert = to_update = []
    #     if self._is_update_action():
    #         if self.end_postponement:
    #             return self._calculate_records_to_insert_update_delete(academic_years)
    #         else:
    #             to_update = academic_years
    #     else:
    #         to_insert = academic_years
    #     return {
    #         'to_delete': to_delete,
    #         'to_update': to_update,
    #         'to_insert': to_insert
    #     }
    #
    # def _calculate_records_to_insert_update_delete(self, academic_years):
    #     last_existing_learn_unit_year = learning_unit_year.find_by_learning_unit(self.learning_unit_instance) \
    #         .filter(academic_year__year__lte=self.end_postponement.year).select_related('academic_year').last()
    #     to_delete = filter(lambda ac_year: ac_year.year >= self.end_postponement, academic_years)
    #     to_update = filter(
    #         lambda ac_year: last_existing_learn_unit_year.year < ac_year.year < self.end_postponement, academic_years)
    #     to_insert = filter(lambda ac_year: ac_year.year < last_existing_learn_unit_year.year, academic_years)
    #     return {
    #         'to_delete': to_delete,
    #         'to_update': to_update,
    #         'to_insert': to_insert
    #     }

    # @TODO: WHEN CREATION, we must keep first learning_unit instance created in order to keep start date !!!
    def _init_forms(self, data=None):
        """This function will init two forms var:
           forms_to_upsert: LearningUnitBaseForm which must be created/updated
           forms_to_delete: LearningUnitBaseForm which must be deleted
        """
        if self.end_postponement:
            # CASE end year specify in learning unit
            self._forms_to_delete = self._get_forms_to_delete(self.end_postponement.year, self.learning_unit_instance)

        if self.learning_unit_instance:
            # Update case
            self._forms_to_upsert = self._get_forms_to_upsert(data, self.start_postponement)
        else:
            # Creation case
            start_year = self.start_postponement.year
            end_year = self.end_postponement.year if self.end_postponement else None
            self._forms_to_upsert = self._get_forms_to_insert(start_year, end_year, data)

    def _get_forms_to_upsert(self, data, start_academic_year):
        end_academic_year = self.end_postponement

        luy_to_upsert_qs = learning_unit_year.find_by_learning_unit(self.learning_unit_instance) \
                                             .filter(academic_year__year__gte=start_academic_year.year)\
                                             .select_related('academic_year')\
                                             .order_by('academic_year__year')
        if end_academic_year:
            luy_to_upsert_qs = luy_to_upsert_qs.filter(academic_year__year__lte=end_academic_year.year)
        # Learning unit base form with instance [TO UPDATE]
        luy_base_forms_update = [self._get_learning_unit_base_form(luy_to_upsert.academic_year,
                                                                   learning_unit_instance=luy_to_upsert.learning_unit,
                                                                   data=data)
                                 for luy_to_upsert in luy_to_upsert_qs]

        # Learning unit base form without instance [TO INSERT]
        lastest_luy = luy_to_upsert_qs.last()
        start_insert_year = lastest_luy.academic_year.year + 1 if lastest_luy else start_academic_year.year
        end_insert_year = end_academic_year.year if end_academic_year else None
        luy_base_forms_insert = self._get_forms_to_insert(start_insert_year, end_year=end_insert_year, data=data)
        return luy_base_forms_update + luy_base_forms_insert

    def _get_forms_to_insert(self, start_year, end_year=None, data=None):
        luy_base_form_insert = []
        max_postponement_year = academic_year.compute_max_academic_year_adjournment()
        end_year = min(end_year,  max_postponement_year) if end_year else max_postponement_year

        if start_year <= end_year:
            # Create a first LearningUnit not persistent (to get the same learningUnit for all LearningUnitYears)
            # learn_unit = LearningUnit(start_year=start_year, end_year=self.end_postponement)
            ac_years = academic_year.find_academic_years(start_year=start_year, end_year=end_year)
            luy_base_form_insert = [self._get_learning_unit_base_form(ac_year, data=data, start_year=start_year)
                                    for ac_year in ac_years]

            # # Create a first LearningUnit not persistent (to get the same learningUnit for all LearningUnitYears)
            # ac_years = academic_year.find_academic_years(start_year=start_year, end_year=end_year)
            # first_form = self._get_learning_unit_base_form(ac_years[0], data=data)
            # luy_base_form_insert = [first_form]
            # if len(ac_years) > 1:
            #     luy_base_form_insert += [
            #         self._get_learning_unit_base_form(ac_year, data=data,
            #                                           learning_unit_instance=first_form.forms[LearningUnitModelForm].instance)
            #         for ac_year in ac_years
            #         ]
        return luy_base_form_insert

    def _get_forms_to_delete(self, start_year, learning_unit_instance):
        end_year = self.end_postponement.year
        luy_to_delete_qs = learning_unit_year.find_by_learning_unit(self.learning_unit_instance)\
                                             .filter(academic_year__year__gt=end_year).select_related('academic_year')
        return [self._get_learning_unit_base_form(luy.academic_year, learning_unit_instance=learning_unit_instance)
                for luy in luy_to_delete_qs]

    def _get_learning_unit_base_form(self, academic_year, learning_unit_instance=None, data=None, start_year=None):
        form_kwargs = {
            'person': self.person,
            'learning_unit_instance': learning_unit_instance,
            'academic_year': academic_year,
            'start_year': start_year,
            'data': data.copy() if data else None,
            'learning_unit_full_instance': self.learning_unit_full_instance
        }
        if learning_unit_instance and data:
            learning_unit_year_full_instance = learning_unit_year.search(academic_year_id=academic_year.id,
                                                                         learning_unit=learning_unit_instance).get()
            management_form_updated = self._get_entity_formset_management_form(data, learning_unit_year_full_instance)
            form_kwargs['data'].update(management_form_updated)

        return FullForm(**form_kwargs) if self.subtype == learning_unit_year_subtypes.FULL else \
            PartimForm(**form_kwargs)

    def _get_entity_formset_management_form(self, data, learning_unit_year_full_instance):
        """This function will update specific key [related to learning container year]
           of management form provided by formset"""
        management_form = {}
        for index, type in enumerate(entity_container_year_link_type.ENTITY_TYPE_LIST):
            if data.get('entitycontaineryear_set-{}-learning_container_year'.format(index)):
                management_form['entitycontaineryear_set-{}-learning_container_year'.format(index)] = \
                    learning_unit_year_full_instance.learning_container_year.id
        return management_form

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

        return {
            '2017-18': {
                'acronym': {
                    'old_value': 'LDROI1001',
                    'new_value': 'LDROI9999'
                }
            }
        }

    def get_context(self):
        if self._forms_to_upsert:
            return self._forms_to_upsert[0].get_context()
        return {}

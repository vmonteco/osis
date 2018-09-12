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
import datetime
import pathlib

from django.core.management import BaseCommand, CommandError
from django.db.transaction import atomic

from base.models.academic_year import AcademicYear
from base.models.admission_condition import AdmissionCondition
from base.models.education_group_year import EducationGroupYear


def check_parameters(filename):
    path = pathlib.Path(filename)
    if not path.exists():
        raise CommandError('The file {} does not exist'.format(filename))

    return path


class Command(BaseCommand):
    def add_arguments(self, parser):
        this_year = datetime.date.today().year
        parser.add_argument('--from', type=int, default=this_year, dest='from_year')
        parser.add_argument('--to', type=int, default=this_year + 1, dest='to_year')

    @atomic
    def handle(self, *args, **options):
        # cpprint(options)

        academic_year_to = AcademicYear.objects.get(year=options['to_year'])

        for egy_source in EducationGroupYear.objects.filter(academic_year__year=options['from_year']):
            egy_destination = EducationGroupYear.objects.filter(academic_year=academic_year_to,
                                                                education_group=egy_source.education_group,
                                                                acronym=egy_source.acronym)
            if egy_destination is None:
                continue

            self.duplicate_info(egy_source, egy_destination)

    def duplicate_info(self, source, destination):
        # self.duplicate_cms_terms(source, destination)
        self.duplicate_admission_condition(source, destination)
        # pass

    def duplicate_cms_terms(self, source, destination):
        pass

    def duplicate_admission_condition(self,
                                      education_group_year_source,
                                      education_group_year_destination):
        admission_condition_source = AdmissionCondition.objects.get(
            education_group_year=education_group_year_source
        )

        admission_condition_dest, created = AdmissionCondition.objects.get_or_create(
            education_group_year=education_group_year_destination
        )

        for line in AdmissionConditionLine.objects.filter(admission_condition=admission_condition_source):
            self.duplicate_admission_condition_line(line, admission_condition_dest)

    def duplicate_admission_condition_line(self, source, admission_condition_dest):
        dest, created = AdmissionConditionLine.objects.get_or_create(
            admission_condition=admission_condition_dest,
            section=source.section,
            order=source.order
        )

        source.duplicate(dest)
        dest.save()
##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
import csv
from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from base import models as mdl
from internship import models


@login_required
def internships_students(request):
    #Function to find students link to internship incoming
    students = None

    #Dont delete this bloc of comment
    #if students:
    #    for student in students:
    #        student.address = ""
    #        address = mdl.person_address.find_by_person(student.person)
    #        if address:
    #            student.address = address

    return render(request, "students.html", {'section': 'internship', 'all_students': students})


# To be removed once all students are imported.
def load_internship_students():
    with open('internship/views/internship_students.csv') as csvfile:
        row = csv.reader(csvfile)
        imported_counter = 0
        error_counter = 0
        duplication_counter = 0
        for columns in row:
            if len(columns) > 0:
                person = mdl.person.find_by_global_id(columns[1].strip())
                if person:
                    internships_student = models.InternshipStudentInformation()
                    internships_student.person = person
                    internships_student.location = columns[2].strip()
                    internships_student.postal_code = columns[3].strip()
                    internships_student.city = columns[4].strip()
                    internships_student.country = columns[5].strip()
                    internships_student.email = columns[6].strip()
                    internships_student.phone_mobile = columns[7].strip()
                    try:
                        internships_student.save()
                    except IntegrityError:
                        print("Duplicate : {}".format(str(person)))
                        duplication_counter += 1
                    if person.user :
                        intern_students_group = Group.objects.get(name='internship_students')
                        person.user.groups.add(intern_students_group)
                    imported_counter += 1
                else:
                    error_counter += 1
                    print("Erreur : {} - {}".format(columns[0],columns[1]))
        print("Imports : {}".format(imported_counter))
        print("Erreur de données : {}".format(error_counter))
        print("Duplication : {}".format(duplication_counter))
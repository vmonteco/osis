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
from enum import Enum
from base.models.utils.utils import ChoiceEnum
from django.utils.translation import ugettext_lazy as _

NO_ADDITIONAL_FEES = "NO_ADDITIONAL_FEES"
AESS_CAPAES = "AESS_CAPAES"
MINERVAL_COMPLETE = "MINERVAL_COMPLETE"
UNIVERSITY_CERTIFICATE = "UNIVERSITY_CERTIFICATE"
ADVANCED_MASTER_IN_MEDICAL_SPECIALIZATION = "ADVANCED_MASTER_IN_MEDICAL_SPECIALIZATION"
ACCESS_CONTEST = "ACCESS_CONTEST"
UNIVERSITY_CERTIFICATE_30_CREDITS = "UNIVERSITY_CERTIFICATE_30_CREDITS"
CERTIFICATE_MEDECINE_COMPETENCE = "CERTIFICATE_MEDECINE_COMPETENCE"


RATE_CODE = (
    (NO_ADDITIONAL_FEES, _(NO_ADDITIONAL_FEES)),
    (AESS_CAPAES, _(AESS_CAPAES)),
    (MINERVAL_COMPLETE, _(MINERVAL_COMPLETE)),
    (UNIVERSITY_CERTIFICATE, _(UNIVERSITY_CERTIFICATE)),
    (ADVANCED_MASTER_IN_MEDICAL_SPECIALIZATION, _(ADVANCED_MASTER_IN_MEDICAL_SPECIALIZATION)),
    (ACCESS_CONTEST, _(ACCESS_CONTEST)),
    (UNIVERSITY_CERTIFICATE_30_CREDITS, _(UNIVERSITY_CERTIFICATE_30_CREDITS)),
    (CERTIFICATE_MEDECINE_COMPETENCE, _(CERTIFICATE_MEDECINE_COMPETENCE))
)


class RateCodes(ChoiceEnum):
    NO_ADDITIONAL_FEES = "NO_ADDITIONAL_FEES"
    AESS_CAPAES = "AESS_CAPAES"
    MINERVAL_COMPLETE = "MINERVAL_COMPLETE"
    UNIVERSITY_CERTIFICATE = "UNIVERSITY_CERTIFICATE"
    ADVANCED_MASTER_IN_MEDICAL_SPECIALIZATION = "ADVANCED_MASTER_IN_MEDICAL_SPECIALIZATION"
    ACCESS_CONTEST = "ACCESS_CONTEST"
    UNIVERSITY_CERTIFICATE_30_CREDITS = "UNIVERSITY_CERTIFICATE_30_CREDITS"
    CERTIFICATE_MEDECINE_COMPETENCE = "CERTIFICATE_MEDECINE_COMPETENCE"

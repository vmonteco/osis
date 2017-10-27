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
import logging
import pika
import pika.exceptions

from django.conf import settings

from osis_common.queue import queue_sender


logger = logging.getLogger(settings.DEFAULT_LOGGER)


def publish_to_portal(global_ids=None):
    application_list = _compute_list(global_ids)
    queue_name = settings.QUEUES.get('QUEUES_NAME', {}).get('ATTRIBUTION_RESPONSE')

    if queue_name:
        try:
            queue_sender.send_message(queue_name, application_list)
        except (RuntimeError, pika.exceptions.ConnectionClosed, pika.exceptions.ChannelClosed,
                 pika.exceptions.AMQPError):
            logger.exception('Could not recompute attributions for portal...')
            return False
        return True
    else:
        logger.exception('Could not recompute attributions for portal because not queue name ATTRIBUTION_RESPONSE')
        return False


def _compute_list(global_ids=None):
    return []
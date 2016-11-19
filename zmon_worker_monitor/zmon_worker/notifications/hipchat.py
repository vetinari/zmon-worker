import logging
import urllib
import json

import requests

from notification import BaseNotification

logger = logging.getLogger(__name__)

class NotifyHipchat(BaseNotification):
    @classmethod
    def notify(cls, alert, *args, **kwargs):
        url = cls._config.get('notifications.hipchat.url')

        if not url:
            logger.error("NOTIFICATIONS_HIPCHAT_URL is not set")
            return 0

        token = kwargs.get('token', cls._config.get('notifications.hipchat.token'))
        if not token:
            logger.error("NOTIFICATIONS_HIPCHAT_TOKEN is not set")
            return 0

        repeat = kwargs.get('repeat', 0)
        notify = kwargs.get('notify', False)

        color = 'green' if alert and not alert.get('is_alert') else kwargs.get('color', 'red')

        message = {
            'message': cls._get_subject(alert, custom_message=kwargs.get('message')),
            'color': color,
            'notify': notify
        }

        try:
            logger.info(
                'Sending to: ' + '{}/v2/room/{}/notification?auth_token={}'.format(url, urllib.quote(kwargs['room']),
                                                                                   token) + ' ' + json.dumps(message))
            r = requests.post(
                '{}/v2/room/{}/notification'.format(url, urllib.quote(kwargs['room'])),
                json=message, params={'auth_token': token}, headers={'Content-type': 'application/json'})
            r.raise_for_status()
        except:
            logger.exception('Hipchat write failed!')

        return repeat

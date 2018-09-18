import json
import uuid
import os
import datetime

from xml.sax.saxutils import escape
from django.conf import settings
from zeus.mobile.mybsms import escape_dict


class Client(object):

    id = "dummy"
    remote_status = False

    def __init__(self, from_mobile, user, password, dlr_url):
        self.user = user
        self.password = password
        self.from_mobile = from_mobile
        self.delivery_url = dlr_url
        assert self.delivery_url

    def _construct(self, uid, msisdn, message):
        req = {}
        req['username'] = self.user
        req['password'] = self.password
        req['recipients'] = [str(msisdn)]
        message = escape(message, escape_dict)
        req['message'] = message
        if self.delivery_url:
            req['dlr-url'] = self.delivery_url
        req['senderId'] = self.from_mobile
        return req

    def status(self, msgid):
        raise NotImplementedError

    def send(self, mobile, msg, fields={}, uid=None):
        file_contents = ""
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        fname = "sms-%s-%s.log" % (timestamp, abs(id(self)))
        BASE_DIR = os.path.abspath(settings.SMS_FILE_PATH)
        if not uid:
            uid = unicode(uuid.uuid4())

        mobile = mobile.replace("+", "")
        msg = self._construct(uid, mobile, msg)
        fd = file(os.path.join(BASE_DIR, fname), "w+")
        data = json.dump(msg, fd, indent=4)
        fd.close()
        self._last_uid = uid
        return True, str(abs(id(self)))

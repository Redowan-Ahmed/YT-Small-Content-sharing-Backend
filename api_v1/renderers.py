from __future__ import unicode_literals
import six
from rest_framework.renderers import BaseRenderer
import ujson


class UJSONRenderer(BaseRenderer):

    media_type = 'application/json'
    format = 'json-fast'
    ensure_ascii = True
    charset = None

    def render(self, data, *args, **kwargs):

        if data is None:
            return bytes()

        ret = ujson.dumps(data, ensure_ascii=self.ensure_ascii)

        # force return value to unicode
        if isinstance(ret, six.text_type):
            return bytes(ret.encode('utf-8'))
        return ret
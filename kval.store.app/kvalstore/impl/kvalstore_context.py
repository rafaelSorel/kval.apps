__author__ = 'kval team'

from six.moves import urllib
from six import string_types
import os
import sys
import weakref
import datetime
import json
from time import sleep
import gettext

import logging
LOGGER = logging.getLogger('kvalstore')
LOGGER.setLevel(logging.ERROR)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter
formatter = logging.Formatter('%(asctime)s #%(threadName)s [%(levelname)s] %(name)s::%(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
LOGGER.addHandler(ch)
LOGGER.propagate = False

from kvalstore_context_ui import KvalStoreCtxUI as CtxUI
from kvalstore_settings import KvalStoreAppSettings as AppSettings
from kval import Binder

lang = None
_ = None

class KvalStoreContext():
    def __init__(self,
                 path='/',
                 params=None,
                 plugin_name=u'',
                 plugin_id=u'',
                 override=True,
                 appbinder=None):
        """
        We have to extract the information from the sys parameters
        and re-build our clean uri. Also we extract the path and parameters -
        man, that would be so simple with the normal url-parsing routines.
        """
        if not params:
            params = {}

        self._path = create_path(path)
        self._utils = None
        self._view_mode = None
        self._params = params

        # first the path of the uri
        if override and len(sys.argv) > 2:
            self._uri = sys.argv[2]
            self.log_info("self._uri: " + self._uri)
            comps = urllib.parse.urlparse(self._uri)
            self._path = urllib.parse.unquote(comps.path)
            self.log_info("self._path: " + self._path)

            # after that try to get the params
            if len(sys.argv) > 2:
                try:
                    params = sys.argv[2].split("?")[-1]
                except:
                    params = []
                    pass

                if len(params) > 0:
                    self._uri = self._uri + '?' + params

                    params = dict(urllib.parse.parse_qsl(params))
                    for _param in params:
                        item = params[_param]
                        self._params[_param] = item

                    self.log_info("self._params: "+str(self._params))

        self._system_version = None
        self._appbinder = Binder(appid=plugin_id) if not appbinder else appbinder
        self._ui = None
        self._plugin_handle = int(sys.argv[1]) if len(sys.argv) > 1 else None
        self._plugin_id = plugin_id
        self._plugin_name = plugin_name
        self._version = '1.0.0'
        self._display_mode = '1'
        self._display_submode = '1'
        self._native_path = self._appbinder.getNativePath()
        self._settings = AppSettings(self._appbinder)
        self._lang_path = os.path.join(self._native_path, "resources/languages")
        global lang
        lang = gettext.translation('base',
                   localedir=self._lang_path,
                   languages=['fr' if 'fr' in self.get_language() else 'en'])
        lang.install()

        global _
        _ = lang.gettext

    def format_date_short(self, date_obj):
        print("getRegion('dateshort')")
        date_format = "YY:MM:DD"
        _date_obj = date_obj
        if isinstance(_date_obj, datetime.date):
            _date_obj = datetime.datetime(_date_obj.year, _date_obj.month, _date_obj.day)

        return _date_obj.strftime(date_format)

    def format_time(self, time_obj):
        print("getRegion('time')")
        time_format = "hh:mm"
        _time_obj = time_obj
        if isinstance(_time_obj, datetime.time):
            _time_obj = datetime.time(_time_obj.hour, _time_obj.minute, _time_obj.second)

        return _time_obj.strftime(time_format)

    def get_appbinder(self):
        return self._appbinder

    def create_uri(self, path=u'/', params=None):
        if not params:
            params = {}

        uri = create_uri_path(path)
        if uri:
            uri = "%s://%s%s" % ('plugin', str(self._plugin_id), uri)
        else:
            uri = "%s://%s/" % ('plugin', str(self._plugin_id))

        if len(params) > 0:
            # make a copy of the map
            uri_params = {}
            uri_params.update(params)

            # encode in utf-8
            for param in uri_params:
                if isinstance(params[param], int):
                    params[param] = str(params[param])

                uri_params[param] = to_utf8(params[param])
            uri += '?' + urllib.parse.urlencode(uri_params)

        return uri
        
    def get_language(self):
        """
        Get current language from appbinder
        """
        return self._appbinder.getLanguage()

    def get_system_version(self):
        if not self._system_version:
            self._system_version = '1.5.0'

        return self._system_version

    def get_ui(self):
        if not self._ui:
            self._ui = CtxUI(weakref.proxy(self))
        return self._ui

    def get_handle(self):
        return self._plugin_handle

    def get_native_path(self):
        return self._native_path

    def get_settings(self):
        return self._settings

    def getLocalizedString(self, text_id):
        return ""

    def localize(self, text_id, default_text=u''):
        if text_id is not "":
            return _(text_id)

        return self.to_unicode(default_text)

    def set_content_type(self, content_type):
        self.log_info('Setting content-type: "%s" for "%s"' % (content_type, self.get_path()))

    def add_sort_method(self, *sort_methods):
        for sort_method in sort_methods:
            self.log_debug("sort_method: " + str(sort_method))

    def set_display_mode(self, mode='1', submode='2'):
        self._display_mode = mode
        self._display_submode = submode

    def get_display_mode(self):
        return self._display_mode

    def get_display_submode(self):
        return self._display_submode

    def execute(self, command):
        self.log_info("executebuiltin(command)" + str(command))
        self.get_appbinder().executebuiltin(command)

    def sleep(self, milli_seconds):
        self.log_debug("sleep " + str(milli_seconds))
        sleep(milli_seconds/1000)

    def send_notification(self, method, data):
        data = json.dumps(data)
        self.log_debug('send_notification: |%s| -> |%s|' % (method, data))
        data = '\\"[\\"%s\\"]\\"' % urllib.parse.quote(data)
        self.execute('NotifyAll(kval.store.app,%s,%s)' % (method, data))

    def getInstalledAppsList(self):
        try:
            return self.get_appbinder().get_installed_apps()
        except:
            return None

    def get_path(self):
        return self._path

    def set_path(self, value):
        self._path = value

    def get_params(self):
        return self._params

    def get_param(self, name, default=None):
        return self.get_params().get(name, default)

    def set_param(self, name, value):
        self._params[name] = value

    def get_icon(self):
        return os.path.join(self.get_native_path(), 'icon.png')

    def get_fanart(self):
        return os.path.join(self.get_native_path(), 'fanart.png')

    def create_resource_path(self, *args):
        path_comps = []
        for arg in args:
            path_comps.extend(arg.split('/'))
        path = os.path.join(self.get_native_path(), 'resources', *path_comps)
        return 'file://' + path

    def get_uri(self):
        return self._uri

    def get_name(self):
        return self._plugin_name

    def get_version(self):
        return self._version

    def get_id(self):
        return self._plugin_id

    def log_error(self, text):
        LOGGER.error(text)

    def log_notice(self, text):
        LOGGER.debug(text)

    def log_debug(self, text):
        LOGGER.debug(text)

    def log_info(self, text):
        LOGGER.info(text)

    def to_unicode(self, text):
        result = text
        if isinstance(text, string_types):
            try:
                result = text.decode('utf-8')
            except (AttributeError, UnicodeEncodeError):
                pass

        return result


def create_path(*args):
    comps = []
    for arg in args:
        if isinstance(arg, list):
            return create_path(*arg)

        comps.append(str(arg.strip('/').replace('\\', '/').replace('//', '/')))

    uri_path = '/'.join(comps)
    if uri_path:
        return u'/%s/' % uri_path

    return '/'


def create_uri_path(*args):
    comps = []
    for arg in args:
        if isinstance(arg, list):
            return create_uri_path(*arg)

        comps.append(str(arg.strip('/').replace('\\', '/').replace('//', '/')))

    uri_path = '/'.join(comps)
    if uri_path:
        return urllib.parse.quote('/%s/' % uri_path)

    return '/'

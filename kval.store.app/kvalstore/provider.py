__author__ = 'kval team'

import os
import re
import json
import shutil
import socket
from base64 import b64decode
from distutils.version import LooseVersion

from kvalstore.items import *
from kvalstore.store import client

class RegisterProviderPath(object):
    """
    Exec dict function related to the call.
    """
    def __init__(self, re_path):
        self._kvalon_re_path = re_path
        print "re_path: " + re_path

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            # only use a wrapper if you need extra code to be run here
            return func(*args, **kwargs)

        wrapper.kvalon_re_path = self._kvalon_re_path
        return wrapper

class KvalException(Exception):
    """
    Exception handler
    """
    def __init__(self, message):
        Exception.__init__(self, message)
        self._message = message

    def get_message(self):
        return self._message

class Provider():
    """
    Dispatcher class for all the requests
    comming from main application
    """
    def __init__(self):
        self._resource_manager = None

        self._client = None
        self._is_logged_in = False

        # map for regular expression (path) to method (names)
        self._dict_path = {}

        # register some default paths
        self.register_path('^/$', '_internal_root')
        self.register_path('(?P<path>.*\/)extrafanart\/([\?#].+)?$', '_internal_on_extra_fanart')

        """
        Test each method of this class for the appended attribute '_re_match' by the
        decorator (RegisterProviderPath).
        The '_re_match' attributes describes the path which must match for the decorated method.
        """

        for method_name in dir(self):
            method = getattr(self, method_name)
            if hasattr(method, 'kvalon_re_path'):
                self.register_path(method.kvalon_re_path, method_name)

    def get_alternative_fanart(self, context):
        return context.get_fanart()

    def navigate(self, context):
        path = context.get_path()

        for key in self._dict_path:
            re_match = re.search(key, path, re.UNICODE)
            if re_match is not None:
                method_name = self._dict_path.get(key, '')
                method = getattr(self, method_name)
                if method is not None:
                    result = method(context, re_match)
                    if not isinstance(result, tuple):
                        result = result, {}
                    return result

        raise KvalException("Mapping for path '%s' not found" % path)

    def on_extra_fanart(self, context, re_match):
        """
        The implementation of the provider can override this behavior.
        :param context:
        :param re_match:
        :return:
        """
        return None

    def _internal_on_extra_fanart(self, context, re_match):
        path = re_match.group('path')
        new_context = context.clone(new_path=path)
        return self.on_extra_fanart(new_context, re_match)

    def _internal_root(self, context, re_match):
        return self.on_root(context, re_match)

    def handle_exception(self, context, exception_to_handle):
        return True

    def tear_down(self, context):
        pass

    def register_path(self, re_path, method_name):
        """
        Registers a new method by name (string) for the given regular expression
        :param re_path: regular expression of the path
        :param method_name: name of the method
        :return:
        """
        self._dict_path[re_path] = method_name

    @staticmethod
    def get_dev_config(context, addon_id, dev_configs):
        _dev_config = None #context.get_ui().get_home_window_property('configs')
        #context.get_ui().clear_home_window_property('configs')

        dev_config = None
        if _dev_config is not None:
            context.log_debug('Using window property for developer keys is deprecated, instead use the youtube_registration module.')
            try:
                dev_config = json.loads(_dev_config)
            except ValueError:
                context.log_error('Error loading developer key: |invalid json|')
        if not dev_config and addon_id and dev_configs:
            dev_config = dev_configs.get(addon_id)

        if dev_config is not None and not context.get_settings().allow_dev_keys():
            context.log_debug('Developer config ignored')
            return None
        elif dev_config:
            if not dev_config.get('main') or not dev_config['main'].get('key') \
                    or not dev_config['main'].get('system') or not dev_config.get('origin') \
                    or not dev_config['main'].get('id') or not dev_config['main'].get('secret'):
                context.log_error('Error loading developer config: |invalid structure| '
                                  'expected: |{"origin": ADDON_ID, "main": {"system": SYSTEM_NAME, "key": API_KEY, "id": CLIENT_ID, "secret": CLIENT_SECRET}}|')
                return None
            else:
                dev_origin = dev_config['origin']
                dev_main = dev_config['main']
                dev_system = dev_main['system']
                if dev_system == 'JSONStore':
                    dev_key = b64decode(dev_main['key'])
                    dev_id = b64decode(dev_main['id'])
                    dev_secret = b64decode(dev_main['secret'])
                else:
                    dev_key = dev_main['key']
                    dev_id = dev_main['id']
                    dev_secret = dev_main['secret']
                context.log_debug('Using developer config: origin: |{0}| system |{1}|'.format(dev_origin, dev_system))
                return {'origin': dev_origin, 'main': {'id': dev_id, 'secret': dev_secret, 'key': dev_key, 'system': dev_system}}
        else:
            return None

    def get_fanart(self, context):
        return context.create_resource_path('media', 'fanart.png')

    @RegisterProviderPath('^/apps/(?P<category>[^/]+)/$')
    def _on_fetch_apps(self, context, re_match):
        context.log_info("fetch applications...")
        context.set_display_mode(mode='1', submode='1')
        category = re_match.group('category')
        context.log_info("category: " + category)
        if category == 'browse_channels':
            context.set_display_mode(mode='1', submode='1')

        return client.process(category, self, context, re_match)
    
    @RegisterProviderPath('^/install/(?P<appid>[^/]+)/$')
    def _on_install_app(self, context, re_match):
        context.set_display_mode(mode='1', submode='1')
        appid = re_match.group('appid')
        context.log_info("Install request: " + appid)
        install_info = None
        try:
            install_info = client.get_install_info(appid, context)
        except: 
            context.get_ui().show_notification( \
            context.localize("Problem occured while connecting to store."),
            header=context.localize("Store Problem"))
            return None

        if not install_info:
            context.get_ui().show_notification( \
                      context.localize("Application not found on the store !"),
                      header=context.localize("Application Not Found"))
            return None

        installed_apps = context.getInstalledAppsList()
        for installed_app in installed_apps:
            if installed_app.get('name') == install_info.get('id'):
                #check version
                if  LooseVersion(installed_app.get('version')) >= \
                    LooseVersion(install_info.get('version')):
                    context.log_info("Already installed app: " + install_info.get('id'))
                    context.get_ui().on_ok(
                        context.localize("Install {appname}").format(appname=install_info["name"]),
                        context.localize("<b>{appname}</b> is already installed with version <b>{version}</b>.").\
                                            format(appname=install_info["name"],
                                                   version=install_info.get("version")))
                    return
                else :
                    break

        reply = context.get_ui().on_yes_no_input( \
                     context.localize("Install {appname}").format(appname=install_info["name"]),
                     context.localize("Would you like to install<br><b>{appname}</b> ?").\
                                        format(appname=install_info["name"]),
                                        nolabel=context.localize("Cancel"),
                                        yeslabel=context.localize("Install"))
        if not reply:
            return None

        context.execute("InstallApp(%s, %s, %s, %s)" % \
                        (install_info["id"],
                         install_info["url"],
                         install_info["version"] if "version" in install_info else "",
                         install_info["hash"] if "hash" in install_info else ""))
        return

    @RegisterProviderPath('^/subscriptions/(?P<method>[^/]+)/$')
    def _on_subscriptions(self, context, re_match):
        method = re_match.group('method')
        return yt_subscriptions.process(method, self, context, re_match)

    def on_root(self, context, re_match):
        """
        root entry application
        """
        context.set_display_mode(mode='1', submode='1')
        settings = context.get_settings()

        result = []
        #All Apps Item
        all_apps_item = DirectoryItem('%s' % context.localize("All applications"),
                                     context.create_uri(['apps', 'all']),
                                     image=context.create_resource_path('media', 'all_apps.png'))
        all_apps_item.set_fanart(self.get_fanart(context))
        result.append(all_apps_item)

        #Video Apps Item
        video_apps_item = DirectoryItem('%s' % context.localize("Video applications"),
                                     context.create_uri(['apps', 'video']),
                                     image=context.create_resource_path('media', 'video_apps.png'))
        video_apps_item.set_fanart(self.get_fanart(context))
        result.append(video_apps_item)

        #Game Apps Item
        game_apps_item = DirectoryItem('%s' % context.localize("Game applications"),
                                     context.create_uri(['apps', 'game']),
                                     image=context.create_resource_path('media', 'game_apps.png'))
        game_apps_item.set_fanart(self.get_fanart(context))
        result.append(game_apps_item)

        #Program Apps Item
        prog_apps_item = DirectoryItem('%s' % context.localize("Program applications"),
                                     context.create_uri(['apps', 'program']),
                                     image=context.create_resource_path('media', 'program_apps.png'))
        prog_apps_item.set_fanart(self.get_fanart(context))
        result.append(prog_apps_item)
        
        #favorite Apps Item
        favorite_apps_item = DirectoryItem('%s' % context.localize("Favorites"),
                                     context.create_uri(['apps', 'favorite']),
                                     image=context.create_resource_path('media', 'favorite_apps.png'))
        favorite_apps_item.set_fanart(self.get_fanart(context))
        result.append(favorite_apps_item)

        #search Apps Item
        search_apps_item = DirectoryItem('%s' % context.localize("Search"),
                                     context.create_uri(['apps', 'search']),
                                     image=context.create_resource_path('media', 'search_apps.png'))
        search_apps_item.set_fanart(self.get_fanart(context))
        result.append(search_apps_item)

        #Settins Item
        """
        settings_item = DirectoryItem('%s' % context.localize("Settings"),
                                     context.create_uri(['apps', 'settings']),
                                     image=context.create_resource_path('media', 'settings.png'))
        settings_item.set_fanart(self.get_fanart(context))
        result.append(settings_item)
        """

        return result

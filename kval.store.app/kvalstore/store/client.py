#-*- coding: utf-8 -*-
from hashlib import md5, sha1
from os import uname
import json
import urllib
from traceback import print_exc

from .. utils.net import Net
from .. items import *

KVAL_USERAGENT = 'kval unique User Agent'

DEFAULT_STORE_ADDRESS = "serverAddrHere"

class StoreClient:
    '''
    StoreClient Server Class
    '''
    def __init__(self, context):
        self._context = context
        self.server_addr = None
        self._headers = { "Content-type": "application/x-www-form-urlencoded", \
                          "Accept": "text/plain", \
                          "User-Agent": KVAL_USERAGENT}
        self.net = Net()
        self.conf_files_hashes={}
        self.hostname = self.gethostname()

    def gethostname(self):
        myhost = uname()[1]
        self._context.log_info('myhost: ' + myhost)
        return myhost

    def get_server_addr(self):
        return self.server_addr

    def set_server_addr(self, server_addr):
        '''
        Set the server address
        '''
        self._context.log_info('set_server_addr: ' + server_addr)
        self.server_addr = 'https://' + server_addr

    def _kval_hash(self, strIn):
        '''
        Hash confidential data
        '''
        self._context.log_info( '_kval_hash' )
        if strIn == '' :
            return ''
        self._context.log_info('strIn: "%s"' % strIn)
        self._context.log_info('hash: "%s"' \
                               % sha1(md5(strIn).hexdigest()).hexdigest())
        return sha1(md5(strIn).hexdigest()).hexdigest()

    def fetch_apps(self, cat, lang):
        '''
        interactions with server for live subs
        '''

        self._context.log_info('fetch_all_apps for: %s' % self.hostname)
        params = urllib.urlencode({ 'name': self._kval_hash(self.hostname), \
                                    'action': 'fetch',
                                    'category': cat,
                                    'lang': lang})

        url = self.server_addr + '/server?' + params
        self._context.log_info('url: ' + str(url))
        try :
            #get response from server
            rsp = self.net.http_GET(url, headers=self._headers).content
            self._context.log_info('rsp: ' + str(rsp))
            jsonData = json.loads(rsp)
        except:
            self._context.log_error('Problem connection occured' )
            print_exc()
            return None

        #process server response and data
        if jsonData['responseCode'] == 200:
            try :
                #parse data received in here
                return self.response_to_items(jsonData['list'])
            except :
                self._context.log_error('Could not parse received data')
                print_exc()
                return None

        else :
            self._context.log_error("Response code: " + jsonData['responseCode'])
            return None

    def fetch_app_install_info(self, appid):
        """
        Extract install info from the store server
        """

        params = urllib.urlencode({ 'name': self._kval_hash(self.hostname), \
                                    'action': 'info',
                                    'appid': appid})

        url = self.server_addr + '/server?' + params
        self._context.log_info('url: ' + str(url))
        try :
            #get response from server
            rsp = self.net.http_GET(url, headers=self._headers).content
            self._context.log_info('rsp: ' + str(rsp))
            jsonData = json.loads(rsp)
        except:
            self._context.log_error('Problem connection occured')
            print_exc()
            return None

        #process server response and data
        if jsonData['responseCode'] == 200:
            try :
                #parse data received in here
                return jsonData['info']
            except :
                self._context.log_error('Could not parse received data')
                print_exc()
                return None

        else :
            self._context.log_error("Response code: " + jsonData['responseCode'])
            return None

    def response_to_items(self, json_data, process_next_page=True):
        """
        Convert json response to UI display items.
        """
        items = []
        for app in json_data:
            item = DirectoryItem('%s' % app['ui_name'],
                          self._context.create_uri(['install', app['name']]),
                          image=app['icon'] if 'icon' in app else '',
                          fanart=app['fanart'] if 'fanart' in app else '')

            item.set_thumb(app['backimage'] if 'backimage' in app else '')
            item.set_date("Version "+app['version'] if 'version' in app else '')
            item.set_studio(app['provider'] if 'provider' in app else '')
            #item.set_isFolder(False)
            if 'resume' in app : 
                item.set_plot(app['resume'])

            items.append(item)

        return items

def process(method, provider, context, re_match):
    """
    fetch applications from server.
    """
    context.log_info('Requests apps category: ' + method)
    storeClient = StoreClient(context)
    serverAddress = context.get_appbinder().getSrvMainAddr()
    if not serverAddress or serverAddress == "":
        serverAddress = DEFAULT_STORE_ADDRESS
    storeClient.set_server_addr(serverAddress)
    lang = 'fr' if 'fr' in context.get_language() else 'en'
    return storeClient.fetch_apps(method, lang)

def get_install_info(appid, context):
    """
    Get install info (appname, appid, applink)
    """
    context.log_info('Requests install info for: ' + appid)
    storeClient = StoreClient(context)
    serverAddress = context.get_appbinder().getSrvMainAddr()
    if not serverAddress or serverAddress == "":
        serverAddress = DEFAULT_STORE_ADDRESS
    storeClient.set_server_addr(serverAddress)
    return storeClient.fetch_app_install_info(appid)
    

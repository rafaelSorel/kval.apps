__author__ = 'kval team'

class KvalStoreAppSettings():
    def __init__(self, appbinder):

        self._appbinder = appbinder

    def get_string(self, setting_id, default_value=None):
        return self._appbinder.getSetting(setting_id)

    def set_string(self, setting_id, value):
        self._appbinder.setSetting(setting_id, value)

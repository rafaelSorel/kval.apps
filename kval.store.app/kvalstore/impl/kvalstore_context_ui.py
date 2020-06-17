__author__ = 'kval team'

from six import string_types

from kval import DialogBox as Dialog
from kval import DialogProgress

class KvalProgressDialog():
    """
    Progress diaglog abstraction class of the Kval progress window.
    """
    def __init__(self, heading, text):
        self._dialog = DialogProgress()
        self._dialog.create(heading, text)
        self._total = 100
        self._position = 1
        self.update(steps=-1)

    def get_total(self):
        return self._total

    def get_position(self):
        return self._position

    def set_total(self, total):
        self._total = int(total)

    def close(self):
        if self._dialog:
            self._dialog.close()
            self._dialog = None

    def update(self, steps=1, text=None):
        self._position += steps
        position = int((100 * self._position) / self._total)
        if isinstance(text, string_types):
            self._dialog.update(position, text)
        else:
            self._dialog.update(position)

    def is_aborted(self):
        return self._dialog.iscanceled()

class KvalStoreCtxUI():
    """
    UI abstraction class of the Kval main UI
    """
    def __init__(self, context):
        self._context = context

    def create_progress_dialog(self, heading, text=None, background=False):
        return KvalProgressDialog(heading, text)

    def on_keyboard_input(self, title, default='', hidden=False):
        dialog = Dialog()
        result = dialog.input(title, self._context.to_unicode(default), hidden=hidden)
        if result:
            self._context.log_info("Reply success: " + result)
            text = self._context.to_unicode(result)
            return True, text

        self._context.log_error("Reply Failed: " + result)
        return False, u''


    def on_numeric_input(self, title, default=''):
        return self.on_keyboard_input(title, default)

    def on_yes_no_input(self, title, text, nolabel='Non', yeslabel='Oui'):
        dialog = Dialog()
        return dialog.yesNoBox(title, text, nolabel=nolabel, yeslabel=yeslabel)

    def on_ok(self, title, text):
        dialog = Dialog()
        return dialog.okBox(title, text)

    def on_remove_content(self, content_name):
        text = self._context.localize(constants.localize.REMOVE_CONTENT) % \
                                      self._context.to_unicode(content_name)
        return self.on_yes_no_input( \
               self._context.localize(constants.localize.CONFIRM_REMOVE), 
               text)

    def on_delete_content(self, content_name):
        text = self._context.localize(constants.localize.DELETE_CONTENT) % \
               self._context.to_unicode(content_name)
        return self.on_yes_no_input( \
               self._context.localize(constants.localize.CONFIRM_DELETE),
               text)

    def on_select(self, title, items=[]):
        _dict = {}
        _items = []
        i = 0
        for item in items:
            if isinstance(item, tuple):
                _dict[i] = item[1]
                _items.append(item[0])
            else:
                _dict[i] = i
                _items.append(item)

            i += 1

        dialog = Dialog()
        result = dialog.listInput(title, _items)
        return _dict.get(result, -1)

    def show_notification(self,
                          message,
                          header='',
                          image_uri='',
                          time_milliseconds=5000):
        _header = header
        if not _header:
            _header = self._context.get_name()
        _header = self._context.to_unicode(_header)

        _image = image_uri
        if not _image:
            _image = self._context.get_icon()

        _message = self._context.to_unicode(message)
        _message = _message.replace(',', ' ')
        _message = _message.replace('\n', ' ')

        self._context.get_appbinder().displayMessageUI(_header,
                                                       _message,
                                                       timeout=time_milliseconds,
                                                       icon=_image)

    def open_settings(self):
        self._context.log_info("open_settings requested ...")

    def refresh_container(self):
        self._context.log_info("refresh_container ...")
        self._context.get_appbinder().executebuiltin("Container.Refresh")

    def set_display_mode(self, mode="1", submode="1"):
        self._context.log_info("Container SetViewMode ...")
        self._context.get_appbinder().executebuiltin("Container.SetViewMode(%s, %s)" % (mode, submode))

    @staticmethod
    def set_home_window_property(property_id, value):
        property_id = 'kval.store.app-' + property_id 
        print("set_home_window_property requested: " + property_id + ": " + value)

    @staticmethod
    def get_home_window_property(property_id):
        property_id = 'kval.store.app-' + property_id
        print("get_home_window_property requested: " + property_id)
        return None

    @staticmethod
    def clear_home_window_property(property_id):
        property_id = 'kval.store.app-' + property_id
        print("clear_home_window_property requested: " + property_id)

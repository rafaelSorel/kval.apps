__author__ = 'kval team'

from kval import ItemUi as Item
from traceback import print_exc
from ..items import *
from ..provider import KvalException

def _process_string_value(info_labels, name, param):
    if param is not None:
        info_labels[name] = param

class KvalStoreRunner():
    def __init__(self):
        self.handle = None
        self.settings = None

    def run(self, provider, context=None):
        results = None

        try:
            results = provider.navigate(context)
        except:
            print_exc()
            return

        self.handle = context.get_handle()
        self.settings = context.get_settings()
        self.appbinder = context.get_appbinder()

        result = results[0]
        options = {}
        options.update(results[1])
        context.log_info("Fill out dir/video/image ...")
        if isinstance(result, bool) and not result:
            context.log_error("endOfDirectory(self.handle, succeeded=False)")
            self.appbinder.endOfCategory(self.handle if self.handle else "",
                                          succeeded=False)
        elif isinstance(result, DirectoryItem):
            context.get_ui().set_display_mode(mode=context.get_display_mode(),
                                              submode=context.get_display_submode())
            self._add_directory(context, result)
        elif isinstance(result, list):
            item_count = len(result)
            if item_count > 0:
                context.get_ui().set_display_mode(mode=context.get_display_mode(),
                                          submode=context.get_display_submode())
            for item in result:
                if isinstance(item, DirectoryItem):
                    self._add_directory(context, item, item_count)

            self.appbinder.endOfCategory(self.handle if self.handle else "",
                                          succeeded=True)
        else:
            # handle exception
            pass

    def _add_directory(self, context, directory_item, item_count=0):

        context.log_info("==== add_directory ====")

        item = Item(label=directory_item.get_name())
        
        if directory_item.get_context_menu() is not None:
            item.addContextMenuItems(directory_item.get_context_menu(),
                                     replaceItems=directory_item.replace_context_menu())

        info_labels = {}
        if isinstance(directory_item, DirectoryItem):
            _process_string_value(info_labels, 'plot', directory_item.get_plot())
            _process_string_value(info_labels, 'date', directory_item.get_date())
            _process_string_value(info_labels, 'studio', directory_item.get_studio())

        item.setInfo(type=u'video', infoLabels=info_labels)
        iconImg = directory_item.get_image() if directory_item.get_image() != '' \
                    else context.create_resource_path(u'media',
                                                      u'DefaultFolder.png')
        thumdir = directory_item.get_thumb()
        if thumdir == '':
            thumdir= \
            context.create_resource_path(u'media',
            u'thumbnail.png' if (context.get_display_submode() is '1') else u'thumbnailRectWare.png')

        item.setArt({'icon': iconImg,
                     'thumb': thumdir,
                     'fanart': directory_item.get_fanart()})

        context.log_info("url: "+directory_item.get_uri())
        context.log_info("icon: "+iconImg)
        
        self.appbinder.addItem(handle=self.handle,
                               url=directory_item.get_uri(),
                               item=item,
                               isFolder=directory_item.isFolder(),
                               totalItems=item_count)

    def _add_video(self, context, video_item, item_count=0):
        context.log_info("==== _add_video ====")

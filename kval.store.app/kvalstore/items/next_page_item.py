__author__ = 'bromix'

from .directory_item import DirectoryItem


class NextPageItem(DirectoryItem):
    def __init__(self, context, current_page=1, image=None, fanart=None):
        new_params = {}
        new_params.update(context.get_params())
        new_params['page'] = str(current_page + 1)
        name = context.localize("Next Page", 'Next Page')
        if name.find('%d') != -1:
            name %= current_page + 1

        if not image or image == '':
            image = context.create_resource_path(u'media', u'nextPage.png')

        DirectoryItem.__init__(self, name, context.create_uri(context.get_path(), new_params), image=image)
        if fanart:
            self.set_fanart(fanart)
        else:
            self.set_fanart(context.get_fanart())

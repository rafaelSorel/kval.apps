__author__ = 'kval team'

from .directory_item import DirectoryItem


class FavoritesItem(DirectoryItem):
    def __init__(self, context, alt_name=None, image=None, fanart=None):
        name = alt_name
        if not name:
            name = context.localize("Favorites")

        if image is None:
            image = context.create_resource_path('media/favorites.png')

        DirectoryItem.__init__(self, name, context.create_uri(["fovorites", 'list']), image=image)
        if fanart:
            self.set_fanart(fanart)
        else:
            self.set_fanart(context.get_fanart())

from .base_item import BaseItem


class DirectoryItem(BaseItem):
    def __init__(self, name, uri, image=u'', fanart=u''):
        BaseItem.__init__(self, name, uri, image, fanart)
        self._plot = name
        self._thumb = ''
        self._isFolder = True

    def set_name(self, name):
        self._name = name

    def set_plot(self, plot):
        self._plot = plot

    def set_thumb(self, thumb):
        self._thumb = thumb

    def get_thumb(self):
        return self._thumb

    def get_plot(self):
        return self._plot

    def set_isFolder(self, isFolder):
        self._isFolder = isFolder

    def isFolder(self):
        return self._isFolder

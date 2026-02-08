"""Custom drag content type to prevent desktop auto-launch."""

from gi.repository import GObject


class AppImageDragContent(GObject.Object):
    """Custom GObject for drag-drop that desktop won't auto-process."""

    __gtype_name__ = "AppImageDragContent"

    file_path = GObject.Property(type=str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

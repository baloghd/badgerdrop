"""AppImage parsing service."""

from pathlib import Path

from badgerdrop.appimage import AppImageInfo, AppImageParser
from badgerdrop.services.errors import AppImageServiceError


class AppImageService:
    """Service for parsing AppImage files.

    This service handles the parsing of AppImage files, extracting metadata
    like name, icon, and desktop entry information.
    """

    def __init__(self, debug: bool = False):
        """Initialize the AppImage service.

        Args:
            debug: Enable debug output
        """
        self.debug = debug

    def parse_appimage(self, file_path: str) -> AppImageInfo:
        """Parse an AppImage file and extract metadata.

        Args:
            file_path: Path to the AppImage file

        Returns:
            AppImageInfo containing parsed metadata

        Raises:
            AppImageServiceError: If the file is not an AppImage or parsing fails
        """
        path = Path(file_path)

        # Validate file extension
        if not path.suffix.lower() == ".appimage" and not path.name.endswith(
            ".AppImage"
        ):
            raise AppImageServiceError("Not an AppImage file")

        try:
            # Parse the AppImage
            parser = AppImageParser(file_path, debug=self.debug)
            info = parser.parse()
            return info

        except Exception as e:
            raise AppImageServiceError(f"Failed to parse AppImage: {e}") from e

    def validate_appimage(self, file_path: str) -> bool:
        """Check if a file is a valid AppImage without full parsing.

        Args:
            file_path: Path to check

        Returns:
            True if the file appears to be an AppImage
        """
        path = Path(file_path)
        return path.suffix.lower() == ".appimage" or path.name.endswith(".AppImage")

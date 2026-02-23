"""Utilities for desktop integration."""

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class DesktopIntegrationError(Exception):
    """Exception raised for desktop integration errors."""

    pass


class DesktopIntegration:
    """Utility for desktop integration operations.

    Provides methods for revealing files in the file manager and
    opening files with their default applications.
    """

    @staticmethod
    def reveal_in_file_manager(path: Path) -> None:
        """Open the file manager to show the specified file or directory.

        Uses xdg-open to open the parent directory of the given path.

        Args:
            path: Path to the file or directory to reveal

        Raises:
            DesktopIntegrationError: If the file manager cannot be opened
        """
        if not path.exists():
            raise DesktopIntegrationError(f"Path does not exist: {path}")

        target = path.parent if path.is_file() else path

        logger.debug("Opening folder: %s", target)

        try:
            result = subprocess.run(
                ["xdg-open", str(target)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                logger.warning("xdg-open returned non-zero: %s", result.stderr)
        except FileNotFoundError as err:
            raise DesktopIntegrationError("xdg-open not found") from err
        except Exception as e:
            raise DesktopIntegrationError(f"Failed to open file manager: {e}") from e

    @staticmethod
    def open_file(path: Path) -> None:
        """Open a file with its default application.

        Args:
            path: Path to the file to open

        Raises:
            DesktopIntegrationError: If the file cannot be opened
        """
        if not path.exists():
            raise DesktopIntegrationError(f"File does not exist: {path}")

        logger.debug("Opening file: %s", path)

        try:
            result = subprocess.run(
                ["xdg-open", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                logger.warning("xdg-open returned non-zero: %s", result.stderr)
        except FileNotFoundError as err:
            raise DesktopIntegrationError("xdg-open not found") from err
        except Exception as e:
            raise DesktopIntegrationError(f"Failed to open file: {e}") from e

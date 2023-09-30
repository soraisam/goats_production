# Standard library imports.
import io
from typing import Any

# Related third party imports.
import astropy
from astropy.utils.console import ProgressBarOrSpinner
from astroquery import log
from astroquery.query import BaseQuery
from astroquery.gemini import ObservationsClass

# Local application/library specific imports.


class BaseQueryExtension(BaseQuery):
    """Extends astroquery BaseQuery."""
    def _download_file_content(self, url: str, timeout: int | None = None,
                               auth: dict[str, Any] | None = None, method: str | None = "GET", **kwargs
                               ) -> bytes:
        """Download content from a URL and return it. Resembles
        `_download_file` but returns the content instead of saving it to a
        local file.

        Parameters
        ----------
        url : `str`
            The URL from where to download the file.
        timeout : `int | None`
            Time in seconds to wait for the server response, by default
            ``None``.
        auth : `dict[str, Any] | None`
            Authentication details, by default ``None``.
        method : `str | None`
            The HTTP method to use, by default "GET".

        Returns
        -------
        `bytes`
            The downloaded content.
        """

        response = self._session.request(method, url, timeout=timeout, auth=auth, **kwargs)
        response.raise_for_status()

        if 'content-length' in response.headers:
            length = int(response.headers['content-length'])
            if length == 0:
                log.warn('URL {0} has length=0'.format(url))
        else:
            length = None

        blocksize = astropy.utils.data.conf.download_block_size
        bytes_read = 0
        content = b""

        # Only show progress bar if logging level is INFO or lower.
        if log.getEffectiveLevel() <= 20:
            progress_stream = None  # Astropy default
        else:
            progress_stream = io.StringIO()

        with ProgressBarOrSpinner(length, f'Downloading URL {url} ...', file=progress_stream) as pb:
            for block in response.iter_content(blocksize):
                content += block
                bytes_read += len(block)
                if length is not None:
                    pb.update(bytes_read if bytes_read <= length else length)
                else:
                    pb.update(bytes_read)

        response.close()

        return content


class GOAClass(ObservationsClass, BaseQueryExtension):
    """GOAClass is responsible for handling operations related to the Gemini
    Observatory Archive (GOA).
    """
    def logout(self) -> None:
        """Logout from the GOA service by deleting the specific session cookie
        and updating the authentication state.
        """
        # Delete specific cookie.
        cookie_name = "gemini_archive_session"
        if cookie_name in self._session.cookies:
            del self._session.cookies[cookie_name]

        # Update authentication state.
        self._authenticated = False

    def get_file_content(self, url, timeout: int | None = None, auth: dict[str, Any] | None = None,
                         method: str | None = "GET", **kwargs) -> bytes:
        """Download the file content from a given URL.

        Parameters
        ----------
        url : `str`
            The URL from where to download the file.
        timeout : `int | None`
            Time in seconds to wait for the server response, by default
            ``None``.
        auth : `dict[str, Any] | None`
            Authentication details, by default ``None``.
        method : `str | None`
            The HTTP method to use, by default "GET".

        Returns
        -------
        `bytes`
            The downloaded file content.
        """
        return self._download_file_content(url, timeout=timeout, auth=auth, method=method, **kwargs)

    def get_file_url(self, filename: str) -> str:
        """Generate the file URL based on the filename.

        Parameters
        ----------
        filename : `str`
            The name of the file.

        Returns
        -------
        `str`
            The URL where the file can be downloaded.
        """
        return f"https://archive.gemini.edu/file/{filename}"


# Instantiate the GOAClass.
GOA = GOAClass()

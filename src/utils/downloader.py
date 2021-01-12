import json
from collections import UserDict

import requests
import requests_cache
import yaml

requests_cache.install_cache('.downloader_cache')

class DownloadError(Exception):
    """Error fetching data from url"""

class SchemaDownloader():
    """
    Schema Downloader and download util for metadata
    """

    def __init__(self):
        self.schemas = {}

    def register(self, name, url):
        """
        register a validation schema by url and name
        """
        self.schemas[name] = self.download_schema(url)

    @staticmethod
    def download(url):
        """
        get json/yaml api metadata by url
        """
        try:
            res = requests.get(url, timeout=5)
        except requests.exceptions.RequestException as err:
            raise DownloadError(f'Failed URL request: {str(err)}')
        if res.status_code != 200:
            raise DownloadError(f'Failed URL request with status: {res.status_code}')
        try:
            metadata = res.json()
        except ValueError:
            try:
                metadata = yaml.load(res.text, Loader=yaml.SafeLoader)
            except (yaml.scanner.ScannerError, yaml.parser.ParserError) as err:
                raise DownloadError(f'Invalid Format: {str(err)}')

        data = UserDict(metadata)
        data.etag = res.headers.get('ETag', 'I').strip('W/"')
        return data

    def download_schema(self, url):
        """
        get json/yaml validation schema by url
        """
        data = requests.get(url).text
        if data.startswith("export default "):
            data = data[len("export default "):]
        try:
            schema = json.loads(data)
        except ValueError:
            try:
                schema = yaml.load(data, Loader=yaml.SafeLoader)
            except (yaml.scanner.ScannerError, yaml.parser.ParserError) as err:
                raise DownloadError(f'Invalid Format: {str(err)}')
        if schema:
            return schema

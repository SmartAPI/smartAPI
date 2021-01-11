import json

import requests
import requests_cache
import yaml

class DownloadError(Exception):
    """Error fetching data from url"""

class SchemaDownloader():
    """
    Schema Downloader and download util for metadata
    """

    def __init__(self, cache):
        requests_cache.install_cache(cache)
        self.schemas = {}
        self.v2_schemas = {}

    def register(self, name, url, v='v3'):
        """
        register a validation schema by url, name and version
        """
        if v == 'v3':
            self.schemas[name] = self.download_schema(url)
        else:
            self.v2_schemas[name] = self.download_schema(url)

    def get_schemas(self, v='v3'):
        """
        get version registered validation schemas
        """
        if v == 'v3':
            return self.schemas
        else:
            return self.v2_schemas

    @staticmethod
    def download(url, etag_only=False):
        """
        get json/yaml api metadata by url
        """
        try:
            res = requests.get(url, timeout=5)
            if etag_only:
                return res.headers.get('ETag', 'I').strip('W/"')

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
        return metadata

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

import json

import requests
import requests_cache
import yaml

class RegistryError(Exception):
    """Redefined Error to avoid circular dependency"""

class SchemaDownloader():
    """
    Schema Downloader and download util for metadata
    """

    def __init__(self):
        requests_cache.install_cache('smartapi_downloader_cache')
        self.schemas = {}

    def register(self, name, url):
        """
        register a validation schema by url and name
        """
        self.schemas[name] = self.download_schema(url)

    def get_schemas(self):
        """
        get all registered validation schemas
        """
        return self.schemas

    # def get_schema(self):
    #     schema = requests.get(SWAGGER2_SCHEMA_URL).text
    #     if schema.startswith("export default "):
    #         schema = schema[len("export default "):]
    #     try:
    #         self.oas_schema = json.loads(schema)
    #     except Exception:
    #         self.oas_schema = yaml.load(schema, Loader=yaml.SafeLoader)

    @staticmethod
    def download(url):
        """
        get json/yaml api metadata by url
        """
        try:
            res = requests.get(url, timeout=5)
        except requests.exceptions.RequestException as err:
            raise RegistryError(f'Failed URL request: {str(err)}')
        if res.status_code != 200:
            raise RegistryError(f'Failed URL request with status: {res.status_code}')
        try:
            metadata = res.json()
        except ValueError:
            try:
                metadata = yaml.load(res.text, Loader=yaml.SafeLoader)
            except (yaml.scanner.ScannerError, yaml.parser.ParserError) as err:
                raise RegistryError(f'Invalid Format: {str(err)}')
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
                raise RegistryError(f'Invalid Format: {str(err)}')
        if schema:
            return schema

    @staticmethod
    def get_etag(url):
        try:
            res = requests.get(url).headers.get('ETag', 'I').strip('W/"')
        except BaseException:
            return False
        return res

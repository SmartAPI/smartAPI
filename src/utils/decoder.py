""" Stream Decoder """

import gzip
import json

import yaml

# -------------
#  Conversion
# -------------

TYPE_ERR = "Expect a serialization of a mapping type."


def to_yaml(stream):
    try:
        data = yaml.load(stream, Loader=yaml.SafeLoader)
    except (yaml.scanner.ScannerError, yaml.parser.ParserError) as err:
        raise ValueError(str(err)) from err
    if not isinstance(data, dict):
        raise TypeError(TYPE_ERR)
    return data


def to_json(stream):
    try:
        data = json.loads(stream)
    except json.JSONDecodeError as err:
        raise ValueError(str(err)) from err
    if not isinstance(data, dict):
        raise TypeError(TYPE_ERR)
    return data


def to_dict(stream, ext=None, ctype=None):
    """
    Load a string or bytes to a dict.
    If extension or content-type is specified,
    only parse stream as the specified format.
    """

    ext = ext.lower() if isinstance(ext, str) else ""
    ctype = ctype.lower() if isinstance(ctype, str) else ""

    # by extension
    if "json" in ext:
        return to_json(stream)
    if ext in ("yaml", "yml"):
        return to_yaml(stream)

    # by content-type
    if "json" in ctype:
        return to_json(stream)
    if "yaml" in ctype:
        return to_yaml(stream)

    # javascript files
    if isinstance(stream, bytes):
        try:
            stream = stream.decode()
        except UnicodeDecodeError:
            pass
    if isinstance(stream, str):
        if stream.startswith("export default "):
            stream = stream[len("export default ") :]

    # brute force
    return to_yaml(stream)


# -------------
# Compression
# -------------


def compress(stream):
    return gzip.compress(stream) if stream else None


def decompress(stream):
    return gzip.decompress(stream) if stream else None

from typing import Union, List
import bmt

# Initialize the Biolink Model Toolkit instance globally if it's used frequently
# or pass it as a parameter to functions that require it.
toolkit = bmt.Toolkit()

def get_expanded_values(value: Union[str, List[str]], toolkit_instance=toolkit) -> List[str]:
    """Return expanded value list for a given Biolink class name."""
    if isinstance(value, str):
        value = [value]
    _out = []
    for v in value:
        try:
            v = toolkit_instance.get_descendants(v, reflexive=True, formatted=True)
            v = [x.split(":")[-1] for x in v]  # Remove 'biolink:' prefix
        except ValueError:
            v = [v]
        _out.extend(v)
    return _out

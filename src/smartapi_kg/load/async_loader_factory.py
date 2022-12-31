from .single_spec_async_loader import SingleSpecAsyncLoader
from .team_specs_async_loader import TeamSpecsAsyncLoader
from .all_specs_async_loader import AllSpecsAsyncLoader
from .tag_specs_async_loader import TagSpecsAsyncLoader
from .component_specs_async_loader import ComponentSpecsAsyncLoader


def async_loader_factory(smart_API_id, team_name, tag, component):
    if smart_API_id:
        loader = SingleSpecAsyncLoader(smart_API_id)
    elif team_name:
        loader = TeamSpecsAsyncLoader(team_name)
    elif tag:
        loader = TagSpecsAsyncLoader(tag)
    elif component:
        loader = ComponentSpecsAsyncLoader(component)
    else:
        loader = AllSpecsAsyncLoader()

    specs = loader.load()
    return specs

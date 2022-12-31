from .single_spec_sync_loader import SingleSpecSyncLoader
from .team_specs_sync_loader import TeamSpecsSyncLoader
from .all_specs_sync_loader import AllSpecsSyncLoader
from .tag_specs_sync_loader import TagSpecsSyncLoader
from .component_specs_sync_loader import ComponentSpecsSyncLoader
from .api_names_specs_sync_loader import APINamesSpecsSyncLoader


def sync_loader_factory(smart_API_id, team_name, tag, component, api_names, path):
    if smart_API_id:
        loader = SingleSpecSyncLoader(smart_API_id, path)
    elif team_name:
        loader = TeamSpecsSyncLoader(team_name, path)
    elif tag:
        loader = TagSpecsSyncLoader(tag, path)
    elif component:
        loader = ComponentSpecsSyncLoader(component, path)
    elif isinstance(api_names, list):
        loader = APINamesSpecsSyncLoader(api_names, path)
    else:
        loader = AllSpecsSyncLoader(path)

    return loader.load()

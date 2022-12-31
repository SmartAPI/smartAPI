from .all_specs_sync_loader import AllSpecsSyncLoader


class TeamSpecsSyncLoader(AllSpecsSyncLoader):
    _team_name = ''

    def __init__(self, team_name, path):
        super().__init__(path)
        self._team_name = team_name

    def filter_hits(self, item):
        return "x-translator" in item['info'] and "team" in item['info']["x-translator"] \
               and isinstance(item['info']["x-translator"]['team'], list) \
               and self._team_name in item['info']["x-translator"]['team']

    def parse(self, _input):
        filtered_hits = filter(self.filter_hits, _input['hits'])
        return filtered_hits

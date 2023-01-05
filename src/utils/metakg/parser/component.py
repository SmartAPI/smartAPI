class Components:
    components = {}

    def __init__(self, components):
        self.components = components

    def fetch(self, obj, key):
        if key in ['#', 'components']:
            return obj
        if obj and key in obj:
            return obj[key]
        return None

    def fetch_component_by_ref(self, ref):
        if ref.startswith('#/components/'):
            if ref[-1] == '/':
                ref = ref[0:-1]
            res = self.components
            paths = ref.split('/')
            try:
                for ele in paths:
                    res = self.fetch(res, ele)
            except Exception as e:
                return None
            return res
        return None

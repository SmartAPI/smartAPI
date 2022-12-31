class QueryOperationObject:
    _params = {}
    _request_body = {}
    _support_batch = None
    _input_separator = ''
    _path = ''
    _method = ''
    _server = ''
    _tags = []
    _path_params = []

    @property
    def xBTEKGSOperation(self):
        return {
            'params': self._params,
            'request_body': self._request_body,
            'support_batch': self._support_batch,
            'input_separator': self._input_separator,
        }

    @xBTEKGSOperation.setter
    def xBTEKGSOperation(self, new_op):
        if not isinstance(new_op, str):
            self._params = new_op.get('parameters')
            self._request_body = new_op.get('request_body') or new_op.get('requestBody')
            self._support_batch = new_op.get('supportBatch')
            self._input_separator = new_op.get('inputSeparator')

    @property
    def params(self):
        return self._params

    @property
    def request_body(self):
        return self._request_body

    @property
    def support_batch(self):
        return self._support_batch

    @property
    def input_separator(self):
        return self._input_separator

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, new_path):
        self._path = new_path

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, new_method):
        self._method = new_method

    @property
    def server(self):
        return self._server

    @server.setter
    def server(self, new_server):
        self._server = new_server

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, new_tags):
        self._tags = new_tags

    @property
    def path_params(self):
        return self._path_params

    @path_params.setter
    def path_params(self, new_path_params):
        self._path_params = new_path_params

    def to_dict(self):
        d = {}
        for attr in [
            "params", "request_body", "path_params", "path",
            "method", "server", "tags", "support_batch", "input_separator"
        ]:
            val = getattr(self, attr, None)
            if val:
                d[attr] = val
        return d

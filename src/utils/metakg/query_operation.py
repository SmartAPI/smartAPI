class QueryOperationObject:
    _params = {}
    _request_body = {}
    _support_batch = None
    _input_separator = ""
    _path = ""
    _method = ""
    _server = ""
    _tags = []
    _path_params = []
    _agent_type = None
    _knowledge_level = None
    _testExamples = []
    _useTemplating = None

    @property
    def xBTEKGSOperation(self):
        return {
            "params": self._params,
            "request_body": self._request_body,
            "support_batch": self._support_batch,
            "input_separator": self._input_separator,
        }

    @xBTEKGSOperation.setter
    def xBTEKGSOperation(self, new_op):
        if not isinstance(new_op, str):
            self._params = new_op.get("parameters")
            self._request_body = new_op.get("request_body") or new_op.get("requestBody")
            self._support_batch = new_op.get("supportBatch")
            self._input_separator = new_op.get("inputSeparator")

    @property
    def agent_type(self):
        return self._agent_type

    @agent_type.setter
    def agent_type(self, new_agent_type):
        self._agent_type = new_agent_type

    @property
    def knowledge_level(self):
        return self._knowledge_level

    @knowledge_level.setter
    def knowledge_level(self, new_knowledge_level):
        self._knowledge_level = new_knowledge_level

    @property
    def testExamples(self):
        return self._testExamples

    @testExamples.setter
    def testExamples(self, new_testExamples):
        self._testExamples = new_testExamples

    @property
    def useTemplating(self):
        return self._useTemplating

    @useTemplating.setter
    def useTemplating(self, new_useTemplating):
        self._useTemplating = new_useTemplating

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
            "params",
            "request_body",
            "path_params",
            "path",
            "method",
            "server",
            "tags",
            "support_batch",
            "input_separator",
            "agent_type",
            "knowledge_level",
            "testExamples",
            "useTemplating",
        ]:
            val = getattr(self, attr, None)
            if val:
                d[attr] = val
        return d

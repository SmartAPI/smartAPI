TEST1 = """{
    "openapi": "3.0.0",
    "info": {
        "version": "1.0",
        "title": "DATE API",
        "description": "Web API to query DATE data stored in MySQL. Primary features are MySQL-like syntax for filtering database table rows and the ability to perform JOINs remotely.",
        "contact": {
            "name": "Joseph D. Romano",
            "x-role": "responsible developer",
            "email": "jdr2160@cumc.columbia.edu",
            "x-id": "https://github.com/JDRomano2"
        },
        "termsOfService": "https://github.com/JDRomano2/ncats-apis/blob/master/date/terms.md"
    },
    "servers": [
        {
            "url": "http://date.nsides.io",
            "description": "Production server"
        }
    ],
    "tags": [
        {
            "name": "translator"
        }
    ],
    "paths": {
        "/api/{tablename}": {
            "get": {
                "summary": "Prints contents of {tablename} by row",
                "responses": {
                    "200": {
                        "description": "JSON-formatted list where each element is a JSON object where keys are table columns and values are the corresponding cell values. Users can pass parameters with a MySQL-like syntax to perform filtering within the table."
                    }
                },
                "parameters": [
                    {
                        "name": "tablename",
                        "in": "path",
                        "required": true,
                        "description": "One of the table names documented at http://date.nsides.io, or liste in the response to '/api/tables'.",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "_fields",
                        "in": "query",
                        "description": "One or more table columns to include in the query's response. If omitted, all table columns will be returned in the response.",
                        "required": false,
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "_where",
                        "in": "query",
                        "description": "One or more tuples delimited by logical operators, where each tuple is a comparison applied to a specific table column. Follows syntax specifications described at https://github.com/o1lab/xmysql#row-filtering--where",
                        "required": false,
                        "schema": {
                            "type": "string"
                        }
                    }
                ]
            }
        }
    }
}
"""

TEST2 = """
{
    "openapi": "3.0.2",
    "info": {
        "title": "Automat Panther",
        "version": "1.0.0",
        "x-translator": {
            "component": "KP",
            "teams": [
                "Ranker"
            ]
        },
        "contact": {
            "email": "kebedey@renci.org",
            "name": "Yaphet Kebede",
            "x-id": "https://github.com/yaphetkg",
            "x-role": "contributor"
        },
        "termsOfService": "http://linkmissing"
    },
    "servers": [
        {
            "description": "Default server",
            "url": "https://automat.renci.org/panther"
        }
    ],
    "tags": [
        {
            "name": "translator"
        },
        {
            "name": "automat"
        }
    ],
    "paths": {
        "/query": {
            "post": {
                "tags": [
                    "translator"
                ],
                "summary": "Query Reasoner API",
                "description": "Given a question graph return question graph plus answers.",
                "operationId": "reasoner_api_query_post",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "title": "Request",
                                "allOf": [
                                    {
                                        "$ref": "#/components/schemas/Request"
                                    }
                                ],
                                "example": {
                                    "message": {
                                        "query_graph": {
                                            "nodes": [
                                                {
                                                    "id": "n0",
                                                    "type": "biolink:Cell"
                                                }
                                            ],
                                            "edges": []
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "required": true
                },
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Message"
                                }
                            }
                        }
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPValidationError"
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "components": {
        "schemas": {
            "CypherDatum": {
                "title": "CypherDatum",
                "required": [
                    "row",
                    "meta"
                ],
                "type": "object",
                "properties": {
                    "row": {
                        "title": "Row",
                        "type": "array",
                        "items": {}
                    },
                    "meta": {
                        "title": "Meta",
                        "type": "array",
                        "items": {}
                    }
                }
            }
        }
    }
}
"""
import smartapi from '../../assets/img/logo-large-text.svg';
import bte from '../../assets/img/biothings-explorer-2.svg';
import translator from '../../assets/img/TranslatorLogo.jpg';

export const extensions = {
  state: () => ({
    extensions: {
      smartapi: {
        description:
          'The SmartAPI project aims to maximize the FAIRness (Findable, Accessible, Interoperable, Reusable) of web-based Application Programming Interfaces (APIs).',
        link: 'https://smart-api.info',
        image: smartapi,
        extensions: [
          {
            name: 'version',
            necessity: 'required',
            description:
              'The version of the API definition. Specify API version using Semantic Versioning. The major.minor portion of the semver (for example 3.0) shall designate the feature set. Typically, .patch versions address errors in the API metadata, not the feature set.',
            doc_link: 'https://semver.org/spec/v2.0.0.html',
            type: 'STRING',
            example: {
              info: {
                version: '3.0'
              }
            }
          },
          {
            name: 'termsOfService',
            necessity: 'required',
            description: 'A list of external resources pertinent to the API.',
            doc_link: 'https://semver.org/spec/v2.0.0.html',
            type: 'URL',
            example: {
              info: {
                termsOfService: 'http://mygene.info/terms/'
              }
            }
          },
          {
            name: 'x-role',
            necessity: 'required',
            description:
              'Indicate the role of the contact. Values can be: responsible organization,responsible developer,contributor,support.',
            enum: ['responsible organization', 'responsible developer', 'contributor', 'support'],
            doc_link: '',
            type: 'ENUM',
            example: {
              info: {
                'x-role': 'responsible developer'
              }
            }
          },
          {
            name: 'summary',
            necessity: 'required',
            description: '',
            doc_link: '',
            type: 'STRING',
            example: {
              info: {
                summary: 'your text'
              }
            }
          },
          {
            name: 'x-url',
            necessity: 'required',
            description:
              'The URL for the target documentation. Value MUST be in the format of a URL.',
            doc_link: '',
            type: 'URL',
            example: {
              info: {
                'x-url': 'your text'
              }
            }
          },
          {
            name: 'x-type',
            necessity: 'required',
            description:
              'Values: api documentation, website,developer forum,mailing list,social media,publication',
            enum: [
              'api documentation',
              'website',
              'developer forum',
              'mailing list',
              'social media',
              'publication'
            ],
            doc_link: '',
            type: 'ENUM',
            example: {
              info: {
                'x-type': 'api documentation'
              }
            }
          },
          {
            name: 'description',
            necessity: 'should',
            description:
              'A short description of the target documentation. CommonMark syntax can be used for rich text representation.',
            doc_link: '',
            type: 'STRING',
            example: {
              info: {
                description: 'your text'
              }
            }
          },
          {
            name: 'x-id',
            necessity: 'should',
            description: 'The name of the tag. Recommend that you use URI to specify the concept.',
            doc_link: '',
            type: 'URI',
            example: {
              info: {
                'x-id': 'https://github.com/newgene'
              }
            }
          },
          {
            name: 'x-parameterType',
            necessity: 'should',
            description: 'A concept URI to describe the type of parameter.',
            doc_link:
              'https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md#parameterObject',
            type: 'URI',
            example: {
              name: 'username',
              in: 'path',
              description: 'username to fetch',
              required: true,
              schema: {
                type: 'string',
                example: 'bob1234',
                default: 'anonymous'
              },
              'x-parameterType': 'http://example.org/username',
              'x-valueType': 'http://example.org/facebookid'
            }
          },
          {
            name: 'x-valueType',
            necessity: 'should',
            description:
              'A list of URIs to define the types of accepted value types. These should be selected from a registry of value types such as identifiers.org. This attribute is different from',
            doc_link: '',
            type: '[URI]',
            example: {
              name: 'username',
              in: 'path',
              description: 'username to fetch',
              required: true,
              schema: {
                type: 'string',
                example: 'bob1234',
                default: 'anonymous'
              },
              'x-parameterType': 'http://example.org/username',
              'x-valueType': 'http://example.org/facebookid'
            }
          },
          {
            name: 'content',
            necessity: 'should',
            description: 'Use media type definitions listed at RFC6838.',
            doc_link: 'https://www.iana.org/assignments/media-types/media-types.xhtml',
            type: 'Map',
            example: {
              description: 'A complex object array response',
              content: {
                'application/json': {
                  schema: {
                    type: 'array',
                    items: {
                      $ref: '#/components/schemas/VeryComplexType'
                    }
                  }
                }
              }
            }
          },
          {
            name: 'x-externalResources',
            necessity: 'optional',
            description: 'A list of external resources pertinent to the API.',
            doc_link: '',
            type: 'MAP',
            example: null
          },
          {
            name: 'x-accessRestriction',
            necessity: 'optional',
            description: 'Indicate whether there are restrictions to using the API.',
            enum: ['none', 'limited', 'fee'],
            doc_link: '',
            type: 'ENUM',
            example: {
              title: 'Sample Pet Store App',
              description: 'This is a sample server for a pet store.',
              termsOfService: 'http://example.com/terms/',
              version: '1.0.1',
              'x-accessRestriction': 'none',
              'x-implementationLanguage': 'python'
            }
          },
          {
            name: 'contacts',
            necessity: 'optional',
            description: 'A list of other contacts.',
            doc_link: '',
            type: 'OBJECT',
            example: {
              contact: {
                name: 'API Support',
                url: 'http://www.example.com/support',
                email: 'support@example.com'
              }
            }
          },
          {
            name: 'x-implementationLanguage',
            necessity: 'optional',
            description: 'Language the API was written in.',
            doc_link: '',
            type: 'STRING',
            example: {
              title: 'Sample Pet Store App',
              description: 'This is a sample server for a pet store.',
              termsOfService: 'http://example.com/terms/',
              version: '1.0.1',
              'x-accessRestriction': 'none',
              'x-implementationLanguage': 'python'
            }
          },
          {
            name: 'x-location',
            necessity: 'optional',
            description: 'Location, city and country of the server hosting the API.',
            doc_link: '',
            type: 'STRING',
            example: {
              url: 'https://development.gigantic-server.com/v1',
              description: 'Development server',
              'x-location': 'California, USA',
              'x-maturity': 'production'
            }
          },
          {
            name: 'x-maturity',
            necessity: 'optional',
            description: 'Maturity of the API. Values to use: development, staging, production.',
            doc_link: '',
            type: 'STRING',
            example: {
              url: 'https://development.gigantic-server.com/v1',
              description: 'Development server',
              'x-location': 'California, USA',
              'x-maturity': 'production'
            }
          },
          {
            name: 'x-description',
            necessity: 'optional',
            description:
              'A short description of the target documentation. CommonMark syntax can be used for rich text representation.',
            doc_link: 'https://spec.commonmark.org/',
            type: 'STRING',
            example: [
              {
                'x-url': 'http://example.org/api/docs',
                'x-type': 'api documentation'
              },
              {
                'x-url': 'https://doi.org/10.1093/nar/gks1114',
                'x-type': 'publication',
                'x-description':
                  'BioGPS and MyGene.info: organizing online, gene-centric information'
              },
              {
                'x-url': 'http://twitter.com/mygeneinfo',
                'x-type': 'social media'
              }
            ]
          },
          {
            name: 'x-uri',
            necessity: 'optional',
            description:
              'Specify the json schema using a Reference Object, or use x-uri as an additional property in the schema field to point to an external location for an XML, RDF, etc schema.',
            doc_link: '',
            type: 'URI',
            example: null
          },
          {
            name: 'x-responseValueType',
            necessity: 'optional',
            description:
              'Specify the types of objects and relations in the response using either a reference to the JSON-LD context file or to a Response Value Type Object.',
            doc_link: '',
            type: 'OBJECT',
            example: null
          },
          {
            name: 'x-path',
            necessity: 'optional',
            description:
              'The path using dot notation to the element of interest. e.g. friend.name to follow the path from root object to the name attribute to the name field',
            doc_link:
              'https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md#responseValueTypeObject',
            type: 'STRING',
            example: [
              {
                'x-path': 'ncbigene.id',
                'x-valueType': 'http://identifiers.org/ncbigene'
              }
            ]
          },
          {
            name: 'x-valueType',
            necessity: 'optional',
            description:
              'The value type for the field. e.g. http://identifiers.org/ncbigene indicates that the field type is from the NCBI Gene database',
            doc_link:
              'https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md#responseValueTypeObjectValue',
            type: 'STRING',
            example: [
              {
                'x-path': 'ncbigene.id',
                'x-valueType': 'http://identifiers.org/ncbigene'
              }
            ]
          }
        ]
      },
      'x-bte': {
        description:
          'BioThings Explorer is an application that creates a federated knowledge graph that is composed of a network of biomedical web services. BioThings Explorer leverages semantically precise annotations of inputs and outputs for each resource, and automates the chaining of web service calls to execute multi-step graph queries.',
        link: 'https://explorer.biothings.io/',
        image: bte,
        extensions: [
          {
            name: 'x-bte-kg-operations',
            necessity: 'optional',
            description:
              'the x-bte-operations can have whatever key / name you want. We tend to use subject-category/predicate-object-category combos as the names.',
            doc_link:
              'https://github.com/biothings/biothings_explorer/blob/main/docs/README-types-of-apis.md#what-is-the-x-bte-annotation-format',
            type: 'OBJECT',
            example: {
              'x-bte-kgs-operations': {
                aeolusTreats: [
                  {
                    supportBatch: true,
                    useTemplating: true,
                    inputs: [
                      {
                        id: 'UNII',
                        semantic: 'SmallMolecule'
                      }
                    ],
                    requestBody: {
                      body: {
                        q: '{{ queryInputs }}',
                        scopes: 'aeolus.unii'
                      }
                    },
                    outputs: [
                      {
                        id: 'MEDDRA',
                        semantic: 'Disease'
                      }
                    ],
                    parameters: {
                      fields: 'aeolus.indications',
                      jmespath: 'aeolus.indications|[?count>`20`]',
                      size: 1000
                    },
                    predicate: 'treats',
                    source: 'infores:aeolus',
                    response_mapping: {
                      $ref: '#/components/x-bte-response-mapping/aeolusIndication-meddra'
                    }
                  }
                ]
              }
            }
          },
          {
            name: 'x-bte-response-mapping',
            necessity: 'optional',
            description:
              "That's where we will map each field in the parameters.fields to the output or another key (that will be used as the name/id of the edge-attribute in BTE).",
            doc_link:
              'https://github.com/biothings/biothings_explorer/blob/main/docs/README-writing-x-bte.md#writing-the-x-bte-response-mapping-section',
            type: 'OBJECT',
            example: {
              'x-bte-response-mapping': {
                'aeolus-unii': {
                  UNII: 'aeolus.unii'
                },
                chebi: {
                  CHEBI: 'chebi.id'
                }
              }
            }
          }
        ]
      },
      'x-translator': {
        description:
          'The platform created by the Consortium members and funded through NCATS’s Other Transactions Authority has been designed as an exploration tool integrating trusted data sources, which aids researchers in discovering novel connections representing biomedical knowledge. The alpha release of Translator allows the user to explore relationships between chemicals/drugs and either diseases or genes.',
        link: 'https://ncats.nih.gov/research/research-activities/translator',
        image: translator,
        extensions: [
          {
            name: 'x-translator',
            necessity: 'should',
            description:
              'This extension is inside the OpenAPI info object and contains basic API-level metadata. Currently, there are two required properties: component (KP, ARA, ARS, or Utility) and team (one or more Translator team names).',
            doc_link:
              'https://github.com/NCATSTranslator/translator_extensions/blob/main/x-translator/smartapi_x-translator_examples.md',
            type: 'OBJECT',
            example: {
              info: {
                'x-translator': {
                  infores: 'infores:mygene-info',
                  component: 'KP',
                  team: ['Service Provider'],
                  'biolink-version': '3.5.0'
                }
              }
            }
          },
          {
            name: 'x-trapi',
            necessity: 'should',
            description:
              'This extension is inside the OpenAPI info object and contains basic API-level metadata. Currently, there are 2 required properties (version and operations).',
            doc_link:
              'https://github.com/NCATSTranslator/translator_extensions/blob/main/x-trapi/smartapi_x-trapi_examples.md',
            type: 'OBJECT',
            example: {
              info: {
                'x-trapi': {
                  operations: ['lookup', 'overlay_connect_knodes', 'annotate_nodes'],
                  version: '1.4.0',
                  test_data_location: {
                    staging: {
                      url: 'https://automat.ci.transltr.io/drugcentral/1.4/sri_testing_data'
                    }
                  }
                }
              }
            }
          }
        ]
      }
    }
  }),
  strict: true,
  getters: {
    extensions: (state) => {
      return state.extensions;
    }
  }
};

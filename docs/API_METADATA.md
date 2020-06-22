##### What is OpenAPI v3?

The OpenAPI Specification (OAS) defines a standard, language-agnostic interface to RESTful APIs which allows both humans and computers to discover and understand the capabilities of the service without access to source code, documentation, or through network traffic inspection. When properly defined, a consumer can understand and interact with the remote service with a minimal amount of implementation logic.

An OpenAPI definition can then be used by documentation generation tools to display the API, code generation tools to generate servers and clients in various programming languages, testing tools, and many other use cases.

##### Useful Tools

You can use [this editor _build_](http://smart-api.info/editor/) to write/edit your API metadata. You can start with an existing metadata example from "[mygene.info](https://github.com/NCATS-Tangerine/translator-api-registry/blob/master/mygene.info/openapi_minimum.yml)" API. The editor automatically validates your API metadata and gives a live preview of auto-generated API documentation.

This [guide](/guide) can also guide through the process/tools on how to create your OpenAPI v3 API metadata or how to upgrade an existing Swagger v2 API metadata to OpenAPI v3.

###### OpenAPI v3 API Metadata Example:

`

<pre>  openapi: '3.0.0'
  info:
    version: '3.0'
    title: MyGene.info API
    description: >-
      Documentation of the MyGene.info Gene Query web services. Learn more about
      [MyGene.info](http://mygene.info/)
    termsOfService: http://mygene.info/terms/
    contact:
      name: Chunlei Wu
      x-role: responsible developer
      email: help@mygene.info
      x-id: 'https://github.com/newgene'
  servers:
    - url: 'http://mygene.info/v3'
      description: 'Production server'
  tags:
    - name: gene
    - name: annotation
    - name: query
    - name: translator
  paths:
    /query:
      get:
        summary: 'Make gene query and return matching gene hits'
        parameters:
          - name: q
            in: query
            description: >-
              Query string. Examples "CDK2", "NM_052827", "204639_at". The
              detailed query syntax can be found at
              http://docs.mygene.info/en/latest/doc/query_service.html
            required: true
            x-valueType:
              - 'http://identifiers.org/hgnc.symbol/'
              - 'http://identifiers.org/refseq/'
              - 'http://identifiers.org/unigene/'
              - 'http://identifiers.org/uniprot/'
              - 'http://identifiers.org/pdb/'
              - 'http://identifiers.org/biocarta.pathway/'
              - 'http://identifiers.org/kegg.pathway/'
              - 'http://identifiers.org/wikipathways/'
              - 'http://identifiers.org/pharmgkb.pathways/'
              - 'http://identifiers.org/reactome/'
            schema:
              type: string
        responses:
          '200':
            description: 'A query response object with "hits" property'
            x-responseValueType:
              - path: hits._id
                valueType: 'http://identifiers.org/ncbigene/'
              - path: hits.entrezgene
                valueType: 'http://identifiers.org/ncbigene/'
              - path: hits.symbol
                valueType: 'http://identifiers.org/hgnc.symbol/'
              - path: hits.taxid
                valueType: 'http://identifiers.org/taxonomy/'
            x-JSONLDContext:
              'https://github.com/NCATS-Tangerine/translator-api-registry/blob/master/mygene.info/jsonld_context/mygene_context.json'
    '/gene/{geneid}':
      get:
        summary: 'For a given gene id, return the matching gene object'
        parameters:
          - name: geneid
            in: path
            description: >-
              Entrez or Ensembl gene id, e.g., 1017, ENSG00000170248\. A retired
              Entrez Gene id works too if it is replaced by a new one, e.g.,
              245794
            required: true
            x-valueType:
              - 'http://identifiers.org/ncbigene/'
              - 'http://identifiers.org/ensembl/'
            schema:
              type: string
        responses:
          '200':
            description: 'A gene object'
            x-responseValueType:
              - path: symbol
                valueType: 'http://identifiers.org/hgnc.symbol/'
              - path: unigene
                valueType: 'http://identifiers.org/unigene/'
              - path: uniprot.Swiss-Prot
                valueType: 'http://identifiers.org/uniprot/'
              - path: pdb
                valueType: 'http://identifiers.org/pdb/'
              - path: pathway.biocarta.id
                valueType: 'http://identifiers.org/biocarta.pathway/'
              - path: pathway.kegg.id
                valueType: 'http://identifiers.org/kegg.pathway/'
              - path: pathway.reactome.id
                valueType: 'http://identifiers.org/reactome/'
              - path: pathway.wikipathways.id
                valueType: 'http://identifiers.org/wikipathways/'
              - path: pathway.pharmgkb.id
                valueType: 'http://identifiers.org/pharmgkb.pathways/'
            x-JSONLDContext:
              'https://github.com/NCATS-Tangerine/translator-api-registry/blob/master/mygene.info/jsonld_context/mygene_context.json'
            </pre>

`

#### Provide semantics for API input and output

###### _x-smartapi_ extension

###### Introduction:

The goal of this extension is to facilitate the automatic retrieval of single-hop knowledge graph data in the format of subject-predicate-object (e.g. ChemicalSubstance – treats – Disease) from APIs by intelligent agents, such as [BioThings Explorer](https://github.com/biothings/biothings_explorer/). This is achieved through documenting single-hop knowledge graph retrieval operations that an individual [OpenAPI operation](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#operation-object) can perform. The knowledge graph retrieval operation should be defined using the [BioLink Data Model](https://biolink.github.io/biolink-model/), e.g. each input/output node should be categorized using Biolink classes and ID prefixes, edges should be labeled using valid Biolink relationship types.

###### Documentation:

[Click here](https://x-bte-extension.readthedocs.io/en/latest/index.html) to learn more about the **x-smartapi** extension.

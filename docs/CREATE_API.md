# General API implementation best practices
Regardless the type of APIs you are implementing, we recommend to follow these API best-practices.


### 1. CORS support
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;An API endpoint should support [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Access_control_CORS) with unrestricted hostnames, so that users can make cross-origin API requests directly from their web application.

### 2. HTTPS support
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;An API endpoint should support HTPPS protocol, ideally both HTTP and HTTPS, so that users can make encrypted API request if needed.

### 3. HTTP compression support
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;An API endpoint should support gzip HTTP compression protocol to reduce the data transfer size.

### 4. HTTP caching support
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;An API endpoint support HTTP caching headers with both “Cache-Control” and “etag” headers (max-age can be adjustable, e.g. set to 7 days).

### 5. Versioning
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; To maintain the backcompatability, versioning your API is preferred. One way is to include the version number in the URLs:
  - Include the version number (as "v1", "v2", "v3", and so on) to the endpoint URLs (e.g. http://myvariant.info/v1/variant endpoint)
  - Increase version number when breaking changes are introduced to the API
  
### 6. Support batch queries
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Batch queries are efficient for a large list of inputs. A typical implementation is to use GET for single query, and POST for the corresponding batch query:
  - GET: perform a single entity-retrieval or a single query
  - POST: perform a batch of entity-retrieval or queries
  
### 7. Support JSON response format
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Typically, an API can return response in JSON format by default. If multiple return formats are available, one can consider to use "content-type" header or explicit query parameter:
  - `Content-Type` header

    When ```Content-Type: application/json``` header is present in the request, the response will be returned as JSON.
    
  - Query parameter:

    For example, when `format=json` query parameter is passed, the response will be returned as JSON.


### 8. Support paging or streaming of the large response

 * If a large response is expected from an API endpoint, the paging or streaming support is preferred. For example, this is a typical paging implementation with both `size` and `from` query parameters:

    * size
       * The maximum number of matching object hits to return
       * Optional, default is 10

    * from
       * The number of matching hits to skip
       * Optional, default is 0
  
   See this live example from [MyGene.info](https://mygene.info) API:

   https://mygene.info/v3/query?q=cdk2&size=50&from=20


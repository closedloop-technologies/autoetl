# API Crawling Notes

We rely heavily on the [OpenAPI v3.1](https://swagger.io/specification/)
specification to describe the API.

https://github.com/OAI/OpenAPI-Specification/tree/main/schemas

This serves as the source of truth for the API as we crawl and explore the API.  We use the OpenAPI specification to generate the code that will interact with the API.


An **API** is a collection of endpoints (paths), servers, authentication methods, and other metadata that describe how to interact with the API.

 * Where possible we located the OpenAPI specification for the API and used it as a base to describe the API.
 * We add additional documentation to fill in missing pieces of the OpenAPI specification.
 * We use success and error codes from the API to further improve the documentation.
   * Full Request and Response Types
   * Example Request and Responses data
   * Docustrings for each endpoint
   * Authentication methods
   * Authorization methods

Assuming we have a complete and accurate OpenAPI specification, we can

 * Generate python typing for the API
   * Request and Response Objects
   * Core Objects
 * Graph of input and output types
   * Separate out pagination parameters
   * Create a call graph of the API to crawl the API for a given set of data.
   * Mock endpoints for testing (real and fake data)
 * Entity Relationship DataModel for outputs

* Integrate with code generation tools to generate
   * Better API docus
   * Better API clients
   * Better testing tools for the API
   * Postman collections


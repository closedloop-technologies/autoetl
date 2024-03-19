from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, AnyUrl, EmailStr


class OpenAPIVersionEnum(str, Enum):
    v3_0_0 = "3.0.0"
    v3_0_1 = "3.0.1"
    v3_0_2 = "3.0.2"
    v3_0_3 = "3.0.3"
    v3_1_0 = "3.1.0"


class ReferenceObject(BaseModel):
    ref: str = Field(
        ...,
        alias="$ref",
        description="The reference identifier. This MUST be in the form of a URI.",
    )
    summary: Optional[str] = Field(
        None,
        description="A short summary which by default SHOULD override that of the referenced component.",
    )
    description: Optional[str] = Field(
        None,
        description="A description which by default SHOULD override that of the referenced component.",
    )


class ExampleObject(BaseModel):
    summary: Optional[str] = Field(
        None, description="Short description for the example."
    )
    description: Optional[str] = Field(
        None, description="Long description for the example."
    )
    value: Optional[Any] = Field(None, description="Embedded literal example.")
    externalValue: Optional[AnyUrl] = Field(
        None, description="A URI that points to the literal example."
    )


class SchemaObject(BaseModel):
    title: Optional[str] = Field(None, description="A title for the schema.")
    multipleOf: Optional[float] = Field(
        None, description="The value must be a multiple of this number."
    )
    maximum: Optional[float] = Field(None, description="The maximum value allowed.")
    exclusiveMaximum: Optional[bool] = Field(
        None, description="If true, the value must be less than the maximum."
    )
    minimum: Optional[float] = Field(None, description="The minimum value allowed.")
    exclusiveMinimum: Optional[bool] = Field(
        None, description="If true, the value must be greater than the minimum."
    )
    maxLength: Optional[int] = Field(
        None, gte=0, description="The maximum length of a string value."
    )
    minLength: Optional[int] = Field(
        None, gte=0, description="The minimum length of a string value."
    )
    pattern: Optional[str] = Field(
        None, description="A regular expression that the value must match."
    )
    maxItems: Optional[int] = Field(
        None, gte=0, description="The maximum number of items allowed in an array."
    )
    minItems: Optional[int] = Field(
        None, gte=0, description="The minimum number of items allowed in an array."
    )
    uniqueItems: Optional[bool] = Field(
        None, description="If true, the items in an array must be unique."
    )
    maxProperties: Optional[int] = Field(
        None,
        gte=0,
        description="The maximum number of properties allowed in an object.",
    )
    minProperties: Optional[int] = Field(
        None,
        gte=0,
        description="The minimum number of properties allowed in an object.",
    )
    required: Optional[List[str]] = Field(
        None, description="The names of the required properties."
    )
    enum: Optional[List[Any]] = Field(
        None, description="The list of acceptable values."
    )
    type: Optional[str] = Field(None, description="The type of the value.")
    allOf: Optional[List["SchemaObject"]] = Field(
        None, description="The value must satisfy all the subschemas."
    )
    oneOf: Optional[List["SchemaObject"]] = Field(
        None, description="The value must satisfy exactly one of the subschemas."
    )
    anyOf: Optional[List["SchemaObject"]] = Field(
        None, description="The value must satisfy at least one of the subschemas."
    )
    not_: Optional["SchemaObject"] = Field(
        None, alias="not", description="The value must not satisfy this schema."
    )
    items: Optional["SchemaObject"] = Field(
        None, description="The schema for the items of an array."
    )
    properties: Optional[Dict[str, "SchemaObject"]] = Field(
        None, description="The schemas for the properties of an object."
    )
    additionalProperties: Optional[Union["SchemaObject", ReferenceObject, bool]] = (
        Field(
            None, description="The schema for the additional properties of an object."
        )
    )
    description: Optional[str] = Field(None, description="A description of the schema.")
    format: Optional[str] = Field(None, description="The format of the value.")
    default: Optional[Any] = Field(None, description="The default value.")
    nullable: Optional[bool] = Field(
        None, description="If true, the value can be null."
    )
    discriminator: Optional["DiscriminatorObject"] = Field(
        None, description="Adds support for polymorphism."
    )
    readOnly: Optional[bool] = Field(
        None, description="If true, the value is read-only."
    )
    writeOnly: Optional[bool] = Field(
        None, description="If true, the value is write-only."
    )
    xml: Optional["XMLObject"] = Field(
        None,
        description="Adds additional metadata to describe the XML representation of the value.",
    )
    externalDocs: Optional["ExternalDocumentationObject"] = Field(
        None, description="Additional external documentation for the schema."
    )
    example: Optional[Any] = Field(
        None, description="A free-form property to include an example of the value."
    )
    deprecated: Optional[bool] = Field(
        None,
        description="If true, the schema is deprecated and should be transitioned out of usage.",
    )


class DiscriminatorObject(BaseModel):
    propertyName: str = Field(
        ...,
        description="The name of the property in the payload that will hold the discriminator value.",
    )
    mapping: Optional[Dict[str, str]] = Field(
        None,
        description="An object to hold mappings between payload values and schema names or references.",
    )


class XMLObject(BaseModel):
    name: Optional[str] = Field(
        None,
        description="Replaces the name of the element/attribute used for the described schema property.",
    )
    namespace: Optional[AnyUrl] = Field(
        None, description="The URI of the namespace definition."
    )
    prefix: Optional[str] = Field(
        None, description="The prefix to be used for the name."
    )
    attribute: Optional[bool] = Field(
        None,
        description="Declares whether the property definition translates to an attribute instead of an element.",
    )
    wrapped: Optional[bool] = Field(
        None,
        description="MAY be used only for an array definition. Signifies whether the array is wrapped.",
    )


class ExternalDocumentationObject(BaseModel):
    description: Optional[str] = Field(
        None, description="A description of the target documentation."
    )
    url: AnyUrl = Field(..., description="The URL for the target documentation.")


class ContactObject(BaseModel):
    name: Optional[str] = Field(
        None, description="The identifying name of the contact person/organization."
    )
    url: Optional[AnyUrl] = Field(
        None, description="The URL pointing to the contact information."
    )
    email: Optional[EmailStr] = Field(
        None, description="The email address of the contact person/organization."
    )


class LicenseObject(BaseModel):
    name: str = Field(..., description="The license name used for the API.")
    identifier: Optional[str] = Field(
        None, description="An SPDX license expression for the API."
    )
    url: Optional[AnyUrl] = Field(
        None, description="A URL to the license used for the API."
    )


class InfoObject(BaseModel):
    title: str = Field(..., description="The title of the API.")
    summary: Optional[str] = Field(None, description="A short summary of the API.")
    description: Optional[str] = Field(None, description="A description of the API.")
    termsOfService: Optional[AnyUrl] = Field(
        None, description="A URL to the Terms of Service for the API."
    )
    contact: Optional[ContactObject] = Field(
        None, description="The contact information for the exposed API."
    )
    license: Optional[LicenseObject] = Field(
        None, description="The license information for the exposed API."
    )
    version: str = Field(..., description="The version of the OpenAPI document.")


class ServerVariableObject(BaseModel):
    enum: Optional[List[str]] = Field(
        None,
        description="An enumeration of string values to be used if the substitution options are from a limited set.",
    )
    default: str = Field(
        ...,
        description="The default value to use for substitution, which SHALL be sent if an alternate value is not supplied.",
    )
    description: Optional[str] = Field(
        None, description="An optional description for the server variable."
    )


class ServerObject(BaseModel):
    url: AnyUrl = Field(..., description="A URL to the target host.")
    description: Optional[str] = Field(
        None,
        description="An optional string describing the host designated by the URL.",
    )
    variables: Optional[Dict[str, ServerVariableObject]] = Field(
        None, description="A map between a variable name and its value."
    )


class ParameterLocation(str, Enum):
    query = "query"
    header = "header"
    path = "path"
    cookie = "cookie"


class ParameterStyle(str, Enum):
    matrix = "matrix"
    label = "label"
    form = "form"
    simple = "simple"
    spaceDelimited = "spaceDelimited"
    pipeDelimited = "pipeDelimited"
    deepObject = "deepObject"


class ParameterObject(BaseModel):
    name: str = Field(..., description="The name of the parameter.")
    in_: ParameterLocation = Field(
        ..., alias="in", description="The location of the parameter."
    )
    description: Optional[str] = Field(
        None, description="A brief description of the parameter."
    )
    required: Optional[bool] = Field(
        None, description="Determines whether this parameter is mandatory."
    )
    deprecated: Optional[bool] = Field(
        None,
        description="Specifies that a parameter is deprecated and SHOULD be transitioned out of usage.",
    )
    allowEmptyValue: Optional[bool] = Field(
        None, description="Sets the ability to pass empty-valued parameters."
    )
    style: Optional[ParameterStyle] = Field(
        None,
        description="Describes how the parameter value will be serialized depending on the type of the parameter value.",
    )
    explode: Optional[bool] = Field(
        None,
        description="When this is true, parameter values of type array or object generate separate parameters for each value of the array or key-value pair of the map.",
    )
    allowReserved: Optional[bool] = Field(
        None,
        description="Determines whether the parameter value SHOULD allow reserved characters.",
    )
    schema: Optional[SchemaObject] = Field(
        None, description="The schema defining the type used for the parameter."
    )
    example: Optional[Any] = Field(
        None, description="Example of the parameter's potential value."
    )
    examples: Optional[Dict[str, Union[ExampleObject, ReferenceObject]]] = Field(
        None, description="Examples of the parameter's potential value."
    )
    content: Optional[Dict[str, "MediaTypeObject"]] = Field(
        None, description="A map containing the representations for the parameter."
    )


class MediaTypeObject(BaseModel):
    schema: Optional[Union[SchemaObject, ReferenceObject]] = Field(
        None,
        description="The schema defining the content of the request, response, or parameter.",
    )
    example: Optional[Any] = Field(None, description="Example of the media type.")
    examples: Optional[Dict[str, Union[ExampleObject, ReferenceObject]]] = Field(
        None, description="Examples of the media type."
    )
    encoding: Optional[Dict[str, "EncodingObject"]] = Field(
        None, description="A map between a property name and its encoding information."
    )


class EncodingObject(BaseModel):
    contentType: Optional[str] = Field(
        None, description="The Content-Type for encoding a specific property."
    )
    headers: Optional[Dict[str, Union["HeaderObject", ReferenceObject]]] = Field(
        None,
        description="A map allowing additional information to be provided as headers.",
    )
    style: Optional[str] = Field(
        None,
        description="Describes how a specific property value will be serialized depending on its type.",
    )
    explode: Optional[bool] = Field(
        None,
        description="When this is true, property values of type array or object generate separate parameters for each value of the array, or key-value-pair of the map.",
    )
    allowReserved: Optional[bool] = Field(
        None,
        description="Determines whether the parameter value SHOULD allow reserved characters.",
    )


class RequestBodyObject(BaseModel):
    description: Optional[str] = Field(
        None, description="A brief description of the request body."
    )
    content: Dict[str, MediaTypeObject] = Field(
        ..., description="The content of the request body."
    )
    required: Optional[bool] = Field(
        None, description="Determines if the request body is required in the request."
    )


class ResponseObject(BaseModel):
    description: str = Field(..., description="A description of the response.")
    headers: Optional[Dict[str, Union["HeaderObject", ReferenceObject]]] = Field(
        None, description="Maps a header name to its definition."
    )
    content: Optional[Dict[str, MediaTypeObject]] = Field(
        None,
        description="A map containing descriptions of potential response payloads.",
    )
    links: Optional[Dict[str, Union["LinkObject", ReferenceObject]]] = Field(
        None,
        description="A map of operations links that can be followed from the response.",
    )


class CallbackObject(BaseModel):
    pass


class LinkObject(BaseModel):
    operationRef: Optional[str] = Field(
        None, description="A relative or absolute URI reference to an OAS operation."
    )
    operationId: Optional[str] = Field(
        None,
        description="The name of an existing, resolvable OAS operation, as defined with a unique operationId.",
    )
    parameters: Optional[Dict[str, Union[Any, Dict[str, Any]]]] = Field(
        None,
        description="A map representing parameters to pass to an operation as specified with operationId or identified via operationRef.",
    )
    requestBody: Optional[Union[Any, Dict[str, Any]]] = Field(
        None,
        description="A literal value or {expression} to use as a request body when calling the target operation.",
    )
    description: Optional[str] = Field(None, description="A description of the link.")
    server: Optional[ServerObject] = Field(
        None, description="A server object to be used by the target operation."
    )


class HeaderObject(BaseModel):
    description: Optional[str] = Field(
        None, description="A brief description of the header."
    )
    required: Optional[bool] = Field(
        None, description="Determines whether this header is mandatory."
    )
    deprecated: Optional[bool] = Field(
        None,
        description="Specifies that a header is deprecated and SHOULD be transitioned out of usage.",
    )
    allowEmptyValue: Optional[bool] = Field(
        None, description="Sets the ability to pass empty-valued headers."
    )
    style: Optional[str] = Field(
        None,
        description="Describes how the header value will be serialized depending on the type of the header value.",
    )
    explode: Optional[bool] = Field(
        None,
        description="When this is true, header values of type array or object generate separate headers for each value of the array or key-value pair of the map.",
    )
    allowReserved: Optional[bool] = Field(
        None,
        description="Determines whether the header value SHOULD allow reserved characters.",
    )
    schema: Optional[SchemaObject] = Field(
        None, description="The schema defining the type used for the header."
    )
    example: Optional[Any] = Field(
        None, description="Example of the header's potential value."
    )
    examples: Optional[Dict[str, Union[ExampleObject, ReferenceObject]]] = Field(
        None, description="Examples of the header's potential value."
    )
    content: Optional[Dict[str, MediaTypeObject]] = Field(
        None, description="A map containing the representations for the header."
    )


class OAuthFlowObject(BaseModel):
    authorizationUrl: Optional[AnyUrl] = Field(
        None, description="The authorization URL to be used for this flow."
    )
    tokenUrl: Optional[AnyUrl] = Field(
        None, description="The token URL to be used for this flow."
    )
    refreshUrl: Optional[AnyUrl] = Field(
        None, description="The URL to be used for obtaining refresh tokens."
    )
    scopes: Dict[str, str] = Field(
        ..., description="The available scopes for the OAuth2 security scheme."
    )


class OAuthFlowsObject(BaseModel):
    implicit: Optional[OAuthFlowObject] = Field(
        None, description="Configuration for the OAuth Implicit flow."
    )
    password: Optional[OAuthFlowObject] = Field(
        None, description="Configuration for the OAuth Resource Owner Password flow."
    )
    clientCredentials: Optional[OAuthFlowObject] = Field(
        None, description="Configuration for the OAuth Client Credentials flow."
    )
    authorizationCode: Optional[OAuthFlowObject] = Field(
        None, description="Configuration for the OAuth Authorization Code flow."
    )


class SecuritySchemeType(str, Enum):
    apiKey = "apiKey"
    http = "http"
    oauth2 = "oauth2"
    openIdConnect = "openIdConnect"
    mutualTLS = "mutualTLS"


class SecuritySchemeObject(BaseModel):
    type: SecuritySchemeType = Field(
        ..., description="The type of the security scheme."
    )
    description: Optional[str] = Field(
        None, description="A description for security scheme."
    )
    name: Optional[str] = Field(
        None,
        description="The name of the header, query or cookie parameter to be used.",
    )
    in_: Optional[ParameterLocation] = Field(
        None, alias="in", description="The location of the API key."
    )
    scheme: Optional[str] = Field(
        None,
        description="The name of the HTTP Authorization scheme to be used in the Authorization header as defined in RFC7235.",
    )
    bearerFormat: Optional[str] = Field(
        None,
        description="A hint to the client to identify how the bearer token is formatted.",
    )
    flows: Optional[OAuthFlowsObject] = Field(
        None,
        description="An object containing configuration information for the flow types supported.",
    )
    openIdConnectUrl: Optional[AnyUrl] = Field(
        None, description="OpenId Connect URL to discover OAuth2 configuration values."
    )


class OperationObject(BaseModel):
    tags: Optional[List[str]] = Field(
        None, description="A list of tags for API documentation control."
    )
    summary: Optional[str] = Field(
        None, description="A short summary of what the operation does."
    )
    description: Optional[str] = Field(
        None, description="A verbose explanation of the operation behavior."
    )
    externalDocs: Optional[ExternalDocumentationObject] = Field(
        None, description="Additional external documentation for this operation."
    )
    operationId: Optional[str] = Field(
        None, description="Unique string used to identify the operation."
    )
    parameters: Optional[List[Union[ParameterObject, ReferenceObject]]] = Field(
        None, description="A list of parameters that are applicable for this operation."
    )
    requestBody: Optional[Union[RequestBodyObject, ReferenceObject]] = Field(
        None, description="The request body applicable for this operation."
    )
    responses: Dict[str, Union[ResponseObject, ReferenceObject]] = Field(
        ...,
        description="The list of possible responses as they are returned from executing this operation.",
    )
    callbacks: Optional[Dict[str, Union[CallbackObject, ReferenceObject]]] = Field(
        None,
        description="A map of possible out-of band callbacks related to the parent operation.",
    )
    deprecated: Optional[bool] = Field(
        None, description="Declares this operation to be deprecated."
    )
    security: Optional[List[Dict[str, List[str]]]] = Field(
        None,
        description="A declaration of which security mechanisms can be used for this operation.",
    )
    servers: Optional[List[ServerObject]] = Field(
        None, description="An alternative server array to service this operation."
    )


class PathItemObject(BaseModel):
    ref: Optional[str] = Field(
        None,
        alias="$ref",
        description="Allows for a referenced definition of this path item.",
    )
    summary: Optional[str] = Field(
        None,
        description="An optional, string summary, intended to apply to all operations in this path.",
    )
    description: Optional[str] = Field(
        None,
        description="An optional, string description, intended to apply to all operations in this path.",
    )
    get: Optional[OperationObject] = Field(
        None, description="A definition of a GET operation on this path."
    )
    put: Optional[OperationObject] = Field(
        None, description="A definition of a PUT operation on this path."
    )
    post: Optional[OperationObject] = Field(
        None, description="A definition of a POST operation on this path."
    )
    delete: Optional[OperationObject] = Field(
        None, description="A definition of a DELETE operation on this path."
    )
    options: Optional[OperationObject] = Field(
        None, description="A definition of a OPTIONS operation on this path."
    )
    head: Optional[OperationObject] = Field(
        None, description="A definition of a HEAD operation on this path."
    )
    patch: Optional[OperationObject] = Field(
        None, description="A definition of a PATCH operation on this path."
    )
    trace: Optional[OperationObject] = Field(
        None, description="A definition of a TRACE operation on this path."
    )
    servers: Optional[List[ServerObject]] = Field(
        None,
        description="An alternative server array to service all operations in this path.",
    )
    parameters: Optional[List[Union[ParameterObject, ReferenceObject]]] = Field(
        None,
        description="A list of parameters that are applicable for all the operations described under this path.",
    )


class ComponentsObject(BaseModel):
    schemas: Optional[Dict[str, Union[SchemaObject, ReferenceObject]]] = Field(
        None, description="An object to hold reusable Schema Objects."
    )
    responses: Optional[Dict[str, Union[ResponseObject, ReferenceObject]]] = Field(
        None, description="An object to hold reusable Response Objects."
    )
    parameters: Optional[Dict[str, Union[ParameterObject, ReferenceObject]]] = Field(
        None, description="An object to hold reusable Parameter Objects."
    )
    examples: Optional[Dict[str, Union[ExampleObject, ReferenceObject]]] = Field(
        None, description="An object to hold reusable Example Objects."
    )
    requestBodies: Optional[Dict[str, Union[RequestBodyObject, ReferenceObject]]] = (
        Field(None, description="An object to hold reusable Request Body Objects.")
    )
    headers: Optional[Dict[str, Union[HeaderObject, ReferenceObject]]] = Field(
        None, description="An object to hold reusable Header Objects."
    )
    securitySchemes: Optional[
        Dict[str, Union[SecuritySchemeObject, ReferenceObject]]
    ] = Field(None, description="An object to hold reusable Security Scheme Objects.")
    links: Optional[Dict[str, Union[LinkObject, ReferenceObject]]] = Field(
        None, description="An object to hold reusable Link Objects."
    )
    callbacks: Optional[Dict[str, Union[CallbackObject, ReferenceObject]]] = Field(
        None, description="An object to hold reusable Callback Objects."
    )
    pathItems: Optional[Dict[str, Union[PathItemObject, ReferenceObject]]] = Field(
        None, description="An object to hold reusable Path Item Object."
    )


class TagObject(BaseModel):
    name: str = Field(..., description="The name of the tag.")
    description: Optional[str] = Field(None, description="A description for the tag.")
    externalDocs: Optional[ExternalDocumentationObject] = Field(
        None, description="Additional external documentation for this tag."
    )


class OpenAPIObject(BaseModel):
    openapi: OpenAPIVersionEnum = Field(
        ...,
        description="The version number of the OpenAPI Specification that the OpenAPI document uses.",
    )
    info: InfoObject = Field(..., description="Provides metadata about the API.")
    jsonSchemaDialect: Optional[AnyUrl] = Field(
        None,
        description="The default value for the $schema keyword within Schema Objects contained within this OAS document.",
    )
    servers: Optional[List[ServerObject]] = Field(
        None,
        description="An array of Server Objects, which provide connectivity information to a target server.",
    )
    paths: Dict[str, PathItemObject] = Field(
        ..., description="The available paths and operations for the API."
    )
    webhooks: Optional[Dict[str, Union[PathItemObject, ReferenceObject]]] = Field(
        None,
        description="The incoming webhooks that MAY be received as part of this API and that the API consumer MAY choose to implement.",
    )
    components: Optional[ComponentsObject] = Field(
        None, description="An element to hold various schemas for the document."
    )
    security: Optional[List[Dict[str, List[str]]]] = Field(
        None,
        description="A declaration of which security mechanisms can be used across the API.",
    )
    tags: Optional[List[TagObject]] = Field(
        None,
        description="A list of tags used by the document with additional metadata.",
    )
    externalDocs: Optional[ExternalDocumentationObject] = Field(
        None, description="Additional external documentation."
    )

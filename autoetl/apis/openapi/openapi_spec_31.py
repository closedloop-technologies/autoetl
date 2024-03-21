# generated by datamodel-codegen:
#   filename:  openapi_spec_31.json
#   timestamp: 2024-03-21T00:53:27+00:00

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class Openapi(BaseModel):
    type: str
    pattern: str


class Info(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class JsonSchemaDialect(BaseModel):
    type: str
    format: str
    default: str


class Items(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class DefaultItem(BaseModel):
    url: str


class Servers(BaseModel):
    type: str
    items: Items
    default: List[DefaultItem]


class Paths(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class AdditionalProperties(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Webhooks(BaseModel):
    type: str
    additionalProperties: AdditionalProperties


class Components(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Security(BaseModel):
    type: str
    items: Items


class Tags(BaseModel):
    type: str
    items: Items


class ExternalDocs(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Properties(BaseModel):
    openapi: Openapi
    info: Info
    jsonSchemaDialect: JsonSchemaDialect
    servers: Servers
    paths: Paths
    webhooks: Webhooks
    components: Components
    security: Security
    tags: Tags
    externalDocs: ExternalDocs


class AnyOfItem(BaseModel):
    required: List[str]


class Title(BaseModel):
    type: str


class Summary(BaseModel):
    type: str


class Description(BaseModel):
    type: str


class TermsOfService(BaseModel):
    type: str
    format: str


class Contact(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class License(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Version(BaseModel):
    type: str


class Properties1(BaseModel):
    title: Title
    summary: Summary
    description: Description
    termsOfService: TermsOfService
    contact: Contact
    license: License
    version: Version


class Info1(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties1
    required: List[str]
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class Name(BaseModel):
    type: str


class Url(BaseModel):
    type: str
    format: str


class Email(BaseModel):
    type: str
    format: str


class Properties2(BaseModel):
    name: Name
    url: Url
    email: Email


class Contact1(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties2
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class Identifier(BaseModel):
    type: str


class Properties3(BaseModel):
    name: Name
    identifier: Identifier
    url: Url


class Not(BaseModel):
    required: List[str]


class Identifier1(BaseModel):
    not_: Not = Field(..., alias='not')


class DependentSchemas(BaseModel):
    identifier: Identifier1


class License1(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties3
    required: List[str]
    dependentSchemas: DependentSchemas
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class Variables(BaseModel):
    type: str
    additionalProperties: AdditionalProperties


class Properties4(BaseModel):
    url: Url
    description: Description
    variables: Variables


class Server(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties4
    required: List[str]
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class Items3(BaseModel):
    type: str


class Enum(BaseModel):
    type: str
    items: Items3
    minItems: int


class Default(BaseModel):
    type: str


class Properties5(BaseModel):
    enum: Enum
    default: Default
    description: Description


class ServerVariable(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties5
    required: List[str]
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class AdditionalProperties2(BaseModel):
    field_dynamicRef: str = Field(..., alias='$dynamicRef')


class Schemas(BaseModel):
    type: str
    additionalProperties: AdditionalProperties2


class AdditionalProperties3(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Responses(BaseModel):
    type: str
    additionalProperties: AdditionalProperties3


class Parameters(BaseModel):
    type: str
    additionalProperties: AdditionalProperties3


class Examples(BaseModel):
    type: str
    additionalProperties: AdditionalProperties3


class RequestBodies(BaseModel):
    type: str
    additionalProperties: AdditionalProperties3


class Headers(BaseModel):
    type: str
    additionalProperties: AdditionalProperties3


class SecuritySchemes(BaseModel):
    type: str
    additionalProperties: AdditionalProperties3


class Links(BaseModel):
    type: str
    additionalProperties: AdditionalProperties3


class Callbacks(BaseModel):
    type: str
    additionalProperties: AdditionalProperties3


class PathItems(BaseModel):
    type: str
    additionalProperties: AdditionalProperties3


class Properties6(BaseModel):
    schemas: Schemas
    responses: Responses
    parameters: Parameters
    examples: Examples
    requestBodies: RequestBodies
    headers: Headers
    securitySchemes: SecuritySchemes
    links: Links
    callbacks: Callbacks
    pathItems: PathItems


class PropertyNames(BaseModel):
    pattern: str


class FieldSchemasResponsesParametersExamplesRequestBodiesHeadersSecuritySchemesLinksCallbacksPathItems(
    BaseModel
):
    field_comment: str = Field(..., alias='$comment')
    propertyNames: PropertyNames


class PatternProperties(BaseModel):
    field__schemas_responses_parameters_examples_requestBodies_headers_securitySchemes_links_callbacks_pathItems__: FieldSchemasResponsesParametersExamplesRequestBodiesHeadersSecuritySchemesLinksCallbacksPathItems = Field(
        ...,
        alias='^(schemas|responses|parameters|examples|requestBodies|headers|securitySchemes|links|callbacks|pathItems)$',
    )


class Components1(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties6
    patternProperties: PatternProperties
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class FieldModel(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class PatternProperties1(BaseModel):
    field__: FieldModel = Field(..., alias='^/')


class Paths1(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    patternProperties: PatternProperties1
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class Items4(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Servers1(BaseModel):
    type: str
    items: Items4


class Parameters1(BaseModel):
    type: str
    items: Items4


class Get(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Put(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Post(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Delete(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Options(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Head(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Patch(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Trace(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Properties7(BaseModel):
    summary: Summary
    description: Description
    servers: Servers1
    parameters: Parameters1
    get: Get
    put: Put
    post: Post
    delete: Delete
    options: Options
    head: Head
    patch: Patch
    trace: Trace


class PathItem(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties7
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class If(BaseModel):
    type: str
    required: List[str]


class Then(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Else(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class PathItemOrReference(BaseModel):
    if_: If = Field(..., alias='if')
    then: Then
    else_: Else = Field(..., alias='else')


class Items6(BaseModel):
    type: str


class Tags1(BaseModel):
    type: str
    items: Items6


class OperationId(BaseModel):
    type: str


class Items7(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Parameters2(BaseModel):
    type: str
    items: Items7


class RequestBody(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Responses1(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Callbacks1(BaseModel):
    type: str
    additionalProperties: AdditionalProperties3


class Deprecated(BaseModel):
    default: bool
    type: str


class Security1(BaseModel):
    type: str
    items: Items7


class Servers2(BaseModel):
    type: str
    items: Items7


class Properties8(BaseModel):
    tags: Tags1
    summary: Summary
    description: Description
    externalDocs: ExternalDocs
    operationId: OperationId
    parameters: Parameters2
    requestBody: RequestBody
    responses: Responses1
    callbacks: Callbacks1
    deprecated: Deprecated
    security: Security1
    servers: Servers2


class Operation(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties8
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class Properties9(BaseModel):
    description: Description
    url: Url


class ExternalDocumentation(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties9
    required: List[str]
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class In(BaseModel):
    enum: List[str]


class Required(BaseModel):
    default: bool
    type: str


class Schema(BaseModel):
    field_dynamicRef: str = Field(..., alias='$dynamicRef')


class Content(BaseModel):
    field_ref: str = Field(..., alias='$ref')
    minProperties: int
    maxProperties: int


class Properties10(BaseModel):
    name: Name
    in_: In = Field(..., alias='in')
    description: Description
    required: Required
    deprecated: Deprecated
    schema_: Schema = Field(..., alias='schema')
    content: Content


class OneOfItem(BaseModel):
    required: List[str]


class In1(BaseModel):
    const: str


class Properties11(BaseModel):
    in_: In1 = Field(..., alias='in')


class If1(BaseModel):
    properties: Properties11
    required: List[str]


class AllowEmptyValue(BaseModel):
    default: bool
    type: str


class Properties12(BaseModel):
    allowEmptyValue: AllowEmptyValue


class Then1(BaseModel):
    properties: Properties12


class Style(BaseModel):
    type: str


class Explode(BaseModel):
    type: str


class Properties13(BaseModel):
    style: Style
    explode: Explode


class AllOfItem(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Properties14(BaseModel):
    in_: In1 = Field(..., alias='in')


class If2(BaseModel):
    properties: Properties14
    required: List[str]


class Style1(BaseModel):
    default: str
    enum: List[str]


class Required1(BaseModel):
    const: bool


class Properties15(BaseModel):
    style: Style1
    required: Required1


class Then2(BaseModel):
    properties: Properties15
    required: List[str]


class StylesForPath(BaseModel):
    if_: If2 = Field(..., alias='if')
    then: Then2


class Properties16(BaseModel):
    in_: In1 = Field(..., alias='in')


class If3(BaseModel):
    properties: Properties16
    required: List[str]


class Style2(BaseModel):
    default: str
    const: str


class Properties17(BaseModel):
    style: Style2


class Then3(BaseModel):
    properties: Properties17


class StylesForHeader(BaseModel):
    if_: If3 = Field(..., alias='if')
    then: Then3


class Properties18(BaseModel):
    in_: In1 = Field(..., alias='in')


class If4(BaseModel):
    properties: Properties18
    required: List[str]


class Style3(BaseModel):
    default: str
    enum: List[str]


class AllowReserved(BaseModel):
    default: bool
    type: str


class Properties19(BaseModel):
    style: Style3
    allowReserved: AllowReserved


class Then4(BaseModel):
    properties: Properties19


class StylesForQuery(BaseModel):
    if_: If4 = Field(..., alias='if')
    then: Then4


class Properties20(BaseModel):
    in_: In1 = Field(..., alias='in')


class If5(BaseModel):
    properties: Properties20
    required: List[str]


class Style4(BaseModel):
    default: str
    const: str


class Properties21(BaseModel):
    style: Style4


class Then5(BaseModel):
    properties: Properties21


class StylesForCookie(BaseModel):
    if_: If5 = Field(..., alias='if')
    then: Then5


class FieldDefs1(BaseModel):
    styles_for_path: StylesForPath = Field(..., alias='styles-for-path')
    styles_for_header: StylesForHeader = Field(..., alias='styles-for-header')
    styles_for_query: StylesForQuery = Field(..., alias='styles-for-query')
    styles_for_cookie: StylesForCookie = Field(..., alias='styles-for-cookie')


class Schema1(BaseModel):
    properties: Properties13
    allOf: List[AllOfItem]
    field_defs: FieldDefs1 = Field(..., alias='$defs')


class DependentSchemas1(BaseModel):
    schema_: Schema1 = Field(..., alias='schema')


class Parameter(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties10
    required: List[str]
    oneOf: List[OneOfItem]
    if_: If1 = Field(..., alias='if')
    then: Then1
    dependentSchemas: DependentSchemas1
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class If6(BaseModel):
    type: str
    required: List[str]


class Then6(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class ParameterOrReference(BaseModel):
    if_: If6 = Field(..., alias='if')
    then: Then6
    else_: Else = Field(..., alias='else')


class Content1(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Required2(BaseModel):
    default: bool
    type: str


class Properties22(BaseModel):
    description: Description
    content: Content1
    required: Required2


class RequestBody1(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties22
    required: List[str]
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class RequestBodyOrReference(BaseModel):
    if_: If6 = Field(..., alias='if')
    then: Then6
    else_: Else = Field(..., alias='else')


class PropertyNames1(BaseModel):
    format: str


class Content2(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    additionalProperties: AdditionalProperties3
    propertyNames: PropertyNames1


class Schema2(BaseModel):
    field_dynamicRef: str = Field(..., alias='$dynamicRef')


class Encoding(BaseModel):
    type: str
    additionalProperties: AdditionalProperties3


class Properties23(BaseModel):
    schema_: Schema2 = Field(..., alias='schema')
    encoding: Encoding


class MediaType(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties23
    allOf: List[AllOfItem]
    unevaluatedProperties: bool


class ContentType(BaseModel):
    type: str
    format: str


class Headers1(BaseModel):
    type: str
    additionalProperties: AdditionalProperties3


class Style5(BaseModel):
    default: str
    enum: List[str]


class Properties24(BaseModel):
    contentType: ContentType
    headers: Headers1
    style: Style5
    explode: Explode
    allowReserved: AllowReserved


class Encoding1(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties24
    allOf: List[AllOfItem]
    unevaluatedProperties: bool


class Default1(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Properties25(BaseModel):
    default: Default1


class Field15092XX(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class PatternProperties2(BaseModel):
    field__1_5_____0_9__2__XX__: Field15092XX = Field(
        ..., alias='^[1-5](?:[0-9]{2}|XX)$'
    )


class PatternProperties3(BaseModel):
    field__1_5_____0_9__2__XX__: bool = Field(..., alias='^[1-5](?:[0-9]{2}|XX)$')


class If8(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    patternProperties: PatternProperties3


class Then8(BaseModel):
    required: List[str]


class Responses2(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties25
    patternProperties: PatternProperties2
    minProperties: int
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool
    if_: If8 = Field(..., alias='if')
    then: Then8


class Headers2(BaseModel):
    type: str
    additionalProperties: AdditionalProperties3


class Content3(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Links1(BaseModel):
    type: str
    additionalProperties: AdditionalProperties3


class Properties26(BaseModel):
    description: Description
    headers: Headers2
    content: Content3
    links: Links1


class Response(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties26
    required: List[str]
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class If9(BaseModel):
    type: str
    required: List[str]


class Then9(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class ResponseOrReference(BaseModel):
    if_: If9 = Field(..., alias='if')
    then: Then9
    else_: Else = Field(..., alias='else')


class Callbacks2(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    field_ref: str = Field(..., alias='$ref')
    additionalProperties: AdditionalProperties3


class CallbacksOrReference(BaseModel):
    if_: If9 = Field(..., alias='if')
    then: Then9
    else_: Else = Field(..., alias='else')


class ExternalValue(BaseModel):
    type: str
    format: str


class Properties27(BaseModel):
    summary: Summary
    description: Description
    value: bool
    externalValue: ExternalValue


class Example(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties27
    not_: Not = Field(..., alias='not')
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class ExampleOrReference(BaseModel):
    if_: If9 = Field(..., alias='if')
    then: Then9
    else_: Else = Field(..., alias='else')


class OperationRef(BaseModel):
    type: str
    format: str


class Parameters3(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Body(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Properties28(BaseModel):
    operationRef: OperationRef
    operationId: OperationId
    parameters: Parameters3
    requestBody: bool
    description: Description
    body: Body


class Link(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties28
    oneOf: List[OneOfItem]
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class LinkOrReference(BaseModel):
    if_: If9 = Field(..., alias='if')
    then: Then9
    else_: Else = Field(..., alias='else')


class Content4(BaseModel):
    field_ref: str = Field(..., alias='$ref')
    minProperties: int
    maxProperties: int


class Properties29(BaseModel):
    description: Description
    required: Required2
    deprecated: Deprecated
    schema_: Schema2 = Field(..., alias='schema')
    content: Content4


class Style6(BaseModel):
    default: str
    const: str


class Explode2(BaseModel):
    default: bool
    type: str


class Properties30(BaseModel):
    style: Style6
    explode: Explode2


class Schema4(BaseModel):
    properties: Properties30
    field_ref: str = Field(..., alias='$ref')


class DependentSchemas2(BaseModel):
    schema_: Schema4 = Field(..., alias='schema')


class Header(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties29
    oneOf: List[OneOfItem]
    dependentSchemas: DependentSchemas2
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class HeaderOrReference(BaseModel):
    if_: If9 = Field(..., alias='if')
    then: Then9
    else_: Else = Field(..., alias='else')


class Properties31(BaseModel):
    name: Name
    description: Description
    externalDocs: ExternalDocs


class Tag(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties31
    required: List[str]
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class FieldRef(BaseModel):
    type: str
    format: str


class Properties32(BaseModel):
    field_ref: FieldRef = Field(..., alias='$ref')
    summary: Summary
    description: Description


class Reference(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties32


class Schema5(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    field_dynamicAnchor: str = Field(..., alias='$dynamicAnchor')
    type: List[str]


class Type(BaseModel):
    enum: List[str]


class Properties33(BaseModel):
    type: Type
    description: Description


class Type1(BaseModel):
    const: str


class Properties34(BaseModel):
    type: Type1


class If14(BaseModel):
    properties: Properties34
    required: List[str]


class In6(BaseModel):
    enum: List[str]


class Properties35(BaseModel):
    name: Name
    in_: In6 = Field(..., alias='in')


class Then14(BaseModel):
    properties: Properties35
    required: List[str]


class TypeApikey(BaseModel):
    if_: If14 = Field(..., alias='if')
    then: Then14


class Properties36(BaseModel):
    type: Type1


class If15(BaseModel):
    properties: Properties36
    required: List[str]


class Scheme(BaseModel):
    type: str


class Properties37(BaseModel):
    scheme: Scheme


class Then15(BaseModel):
    properties: Properties37
    required: List[str]


class TypeHttp(BaseModel):
    if_: If15 = Field(..., alias='if')
    then: Then15


class Scheme1(BaseModel):
    type: str
    pattern: str


class Properties38(BaseModel):
    type: Type1
    scheme: Scheme1


class If16(BaseModel):
    properties: Properties38
    required: List[str]


class BearerFormat(BaseModel):
    type: str


class Properties39(BaseModel):
    bearerFormat: BearerFormat


class Then16(BaseModel):
    properties: Properties39


class TypeHttpBearer(BaseModel):
    if_: If16 = Field(..., alias='if')
    then: Then16


class Properties40(BaseModel):
    type: Type1


class If17(BaseModel):
    properties: Properties40
    required: List[str]


class Flows(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Properties41(BaseModel):
    flows: Flows


class Then17(BaseModel):
    properties: Properties41
    required: List[str]


class TypeOauth2(BaseModel):
    if_: If17 = Field(..., alias='if')
    then: Then17


class Properties42(BaseModel):
    type: Type1


class If18(BaseModel):
    properties: Properties42
    required: List[str]


class OpenIdConnectUrl(BaseModel):
    type: str
    format: str


class Properties43(BaseModel):
    openIdConnectUrl: OpenIdConnectUrl


class Then18(BaseModel):
    properties: Properties43
    required: List[str]


class TypeOidc(BaseModel):
    if_: If18 = Field(..., alias='if')
    then: Then18


class FieldDefs2(BaseModel):
    type_apikey: TypeApikey = Field(..., alias='type-apikey')
    type_http: TypeHttp = Field(..., alias='type-http')
    type_http_bearer: TypeHttpBearer = Field(..., alias='type-http-bearer')
    type_oauth2: TypeOauth2 = Field(..., alias='type-oauth2')
    type_oidc: TypeOidc = Field(..., alias='type-oidc')


class SecurityScheme(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    properties: Properties33
    required: List[str]
    allOf: List[AllOfItem]
    unevaluatedProperties: bool
    field_defs: FieldDefs2 = Field(..., alias='$defs')


class If19(BaseModel):
    type: str
    required: List[str]


class Then19(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class SecuritySchemeOrReference(BaseModel):
    if_: If19 = Field(..., alias='if')
    then: Then19
    else_: Else = Field(..., alias='else')


class Implicit(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Password(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class ClientCredentials(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class AuthorizationCode(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Properties44(BaseModel):
    implicit: Implicit
    password: Password
    clientCredentials: ClientCredentials
    authorizationCode: AuthorizationCode


class AuthorizationUrl(BaseModel):
    type: str
    format: str


class RefreshUrl(BaseModel):
    type: str
    format: str


class Scopes(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Properties45(BaseModel):
    authorizationUrl: AuthorizationUrl
    refreshUrl: RefreshUrl
    scopes: Scopes


class Implicit1(BaseModel):
    type: str
    properties: Properties45
    required: List[str]
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class TokenUrl(BaseModel):
    type: str
    format: str


class Properties46(BaseModel):
    tokenUrl: TokenUrl
    refreshUrl: RefreshUrl
    scopes: Scopes


class Password1(BaseModel):
    type: str
    properties: Properties46
    required: List[str]
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class Properties47(BaseModel):
    tokenUrl: TokenUrl
    refreshUrl: RefreshUrl
    scopes: Scopes


class ClientCredentials1(BaseModel):
    type: str
    properties: Properties47
    required: List[str]
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class Properties48(BaseModel):
    authorizationUrl: AuthorizationUrl
    tokenUrl: TokenUrl
    refreshUrl: RefreshUrl
    scopes: Scopes


class AuthorizationCode1(BaseModel):
    type: str
    properties: Properties48
    required: List[str]
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool


class FieldDefs3(BaseModel):
    implicit: Implicit1
    password: Password1
    client_credentials: ClientCredentials1 = Field(..., alias='client-credentials')
    authorization_code: AuthorizationCode1 = Field(..., alias='authorization-code')


class OauthFlows(BaseModel):
    type: str
    properties: Properties44
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool
    field_defs: FieldDefs3 = Field(..., alias='$defs')


class Items10(BaseModel):
    type: str


class AdditionalProperties19(BaseModel):
    type: str
    items: Items10


class SecurityRequirement(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    type: str
    additionalProperties: AdditionalProperties19


class PatternProperties4(BaseModel):
    field_x_: bool = Field(..., alias='^x-')


class SpecificationExtensions(BaseModel):
    field_comment: str = Field(..., alias='$comment')
    patternProperties: PatternProperties4


class AdditionalProperties20(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Examples2(BaseModel):
    type: str
    additionalProperties: AdditionalProperties20


class Properties49(BaseModel):
    example: bool
    examples: Examples2


class Examples1(BaseModel):
    properties: Properties49


class AdditionalProperties21(BaseModel):
    type: str


class MapOfStrings(BaseModel):
    type: str
    additionalProperties: AdditionalProperties21


class Style7(BaseModel):
    const: str


class Properties50(BaseModel):
    style: Style7


class If20(BaseModel):
    properties: Properties50
    required: List[str]


class Explode3(BaseModel):
    default: bool


class Properties51(BaseModel):
    explode: Explode3


class Then20(BaseModel):
    properties: Properties51


class Properties52(BaseModel):
    explode: Explode3


class Else9(BaseModel):
    properties: Properties52


class StylesForForm(BaseModel):
    if_: If20 = Field(..., alias='if')
    then: Then20
    else_: Else9 = Field(..., alias='else')


class FieldDefs(BaseModel):
    info: Info1
    contact: Contact1
    license: License1
    server: Server
    server_variable: ServerVariable = Field(..., alias='server-variable')
    components: Components1
    paths: Paths1
    path_item: PathItem = Field(..., alias='path-item')
    path_item_or_reference: PathItemOrReference = Field(
        ..., alias='path-item-or-reference'
    )
    operation: Operation
    external_documentation: ExternalDocumentation = Field(
        ..., alias='external-documentation'
    )
    parameter: Parameter
    parameter_or_reference: ParameterOrReference = Field(
        ..., alias='parameter-or-reference'
    )
    request_body: RequestBody1 = Field(..., alias='request-body')
    request_body_or_reference: RequestBodyOrReference = Field(
        ..., alias='request-body-or-reference'
    )
    content: Content2
    media_type: MediaType = Field(..., alias='media-type')
    encoding: Encoding1
    responses: Responses2
    response: Response
    response_or_reference: ResponseOrReference = Field(
        ..., alias='response-or-reference'
    )
    callbacks: Callbacks2
    callbacks_or_reference: CallbacksOrReference = Field(
        ..., alias='callbacks-or-reference'
    )
    example: Example
    example_or_reference: ExampleOrReference = Field(..., alias='example-or-reference')
    link: Link
    link_or_reference: LinkOrReference = Field(..., alias='link-or-reference')
    header: Header
    header_or_reference: HeaderOrReference = Field(..., alias='header-or-reference')
    tag: Tag
    reference: Reference
    schema_: Schema5 = Field(..., alias='schema')
    security_scheme: SecurityScheme = Field(..., alias='security-scheme')
    security_scheme_or_reference: SecuritySchemeOrReference = Field(
        ..., alias='security-scheme-or-reference'
    )
    oauth_flows: OauthFlows = Field(..., alias='oauth-flows')
    security_requirement: SecurityRequirement = Field(..., alias='security-requirement')
    specification_extensions: SpecificationExtensions = Field(
        ..., alias='specification-extensions'
    )
    examples: Examples1
    map_of_strings: MapOfStrings = Field(..., alias='map-of-strings')
    styles_for_form: StylesForForm = Field(..., alias='styles-for-form')


class Model(BaseModel):
    field_id: str = Field(..., alias='$id')
    field_schema: str = Field(..., alias='$schema')
    description: str
    type: str
    properties: Properties
    required: List[str]
    anyOf: List[AnyOfItem]
    field_ref: str = Field(..., alias='$ref')
    unevaluatedProperties: bool
    field_defs: FieldDefs = Field(..., alias='$defs')

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, HttpUrl


class Contact(BaseModel):
    name: Optional[str] = Field(
        None, description="The identifying name of the contact person/organization."
    )
    url: Optional[HttpUrl] = Field(
        None,
        description="The URL pointing to the contact information. MUST be in the format of a URL.",
    )
    email: Optional[str] = Field(
        None,
        description="The email address of the contact person/organization. MUST be in the format of an email address.",
    )


class License(BaseModel):
    name: str = Field(..., description="The license name used for the API.")
    url: Optional[HttpUrl] = Field(
        None,
        description="A URL to the license used for the API. MUST be in the format of a URL.",
    )


class Info(BaseModel):
    title: str = Field(..., description="The title of the application.")
    version: str = Field(
        ...,
        description="The version of the OpenAPI document (which is distinct from the OpenAPI Specification version or the API implementation version).",
    )
    description: Optional[str] = Field(
        None,
        description="A short description of the application. CommonMark syntax MAY be used for rich text representation.",
    )
    termsOfService: Optional[HttpUrl] = Field(
        None,
        description="A URL to the Terms of Service for the API. MUST be in the format of a URL.",
    )
    contact: Optional[Contact] = Field(
        None, description="The contact information for the exposed API."
    )
    license: Optional[License] = Field(
        None, description="The license information for the exposed API."
    )


class ServerVariable(BaseModel):
    enum: Optional[List[str]] = Field(
        None,
        description="An enumeration of string values to be used if the substitution options are from a limited set.",
    )
    default: str = Field(
        ...,
        description="The default value to use for substitution, which SHALL be sent if an alternate value is not supplied.",
    )
    description: Optional[str] = Field(
        None,
        description="An optional description for the server variable. CommonMark syntax MAY be used for rich text representation.",
    )


class Server(BaseModel):
    url: str = Field(
        ...,
        description="A URL to the target host. This URL supports server variables and MAY be relative.",
    )
    description: Optional[str] = Field(
        None,
        description="An optional string describing the host designated by the URL.",
    )
    variables: Optional[Dict[str, ServerVariable]] = Field(
        None, description="A map between a variable name and its value."
    )


class Reference(BaseModel):
    ref: str = Field(..., alias="$ref", description="The reference string.")


class Schema(BaseModel):
    type: Optional[str] = Field(None, description="The type of the schema.")
    properties: Optional[Dict[str, Union["Schema", Reference]]] = Field(
        None, description="The properties of the schema."
    )
    additionalProperties: Union[bool, "Schema", None] = Field(
        None,
        description="Indicates that the schema is for an object with additional properties.",
    )
    description: Optional[str] = Field(
        None, description="A short description of the schema."
    )
    format: Optional[str] = Field(
        None, description="The extending format for the previously mentioned type."
    )
    items: Optional[Union["Schema", Reference]] = Field(
        None, description="Items for array type."
    )


Schema.model_rebuild()


class PathItem(BaseModel):
    ref: Optional[str] = Field(
        None,
        alias="$ref",
        description="Allows for an external definition of this path item.",
    )
    summary: Optional[str] = Field(
        None, description="A short summary of what the operation does."
    )
    description: Optional[str] = Field(
        None,
        description="A verbose explanation of the operation behavior. CommonMark syntax MAY be used for rich text representation.",
    )
    # Additional fields representing operations (get, put, post, delete, etc.) will be added here.


class Paths(BaseModel):
    __root__: Dict[str, PathItem] = Field(
        ..., description="The available paths and operations for the API."
    )


class Components(BaseModel):
    schemas: Optional[Dict[str, Union[Schema, Reference]]] = Field(
        None, description="An object to hold reusable Schema Objects."
    )
    # Additional component fields will be added here.


class Operation(BaseModel):
    tags: Optional[List[str]] = Field(
        None, description="A list of tags for API documentation control."
    )
    summary: Optional[str] = Field(
        None, description="A short summary of what the operation does."
    )
    description: Optional[str] = Field(
        None,
        description="A verbose explanation of the operation behavior. CommonMark syntax MAY be used for rich text representation.",
    )
    # Additional fields for operation object will be added here.


class Parameter(BaseModel):
    name: str = Field(..., description="The name of the parameter.")
    in_: str = Field(..., alias="in", description="The location of the parameter.")
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
    # Additional fields for parameter object will be added here.


class RequestBody(BaseModel):
    description: Optional[str] = Field(
        None, description="A brief description of the request body."
    )
    content: Dict[str, "MediaType"] = Field(
        ..., description="The content of the request body."
    )
    required: Optional[bool] = Field(
        None, description="Determines if the request body is required in the request."
    )


class MediaType(BaseModel):
    schema: Optional[Union[Schema, Reference]] = Field(
        None, description="The schema defining the type used for the request body."
    )
    # Additional fields for media type object will be added here.


RequestBody.model_rebuild()
MediaType.model_rebuild()


class OpenAPI(BaseModel):
    openapi: str = Field(
        ...,
        description="This string MUST be the version number of the OpenAPI Specification that the OpenAPI document uses.",
    )
    info: Info = Field(
        ...,
        description="Provides metadata about the API. The metadata MAY be used by tooling as required.",
    )
    paths: Paths = Field(
        ..., description="The available paths and operations for the API."
    )
    components: Optional[Components] = Field(
        None, description="An element to hold various schemas for the document."
    )
    servers: Optional[List[Server]] = Field(
        None,
        description="An array of Server Objects, which provide connectivity information to a target server.",
    )
    # Additional top-level fields can be added here.


# Example usage to be provided as before

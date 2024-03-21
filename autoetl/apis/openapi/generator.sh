#!/bin/bash

# https://koxudaxi.github.io/datamodel-code-generator/

echo "Generating OpenAPI data models..."

datamodel-codegen \
    --input openapi_spec_20.json \
    --output openapi_spec_20.py \
    --input-file-type=jsonschema

datamodel-codegen \
    --input openapi_spec_30.json \
    --output openapi_spec_30.py \
    --input-file-type=jsonschema

datamodel-codegen \
    --input openapi_spec_31.json \
    --output openapi_spec_31.py \
    --input-file-type=jsonschema

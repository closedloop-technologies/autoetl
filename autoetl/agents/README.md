# autoETL Agents

Conversational Agents used to debug and improve API documentation and the ETL process.

We are using Anthropic but will support OpenAI and other conversational agents soon.


    print(spec)

    validate(spec, cls=OpenAPIV2SpecValidator)
    validate(spec, cls=OpenAPIV30SpecValidator)
    validate(spec, cls=OpenAPIV31SpecValidator)

    errors_iterator = OpenAPIV31SpecValidator(spec).iter_errors()
    for e in errors_iterator:
        print(e)
    # validate(spec)
    print(f"Valid spec: {fname}")

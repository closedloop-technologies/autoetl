from typing import Union
from .openapi_spec_20 import Properties as OpenAPIObjectV20
from .openapi_spec_30 import Properties as OpenAPIObjectV30
from .openapi_spec_31 import Properties as OpenAPIObjectV31

OpenAPIObject = Union[OpenAPIObjectV20, OpenAPIObjectV30, OpenAPIObjectV31]

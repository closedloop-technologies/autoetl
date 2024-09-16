import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from type_generator import generate_request_types, generate_response_types

logger = logging.getLogger(__name__)


@dataclass
class EntityType:
    name: str
    properties: Dict[str, str]
    relationships: List[Tuple[str, str]] = field(default_factory=list)

    def to_typescript(self) -> str:
        type_definition = f"export interface {self.name} {{\n"
        for prop_name, prop_type in self.properties.items():
            type_definition += f"  {prop_name}: {prop_type};\n"
        type_definition += "}\n"
        return type_definition

    def to_python(self) -> str:
        from pydantic import BaseModel
        from typing import Optional

        class_definition = f"class {self.name}(BaseModel):\n"
        for prop_name, prop_type in self.properties.items():
            if "null" in prop_type:
                class_definition += f"    {prop_name}: Optional[{prop_type.replace(' | null', '')}] = None\n"
            else:
                class_definition += f"    {prop_name}: {prop_type}\n"
        return class_definition


def identify_entity_types(swagger_spec: List[Dict]) -> List[EntityType]:
    request_types = generate_request_types(swagger_spec)
    response_types = generate_response_types(swagger_spec)

    entity_types = []

    for type_name, type_definition in {**request_types, **response_types}.items():
        entity_type = parse_type_definition(type_name, type_definition)
        if entity_type:
            entity_types.append(entity_type)

    for entity_type in entity_types:
        for endpoint_info in swagger_spec:
            path = endpoint_info["path"]
            method = endpoint_info["method"]
            request_type_name = f"{path}_{method}_Request"
            response_type_name = f"{path}_{method}_Response"

            if request_type_name == entity_type.name:
                for param in endpoint_info["parameters"]:
                    ref_type_name = param["type"]
                    entity_type.relationships.append((ref_type_name, "param"))
            elif response_type_name == entity_type.name:
                # TODO: Analyze response schema to identify relationships
                pass

    return entity_types


def parse_type_definition(type_name: str, type_definition: str) -> EntityType:
    try:
        properties = {}
        for line in type_definition.splitlines():
            if ":" in line:
                prop_name, prop_type = (
                    line.strip().split(":")[0],
                    ":".join(line.strip().split(":")[1:]).strip(),
                )
                properties[prop_name] = prop_type

        return EntityType(name=type_name, properties=properties)
    except (IndexError, ValueError) as e:
        logger.error(f"Error parsing type definition for {type_name}: {e}")
        return None

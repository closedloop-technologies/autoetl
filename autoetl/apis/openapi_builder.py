"""This builds the openapi.json file from the openapi spec url or seed urls

Generates a openapi v 3.1 spec here
{project_root}/apis/{api}/openapi_spec/openapi{_v0}.spec

3. Get list of endpoints from the crawl
1. get likely specs from all crawls
2. evaluate the quality of the specs
   1. valid spec?
   1. endpoint coverage
   1. static analysis of each endpoint and its inputs and outputs
   2. dynamic analysis
      1. query endpoints with different inputs, validate types of outputs
   3. LLM analysis of names, tags, descriptions, etc

4. Given Spec shortcomings, query the user for more information
"""

from openapi_spec_validator import (
    OpenAPIV2SpecValidator,
    OpenAPIV30SpecValidator,
    validate,
)
import json
from openapi_spec_validator import validate_url
from openapi_spec_validator import OpenAPIV31SpecValidator
from prefect import flow


from autoetl.agents.doc_bot import AutoETLDocBot
from autoetl.apis.crud import list_apis
from autoetl.project import ETLProject, load_project


def get_crawl_urls(project: ETLProject, api_id) -> list[str]:
    """Get likely endpoints from the crawl"""
    urls = set([])
    for cg in (project.fdir / "apis" / api_id / "docs").rglob("crawl_graph.json"):
        with open(cg, "r") as fh:
            data = json.load(fh)

        urls = urls.union(
            {link.get("source") for link in data}
            | {link.get("target") for link in data if link.get("follow")}
        )
    return urls


def get_crawl_openapi_specs(project: ETLProject, api_id) -> list[str]:
    """Get likely openapi specs"""
    return list((project.fdir / "apis" / api_id / "docs").rglob("openapi_spec/*.json"))


@flow
def create_openapi_spec(project, api, api_related_urls):
    """Create openapi spec
    should satisfy the following:
    validate(spec, cls=OpenAPIV31SpecValidator)
    """
    spec = {}
    validate(spec, cls=OpenAPIV31SpecValidator)
    with open(project.fdir / "apis" / api.id / "openapi", "w") as fh:
        json.dump(spec, fh)
    return {}


def main():
    project = load_project()
    # 1. get likely specs from all crawls
    project.fdir
    apis = list_apis(project.fdir)
    print(apis)
    api = apis[0]

    # Get likely endpoints from the crawl
    api_related_urls = get_crawl_urls(project, api.id)
    spec_fnames = get_crawl_openapi_specs(project, api.id)
    if not spec_fnames:
        new_spec_fname = create_openapi_spec(project, api, api_related_urls)
        spec_fnames = [new_spec_fname]

    for fname in spec_fnames:
        with open(fname, "r") as fh:
            spec = json.load(fh)
            from autoetl.apis.openapi import OpenAPIObjectV20

            x = OpenAPIObjectV20(**spec)
            agent = AutoETLDocBot()
            new_spec = agent.upgrade_openapi_spec(spec)
            # new_spec = upgrade_openapi_spec(project, api, spec)

    # Select the best spec
    if len(spec_fnames) > 1:
        raise ValueError("Multiple openapi specs found")

    # rename the selected spec to openapi.json

    # Score the quality of the spec

    # If no exception is raised by validate_url(), the spec is valid.
    # validate_url("http://example.com/openapi.json")


if __name__ == "__main__":
    main()

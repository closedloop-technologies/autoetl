"""This is a post-processing workflow to support RAG workflows
"""

from autoetl.apis.crud import list_apis
from autoetl.project import ETLProject, load_project


def get_crawl_docs(project: ETLProject, api_id: str, crawl_id) -> list[str]:
    """Read the crawl graph"""
    urls = set([])
    for cg in (project.fdir / "apis" / api_id / "docs").rglob(
        "crawl-*/docs/url-*/doc-*.data"
    ):
        print(cg)
        # with open(cg, "r") as fh:
        #     data = json.load(fh)


if __name__ == "__main__":
    project = load_project()
    apis = list_apis(project.fdir)

    get_crawl_docs(project, apis[0].id, "crawl-c1qgk5tpj6p338x3c5zqknkl")

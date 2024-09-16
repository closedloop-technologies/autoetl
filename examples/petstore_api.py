import asyncio
from autoetl.project import ETLProject


async def main():
    project = ETLProject(
        name="Petstore API2",
        description="A simple project to demonstrate the Petstore API",
    )
    api = await project.add_api(name="Petstore", docs=["https://petstore.swagger.io/"])
    await project.crawl_api_docs(api.id)


if __name__ == "__main__":

    asyncio.run(main())

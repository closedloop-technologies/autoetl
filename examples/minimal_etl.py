"""This is the minimal ETL example


# Initialize a new AutoETL project and enter the directory
autoetl init rain_day_project \
    --name "Rental Propert Dashboard" \
    --description "Daily Weather data for all of my airbnb properties" \
    --source "https://api.weather.com/data" \
    --source "https://api.airbnb.com/hostdata" \
    --target "postgresql://user:password@localhost:5432/mydatabase" \
    --env=.env

autoetl run rain_day_project --daily
"""

import asyncio

from autoetl.project import ETLProject, crawl


async def minimal_example():
    print("This is the minimal ETL example")
    print("Initialize a new AutoETL project and enter the directory")
    project = ETLProject()
    await project.init()

    # Add API
    api = await project.add_api()
    await crawl(api)

    fn = await project.add_function()
    await crawl(fn)

    db = await project.add_database()
    await crawl(db)

    etl = await project.build_etl(
        name="", description="", sources=[api, fn], targets=[db]
    )
    api = await project.build_service()

    infrastructure = await project.deploy([etl, api])

    # Run the ETL a single time
    await infrastructure[etl.id].run()

    # Launch the API server
    await infrastructure[api.id].run()

    await project.teardown()


if __name__ == "__main__":
    asyncio.run(minimal_example())

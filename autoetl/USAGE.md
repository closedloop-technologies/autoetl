# Usage of AutoETL
An advanced Code Generation tool

API Documentation, Discovery, Governance (Monitoring), Security and Deployment

https://chat.openai.com/share/9f44197d-d4a5-4c9d-9d86-711c88113a4b


* Connect API to Database fast - Devs spend 30% of their time on this
* Improve documentation - 80%+ of the time, the documentation is wrong
  - Improve documentation of your vendors
  - Improve your own documentation
  - Share documentation with your team
* Robustness
  - Monitor Sources for errors
  - Vendor changes API
  - Performance Degradation
  - Cost Monitoring
* Security
  - Rate Limiting
  - Authentication
  - Data Validation
  - Data Privacy


Here's the main user story.
A dev has to write a script to extract data from an API and load it into a database.
* The database is a relational database which may or not be empty
* The API is a REST API.
* The data from the API is in JSON format but may be a nested and complex object
* The API must be queried at some regular interval
* The data must be validated before being loaded into the database
* Multiple API calls may be chained together to get the data
* The data may be transformed before being loaded into the database
* The data will be upserted into the database

This is a common task for a data engineer. AutoETL is a tool that can help with this task.

### Extraction - Crawling Endpoints
It should improve documentation
Validate types

1. Add API endpoints
2. Crawl API to improve documentation, add typing and validate the documentation
3. Generate python typing and openapi schema
4. Create a data model to map the API data to the database add types for all inputs (enumeration, regex, etc)
5. Authentication - RBAC model
6. Rate limiting
7. Cost model
8. Authentication

8. Error handling
9. Data validation

### Transformation
1. Register a target database
2. Crawl the database to add metadata, improve documentation, add typing and distributions
3. Generate a graph of the database schema (tables, columns, relationships, indexes, constraints, etc)
4. Describe the ETL in human readable language.  This is the ETL plan.
5. Generate an
5. Map API data model to the database data model.
   1. Identity the transformations that need to be done.
   2. Schema changes that need to be made to the target
   3. Data enrichment that needs to be done to the source data (for example calling an IP lookup service to get the country of an IP address)

### Loading
Generate the ETL code
1. Create a query plan for the API
    1. Chains calls
    2. Pagination
    3. Rate limiting
    4. Error handling
    5. Data validation
2. Create Transformation steps
    1. Merging, splitting, filtering, etc
    2. cannonicalization of data
    3. transformation of data
    4. applying enrichment
3. Create staging tables for the data
    1. Result tables have local dependencies and are roughly the same shape as the target tables
    2. Staging tables are used to store the data before it is loaded into the target tables
    3. Entity resolution to map rows in target database to rows in the staging tables
    4. Apply upsertion logic to the staging tables, apply human in the loop logic to the staging tables
4. Monitoring
    1. response times, payload sizes, error rates, etc
5. Testing
    1. Unit tests (Mock Data, Mock API, Mock Database)
    2. Integration tests
    3. End to end tests

### Serving
Given a target database, generate a REST API to serve the data
1. Create a CRUD API for the target database
2. Create a data view API for the target database
3. Create a complex CRUD API for the target database
4. Create a custom transform API for the target database
5. Create a calculator and points API for the target database
6. Create a RBAC API for the target database


## How to use AutoETL

AutoETL is a command line tool.

The first step is to create a project.  A project is a directory that contains all the configuration files for the ETL process.

```bash
autoetl init
```
Continue with all of the other commands described above


```bash
#!/bin/bash

# Initialize a new AutoETL project and enter the directory
autoetl init my_etl_project
cd my_etl_project

# Add API endpoint configuration
autoetl api add --name "MyAPIEndpoint" --url "https://api.example.com/data" --method "GET" --auth "Bearer YOUR_API_KEY"

# Crawl the API to improve documentation and add typing
autoetl api crawl --name "MyAPIEndpoint" --generate-typing

# Generate data model from API schema
autoetl model generate --from-api "MyAPIEndpoint" --output-model "ApiDataModel"

# Register the target database
autoetl db register --type "postgresql" --host "localhost" --port "5432" --user "user" --password "password" --database "mydatabase"

# Crawl the target database to add metadata and generate a schema graph
autoetl db crawl --database "mydatabase" --generate-schema-graph

# Define transformations and mappings from API data model to database schema
autoetl transform define --source "ApiDataModel" --target "mydatabase" --transformation-file "transformations.json"

# Generate ETL code based on defined transformations and mappings
autoetl etl generate --source "ApiDataModel" --target "mydatabase" --transformation-file "transformations.json" --output "etl_script.py"

# Deploy ETL script to run at regular intervals
autoetl etl deploy --script "etl_script.py" --schedule "0 */6 * * *" # Every 6 hours

# Setup monitoring for the ETL process
autoetl monitor setup --etl "etl_script.py" --alerts "email:dev@example.com"

# Generate REST API for the target database
autoetl serve generate --database "mydatabase" --api-name "MyDatabaseAPI"

# Start the server to serve the generated REST API
autoetl serve start --api "MyDatabaseAPI" --port 8080

echo "AutoETL process setup and API service started."
```

## Project Layout

```
my_etl_project/
│
├── autoetl.yaml # Configuration file for the project
├── .env # Environment variables
│
├── domain_knowledge/{domain_name}
│   ├── README.md # Domain knowledge such as (business rules, constraints, etc) that are used to seed the ETL process.  This is provided as a human readable document
│   ├── domain.graph # Entity relationship property graph definitions / the ontology for the domain
│   └── ...
│
├── apis/{api_name}/{version}/
│   ├── spec.yaml # API endpoint configuration (name, url, method, auth, docs urls, etc)
│   ├── openapi_{as+of+time}_{hash}.yaml
│   ├── openapi.yaml
│   ├── model.py # Generated pydantic model from openapi.yaml
│   ├── schema.graph # Maps endpoint input and output datatypes across the API
│   └── ...
│
├── fns/{namespace}/{fn_name}/
│   ├── spec.yaml # API endpoint configuration (name, url, method, auth, etc)
│   ├── openapi.yaml
│   ├── model.py # Generated pydantic model from openapi.yaml
│   ├── schema.graph # Maps endpoint input and output datatypes across the function
│   └── ...
│
├── db/{database_name}
│   ├── spec.yaml # Database configuration (type, host, port, user, password, database, etc)
│   ├── schema.prisma
│   ├── model.py  # Generated from schema.prisma
│   ├── schema.graph # Map of the database schema (tables, columns, relationships, indexes, constraints, etc and their sampled types and distributions)
│   └── ...
│
├── etl/{etl_name}
│   ├── schema_alignment.graph # Aligns the API data model to the database schema given domain knowledge
│   └── query_plan.graph # Maps out the ETL process (extraction, transformation, to staging)
│   └── resolution.graph # Given a set of staging tables, maps the resolution process to the target tables.  Maps out the upsertion process
│   ├── script.py
│   |── test_script.py
│   └── ...
│
├── deployment/{deployment_name}
|   ├── config.yaml  # Scheduling, alerting, infrastructure of the ETL processes
|   ├── run.py  # Simple script to run the ETL process
│   └── ...
│
├── serve/{api_name}
│   ├── spec.yaml # API configuration (RBAC, name, version, security, rate-limiting, etc)
│   ├── openapi.yaml
│   ├── model.py  # Generated from openapi.yaml
│   ├── api.py  # Generated from openapi.yaml and each endpoint is a function that calls the database or does calculations, or calls functions
│   └── ...
│
```

```bash
#!/bin/bash

# Initialize a new AutoETL project and enter the directory
autoetl init rain_day_project \
    --name "Rental Propert Dashboard" \
    --description "Daily Weather data for all of my airbnb properties" \
    --source "https://api.weather.com/data" \
    --source "https://api.airbnb.com/hostdata" \
    --target "postgresql://user:password@localhost:5432/mydatabase" \
    --env=.env

autoetl run rain_day_project --daily
```
This should crawl the APIs, generate the data models, generate the database schema, and generate the ETL code.  It should also generate the REST API for the target database.

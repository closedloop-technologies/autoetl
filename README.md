# autoetl

Wire up APIs with databases in minutes. Ingest, persist, enrich, merge and serve data automagically.


## Project Structure

Creates a new project directory
```
automath init etl_project
tree -av
```

Creates this folder structure
```bash
.
├── .env
├── apis
├── autoetl.yaml
├── db
├── deployment
├── domain_knowledge
├── etl
├── fns
└── serve
```

```bash
# Initialize a new AutoETL project and enter the directory
autoetl init petstore \
    --source "https://petstore.swagger.io/v2/swagger.json" \
    # --source "https://petstore.swagger.io/"
    --env=.env

autoetl crawl --project petstore
```

## Coming Soon
Read more at [autoetl.dev](https://autoetl.dev) or email us at [sean@closedloop.tech](mailto:sean@closedloop.tech)

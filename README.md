# aussiedlerbote-scrapers

## Pipelines
To validate and change the item's data. Written in order of execution

### DropDpaPipeline
Takes list of sources ("Quelle" on article page) and checks if 'dpa' is present. Drops article if 'dpa' is present.

### DuplicateOrUpdatedPipeline
First validates if 'url' and 'article_html' params are present within the received item. If absent -> DropItem.
Then using hashlib.md5() generate stable hash for both url and article_html, connect to Postgres db using psycopg module and credentials retrieved from the environment, select rows in db where url hash matches. If 0 rows are received -> the url is new -> add url and article hash to db and pass the item further.

If received any row -> compare article_html hashes. If equal -> DropItem(Duplicate). if not equal -> set 'signal' to sig:update -> add article to db and pass item further.

### NtvArticleDefaultValuesPipeline
Fills item with default values if value wasn't set before. This is done to adhere to digital.wires format

## Relational Database
We are using Postgresql to store url and article_html as a 32 characters long hex hash. Here is the table structure:
```
CREATE TABLE article_hashes(
    id SERIAL NOT NULL PRIMARY KEY,
    url_hash UUID NOT NULL,
    article_hash UUID NOT NULL
);
```


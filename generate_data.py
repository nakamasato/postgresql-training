import argparse
import datetime
import random
from unicodedata import category
import uuid
from random import normalvariate, randrange

import psycopg2

dsn = "dbname=test_db host=localhost user=postgres password=postgres"
startDate = datetime.datetime(2021, 1, 20, 13, 00)
now = datetime.datetime.now()
days = (now - startDate).days


def generate_items(n):
    rows = []
    for i in range(n):
        item_id = generate_id()
        created_at = random_date(startDate)  # .strftime("%Y-%m-%d %H:%M:%S")
        name = f"item-{i}"
        status = random.randint(1, 3)
        rows.append(
            (
                item_id,  # id serial PRIMARY KEY
                name,  # name VARCHAR ( 50 ) UNIQUE NOT NULL
                status,  # status SMALLINT NOT NULL
                created_at,  # created_on TIMESTAMP NOT NULL
            )
        )
    return rows


def generate_categories(n):
    rows = []
    for i in range(n):
        category_id = f"category-{i}"
        created_at = random_date(startDate)  # .strftime("%Y-%m-%d %H:%M:%S")
        name = f"category-{i}"
        rows.append(
            (
                category_id,  # id text NOT NULL PRIMARY KEY,
                name,  # name VARCHAR(50) UNIQUE NOT NULL,
                created_at,  # TIMESTAMP NOT NULL
            )
        )
    return rows


def insert(table, rows):
    num_of_fields = len(rows[0])
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                f"INSERT INTO {table} VALUES({','.join(['%s'] * num_of_fields)})", rows
            )


def get_item_ids_as_generator():
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM items;")
            for row in cur:
                yield row


def get_category_ids():
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM categories;")
            return cur.fetchall()


def truncate():
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            for table in ["items", "categories"]:
                cur.execute(f"truncate {table} CASCADE;")


def generate_item_categories():
    rows = []
    category_ids = get_category_ids()
    for iid in get_item_ids_as_generator():
        item_category_id = generate_id()
        category_id = normal_choice(category_ids, 10, 5)
        item_id = iid
        created_at = random_date(startDate)
        updated_at = random_date(created_at)
        rows.append(
            [
                item_category_id,  # id character varying NOT NULL,
                category_id,  # category_id text NOT NULL,
                item_id,  # item_id text NOT NULL,
                created_at,  # created_at timestamp NOT NULL,
                updated_at,  # updated_at timestamp NOT NULL,
            ]
        )
    return rows


def generate_id():
    return str(uuid.uuid4())


def random_bool_str(prob_of_true):
    if random.random() < prob_of_true:
        return "t"
    else:
        return "f"


def random_date(start):
    max_days = (now - start).days
    if max_days == 0:
        return start + datetime.timedelta(
            hours=randrange(24), minutes=randrange(60), seconds=randrange(60)
        )
    else:
        return start + datetime.timedelta(
            days=randrange(max_days),
            hours=randrange(24),
            minutes=randrange(60),
            seconds=randrange(60),
        )


def normal_choice(lst, mean=None, stddev=None):
    if mean is None:
        # if mean is not specified, use center of list
        mean = (len(lst) - 1) / 2

    if stddev is None:
        # if stddev is not specified, let list be -3 .. +3 standard deviations
        stddev = len(lst) / 6

    while True:
        index = int(normalvariate(mean, stddev) + 0.5)
        if 0 <= index < len(lst):
            return lst[index]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--number-of-items",
        "-i",
        dest="number_of_items",
        type=int,
        default=10,
        help="number of items to generate (default: 10000)",
    )

    parser.add_argument(
        "--number-of-categories",
        "-c",
        dest="number_of_categories",
        type=int,
        default=3,
        help="number of items to generate (default: 10000)",
    )

    args = parser.parse_args()

    truncate()
    print("truncated")

    rows = generate_items(args.number_of_items)
    insert("items", rows)
    print(f"inserted {len(rows)} items")

    rows = generate_categories(args.number_of_categories)
    insert("categories", rows)
    print(f"inserted {len(rows)} categories")

    rows = generate_item_categories()
    insert("item_categories", rows)
    print(f"inserted {len(rows)} item_categories")

import argparse
import csv
import datetime
import os
import random
import time
import uuid
from random import normalvariate, randrange

import psycopg2

dsn = "dbname=test_db host=localhost user=postgres password=postgres"
DEFAULT_START_DATE = datetime.datetime(2020, 1, 1, 00, 00)
DEFAULT_END_DATE = datetime.datetime(2022, 1, 1, 00, 00)
CHUNKSIZE = 100


def generate_items(n, start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE):
    rows = []
    for i in range(n):
        item_id = generate_id()
        created_at = random_date(start_date, end_date).strftime("%Y-%m-%d %H:%M:%S")
        name = f"item-{i}"
        status = random.randint(1, 3)
        rows.append(
            [
                item_id,  # id serial PRIMARY KEY
                name,  # name VARCHAR ( 50 ) UNIQUE NOT NULL
                status,  # status SMALLINT NOT NULL
                created_at,  # created_on TIMESTAMP NOT NULL
            ]
        )
    return rows


def generate_categories(n, start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE):
    rows = []
    for i in range(n):
        category_id = f"category-{i}"
        created_at = random_date(start_date, end_date).strftime("%Y-%m-%d %H:%M:%S")
        name = f"category-{i}"
        rows.append(
            [
                category_id,  # id text NOT NULL PRIMARY KEY,
                name,  # name VARCHAR(50) UNIQUE NOT NULL,
                created_at,  # TIMESTAMP NOT NULL
            ]
        )
    return rows


def insert(table, rows):
    num_of_fields = len(rows[0])
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            for i in range(0, len(rows), CHUNKSIZE):
                cur.executemany(
                    f"INSERT INTO {table} VALUES({','.join(['%s'] * num_of_fields)})",
                    rows[i : i + CHUNKSIZE],
                )


def insert_csv(table, csv):
    cmd = f"docker exec -i postgres psql -U postgres test_db -c \"\copy {table} from STDIN with DELIMITER ','\" < {csv}"
    os.system(cmd)


def get_item_ids_as_generator():
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM items;")
            for row in cur:
                yield row[0]


def get_category_ids():
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM categories;")
            return [row[0] for row in cur.fetchall()]


def truncate():
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            for table in ["items", "categories"]:
                cur.execute(f"truncate {table} CASCADE;")


def generate_item_categories(start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE):
    rows = []
    category_ids = get_category_ids()
    for iid in get_item_ids_as_generator():
        item_category_id = generate_id()
        category_id = normal_choice(category_ids, 10, 5)
        item_id = iid
        created_at = random_date(start_date, end_date)
        updated_at = random_date(created_at, end_date)
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


def random_date(start, end):
    max_days = (end - start).days
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


def write_to_csv(rows, filename):
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate data.")
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
        help="number of categories to generate (default: 3)",
    )

    args = parser.parse_args()
    ts = time.time()
    truncate()
    print(f"truncated. {time.time() - ts:.2f}")

    tmp_data_csv = "data.csv"

    rows = generate_items(args.number_of_items)
    write_to_csv(rows, tmp_data_csv)
    print(f"generated {len(rows)} items. {time.time() - ts:.2f}")
    insert_csv("items", tmp_data_csv)
    print(f"inserted {len(rows)} items. {time.time() - ts:.2f}")

    rows = generate_categories(args.number_of_categories)
    write_to_csv(rows, tmp_data_csv)
    print(f"generated {len(rows)} categories. {time.time() - ts:.2f}")
    insert_csv("categories", tmp_data_csv)
    print(f"inserted {len(rows)} categories. {time.time() - ts:.2f}")

    rows = generate_item_categories()
    write_to_csv(rows, tmp_data_csv)
    print(f"generated {len(rows)} item_categories. {time.time() - ts:.2f}")
    insert_csv("item_categories", tmp_data_csv)
    print(f"inserted {len(rows)} item_categories. {time.time() - ts:.2f}")

## Prepare data

1. Run container

    ```
    docker-compose -f docker-compose.yml up -d
    ```

1. Update schema (drop & create)

    ```
    docker exec -i postgres psql -U postgres test_db < test_table.sql
    ```

1. Generate data

    |num of records|roughly expected time|
    |---|---|
    |100,000|10s|
    |1,000,000|20s|
    |10,000,000|1000s|

    ```
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

    ```
    python generate_data.py -i 100000 -c 20
    ```

1. Check data

    ```
    docker exec -i postgres psql -U postgres test_db -c "select * from items limit 10"
    ```

    <details>

    ```
                      id                  |  name  | status |     created_on
    --------------------------------------+--------+--------+---------------------
     2c0bb163-6bf1-475c-b4ef-0a0a6e9f91e0 | name-0 |      1 | 2021-02-12 01:23:12
     e6d22047-0196-464a-908e-b4a07db53b47 | name-1 |      3 | 2022-08-01 16:57:56
     4abe9fa4-abc6-42b6-9426-9e6260b855d5 | name-2 |      3 | 2021-04-15 23:28:35
     028c91c2-93eb-480a-a80f-3d184811fef7 | name-3 |      3 | 2021-12-14 13:35:12
     c83ca045-321c-4f52-94a3-9de02d890490 | name-4 |      3 | 2022-09-28 15:35:37
     acbe49bd-74e8-4be2-90cb-1bf855769328 | name-5 |      3 | 2021-11-23 14:11:26
     53ad62cc-5033-47ea-b462-2cbfd707b6e7 | name-6 |      2 | 2022-05-13 22:29:55
     f2fb4124-5891-4fde-9704-8423f51187fa | name-7 |      1 | 2022-07-18 14:22:23
     fe0da270-b0fb-4846-b3cf-54d5abfcb66f | name-8 |      3 | 2021-09-20 18:19:58
     d57765cd-c8e2-41a8-ad15-82a3359f18c1 | name-9 |      2 | 2021-02-19 02:15:43
    (10 rows)
    ```

    ```
    docker exec -i postgres psql -U postgres test_db -c "select * from categories limit 10"

         id     |    name    |     created_at
    ------------+------------+---------------------
     category-0 | category-0 | 2021-08-05 07:06:01
     category-1 | category-1 | 2021-11-18 19:02:48
     category-2 | category-2 | 2021-04-07 15:23:46
     category-3 | category-3 | 2021-05-12 15:21:52
     category-4 | category-4 | 2021-06-07 13:15:27
     category-5 | category-5 | 2022-01-02 13:52:22
     category-6 | category-6 | 2021-12-10 15:47:41
     category-7 | category-7 | 2022-01-19 18:19:37
     category-8 | category-8 | 2022-03-13 17:51:36
     category-9 | category-9 | 2021-11-18 14:44:20
    (10 rows)
    ```

    </details>

    ```
    docker exec -i postgres psql -U postgres test_db -c "select * from item_categories limit 10"
    ```

    <details>

    ```
                      id                  | category_id |               item_id                |     created_at      |     updated_at
    --------------------------------------+-------------+--------------------------------------+---------------------+---------------------
     c8d28294-4059-428a-97a6-6dc6cad7f2a5 | category-12 | 9dd4680f-9e09-4272-ad1a-12a1f6a1324b | 2022-05-25 04:22:56 | 2022-06-30 12:59:56
     54b17fef-c9c1-45eb-bbac-419e7402a355 | category-13 | d5aff8ce-3324-417e-8f91-2b113288e8cf | 2022-01-04 04:46:37 | 2022-10-27 11:29:48
     2e401c19-c22e-4edd-ae5f-a83265144dd3 | category-10 | df6f9175-86ba-4bd2-a29e-caa76dc47e38 | 2021-07-29 13:19:20 | 2021-10-02 01:57:56
     cd991c35-7d98-4257-9964-b12d2faae4e4 | category-12 | 1373c90f-6914-40f0-a69f-e68bbae5955d | 2022-09-25 14:46:46 | 2022-10-10 06:15:34
     87e5717c-3413-4b44-ba73-9c68a247d0de | category-0  | c1c8943a-e590-4155-8e6a-518e24d58bd2 | 2021-12-14 12:52:18 | 2022-04-20 10:47:02
     a731eaed-bd61-43bb-b2e4-1aedd6e06a5d | category-10 | 3b2ce1fe-32fe-4eb0-a39c-8e2a5b47113b | 2022-06-06 23:16:58 | 2022-07-25 14:40:12
     f2a0b3c0-2f03-45c8-81d6-0c8e07049308 | category-2  | c644b3c4-8884-4d1a-8879-acc90575154f | 2022-08-20 13:29:04 | 2022-09-20 04:17:05
     8d1219f1-0914-4aed-b29a-cea3b8c59120 | category-3  | 97cbff50-e5f9-4d57-ad16-aea42ef979c7 | 2021-04-08 12:39:54 | 2021-06-30 02:18:41
     8291e37f-e90a-4d0f-aa99-25598ee1637e | category-8  | f3e3da3c-4dc8-4931-ab34-5988e4e764e9 | 2021-11-16 03:24:32 | 2022-03-18 14:00:24
     bd60a8fc-2444-455e-87b0-99ebcbcc694f | category-5  | 62838307-fb28-4205-94cd-a7730df99f10 | 2022-04-10 04:22:15 | 2022-10-23 06:58:37
    (10 rows)
    ```

    </details>

    Monthly data distribution:

    <details>

    ```
    docker exec -i postgres psql -U postgres test_db -c "select to_char(created_at, 'YYYY-mm'), count(*) from items group by to_char(created_at, 'YYYY-mm')"

     to_char | count
    ---------+--------
     2021-01 | 176123
     2021-02 | 431441
     2021-03 | 478681
     2021-04 | 461558
     2021-05 | 477867
     2021-06 | 462530
     2021-07 | 478206
     2021-08 | 477592
     2021-09 | 462971
     2021-10 | 477343
     2021-11 | 462902
     2021-12 | 477736
     2022-01 | 477982
     2022-02 | 431127
     2022-03 | 476942
     2022-04 | 461021
     2022-05 | 477172
     2022-06 | 463176
     2022-07 | 476883
     2022-08 | 477472
     2022-09 | 462231
     2022-10 | 471044
    (22 rows)
    ```

    </details>

1. Check index
    ```
    docker exec -i postgres psql -U postgres test_db -c "select tablename, indexname, indexdef from pg_indexes where schemaname = 'public' order by tablename, indexname"
    ```

    <details>

    ```
     tablename  |    indexname    |                                 indexdef
    ------------+-----------------+---------------------------------------------------------------------------
     categories | categories_pkey | CREATE UNIQUE INDEX categories_pkey ON public.categories USING btree (id)
     items      | items_pkey      | CREATE UNIQUE INDEX items_pkey ON public.items USING btree (id)
    (2 rows)
    ```

    </details>

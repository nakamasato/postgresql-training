# Postgres Training

## Prepare data

1. Run container

    ```
    docker-compose -f docker-compose.postgres.yml up -d
    ```

1. Update schema (drop & create)

    ```
    docker exec -i postgres psql -U postgres test_db < test_table.sql
    ```

1. Generate data

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

## Explain

### i=10000,c=20

`EXPLAIN`:

```sql
docker exec -i postgres psql -U postgres test_db -c "explain select i.id, i.created_at from items i join item_categories ic on i.id = ic.item_id WHERE ic.category_id in ('category-1', 'category-2', 'category-3') and (i.created_at > '2021-10-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) order by i.created_at desc, i.id desc limit 30"
                                                                                           QUERY PLAN
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=637.58..637.66 rows=30 width=45)
   ->  Sort  (cost=637.58..638.63 rows=418 width=45)
         Sort Key: i.created_at DESC, i.id DESC
         ->  Hash Join  (cost=310.01..625.24 rows=418 width=45)
               Hash Cond: (i.id = ic.item_id)
               ->  Seq Scan on items i  (cost=0.00..288.00 rows=6145 width=45)
                     Filter: ((created_at > '2021-10-01 00:00:00'::timestamp without time zone) OR ((created_at = '2022-01-01 00:00:00'::timestamp without time zone) AND (id < 'test'::text)))
               ->  Hash  (cost=301.50..301.50 rows=681 width=37)
                     ->  Seq Scan on item_categories ic  (cost=0.00..301.50 rows=681 width=37)
                           Filter: (category_id = ANY ('{category-1,category-2,category-3}'::text[]))
(10 rows)
```

`EXPLAIN ANALYZE`:

```sql
docker exec -i postgres psql -U postgres test_db -c "explain analyze select i.id, i.created_at from items i join item_categories ic on i.id = ic.item_id WHERE ic.category_id in ('category-1', 'category-2', 'category-3') and (i.created_at > '2021-10-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) order by i.created_at desc, i.id desc limit 30"
                                                                                           QUERY PLAN
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=637.58..637.66 rows=30 width=45) (actual time=4.946..4.949 rows=30 loops=1)
   ->  Sort  (cost=637.58..638.63 rows=418 width=45) (actual time=4.945..4.947 rows=30 loops=1)
         Sort Key: i.created_at DESC, i.id DESC
         Sort Method: top-N heapsort  Memory: 29kB
         ->  Hash Join  (cost=310.01..625.24 rows=418 width=45) (actual time=2.521..4.852 rows=420 loops=1)
               Hash Cond: (i.id = ic.item_id)
               ->  Seq Scan on items i  (cost=0.00..288.00 rows=6145 width=45) (actual time=0.013..1.763 rows=6140 loops=1)
                     Filter: ((created_at > '2021-10-01 00:00:00'::timestamp without time zone) OR ((created_at = '2022-01-01 00:00:00'::timestamp without time zone) AND (id < 'test'::text)))
                     Rows Removed by Filter: 3860
               ->  Hash  (cost=301.50..301.50 rows=681 width=37) (actual time=2.500..2.500 rows=681 loops=1)
                     Buckets: 1024  Batches: 1  Memory Usage: 54kB
                     ->  Seq Scan on item_categories ic  (cost=0.00..301.50 rows=681 width=37) (actual time=0.039..2.398 rows=681 loops=1)
                           Filter: (category_id = ANY ('{category-1,category-2,category-3}'::text[]))
                           Rows Removed by Filter: 9319
 Planning Time: 1.119 ms
 Execution Time: 5.012 ms
(16 rows)
```

### i=100000,c=100

`EXPLAIN`:

```sql
docker exec -i postgres psql -U postgres test_db -c "explain select i.id, i.created_at from items i join item_categories ic on i.id = ic.item_id WHERE ic.category_id in ('category-1', 'category-2', 'category-3') and (i.created_at > '2021-10-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) order by i.created_at desc, i.id desc limit 30"
                                                                                              QUERY PLAN
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=5886.99..5890.44 rows=30 width=45)
   ->  Gather Merge  (cost=5886.99..6170.81 rows=2468 width=45)
         Workers Planned: 1
         ->  Sort  (cost=4886.98..4893.15 rows=2468 width=45)
               Sort Key: i.created_at DESC, i.id DESC
               ->  Parallel Hash Join  (cost=2499.29..4814.09 rows=2468 width=45)
                     Hash Cond: (i.id = ic.item_id)
                     ->  Parallel Seq Scan on items i  (cost=0.00..2165.41 rows=35966 width=45)
                           Filter: ((created_at > '2021-10-01 00:00:00'::timestamp without time zone) OR ((created_at = '2022-01-01 00:00:00'::timestamp without time zone) AND (id < 'test'::text)))
                     ->  Parallel Hash  (cost=2448.82..2448.82 rows=4037 width=37)
                           ->  Parallel Seq Scan on item_categories ic  (cost=0.00..2448.82 rows=4037 width=37)
                                 Filter: (category_id = ANY ('{category-1,category-2,category-3}'::text[]))
(12 rows)
```

`EXPLAIN ANALYZE`:

```sql
docker exec -i postgres psql -U postgres test_db -c "explain analyze select i.id, i.created_at from items i join item_categories ic on i.id = ic.item_id WHERE ic.category_id in ('category-1', 'category-2', 'category-3') and (i.created_at > '2021-10-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) order by i.created_at desc, i.id desc limit 30"

                                                                                              QUERY PLAN
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=5886.99..5890.44 rows=30 width=45) (actual time=378.801..380.977 rows=30 loops=1)
   ->  Gather Merge  (cost=5886.99..6170.81 rows=2468 width=45) (actual time=378.800..380.973 rows=30 loops=1)
         Workers Planned: 1
         Workers Launched: 1
         ->  Sort  (cost=4886.98..4893.15 rows=2468 width=45) (actual time=370.168..370.171 rows=22 loops=2)
               Sort Key: i.created_at DESC, i.id DESC
               Sort Method: top-N heapsort  Memory: 28kB
               Worker 0:  Sort Method: top-N heapsort  Memory: 28kB
               ->  Parallel Hash Join  (cost=2499.29..4814.09 rows=2468 width=45) (actual time=189.227..369.472 rows=2106 loops=2)
                     Hash Cond: (i.id = ic.item_id)
                     ->  Parallel Seq Scan on items i  (cost=0.00..2165.41 rows=35966 width=45) (actual time=0.191..175.322 rows=30532 loops=2)
                           Filter: ((created_at > '2021-10-01 00:00:00'::timestamp without time zone) OR ((created_at = '2022-01-01 00:00:00'::timestamp without time zone) AND (id < 'test'::text)))
                           Rows Removed by Filter: 19468
                     ->  Parallel Hash  (cost=2448.82..2448.82 rows=4037 width=37) (actual time=188.714..188.715 rows=3456 loops=2)
                           Buckets: 8192  Batches: 1  Memory Usage: 576kB
                           ->  Parallel Seq Scan on item_categories ic  (cost=0.00..2448.82 rows=4037 width=37) (actual time=1.034..187.452 rows=3456 loops=2)
                                 Filter: (category_id = ANY ('{category-1,category-2,category-3}'::text[]))
                                 Rows Removed by Filter: 46544
 Planning Time: 1.741 ms
 Execution Time: 381.075 ms
(20 rows)
```

## Example1

```sql
select i.id, i.created_at from items i join item_categories ic on i.id = ic.item_id WHERE ic.category_id in ('category-1', 'category-2', 'category-3') and (i.created_at > '2021-10-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) order by i.created_at desc, i.id desc limit 30
```

### 0. Baseline

```sql
docker exec -i postgres psql -U postgres test_db -c "explain analyze select i.id, i.created_at from items i join item_categories ic on i.id = ic.item_id WHERE ic.category_id in ('category-1', 'category-2', 'category-3') and (i.created_at > '2021-10-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) order by i.created_at desc, i.id desc limit 30"

                                                                                              QUERY PLAN
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=5886.99..5890.44 rows=30 width=45) (actual time=378.801..380.977 rows=30 loops=1)
   ->  Gather Merge  (cost=5886.99..6170.81 rows=2468 width=45) (actual time=378.800..380.973 rows=30 loops=1)
         Workers Planned: 1
         Workers Launched: 1
         ->  Sort  (cost=4886.98..4893.15 rows=2468 width=45) (actual time=370.168..370.171 rows=22 loops=2)
               Sort Key: i.created_at DESC, i.id DESC
               Sort Method: top-N heapsort  Memory: 28kB
               Worker 0:  Sort Method: top-N heapsort  Memory: 28kB
               ->  Parallel Hash Join  (cost=2499.29..4814.09 rows=2468 width=45) (actual time=189.227..369.472 rows=2106 loops=2)
                     Hash Cond: (i.id = ic.item_id)
                     ->  Parallel Seq Scan on items i  (cost=0.00..2165.41 rows=35966 width=45) (actual time=0.191..175.322 rows=30532 loops=2)
                           Filter: ((created_at > '2021-10-01 00:00:00'::timestamp without time zone) OR ((created_at = '2022-01-01 00:00:00'::timestamp without time zone) AND (id < 'test'::text)))
                           Rows Removed by Filter: 19468
                     ->  Parallel Hash  (cost=2448.82..2448.82 rows=4037 width=37) (actual time=188.714..188.715 rows=3456 loops=2)
                           Buckets: 8192  Batches: 1  Memory Usage: 576kB
                           ->  Parallel Seq Scan on item_categories ic  (cost=0.00..2448.82 rows=4037 width=37) (actual time=1.034..187.452 rows=3456 loops=2)
                                 Filter: (category_id = ANY ('{category-1,category-2,category-3}'::text[]))
                                 Rows Removed by Filter: 46544
 Planning Time: 1.741 ms
 Execution Time: 381.075 ms
(20 rows)
```

### 1. Reduce seq scan + rows removed by filter (381ms → 43 ms)

Add index on `item_categories`

```
docker exec -i postgres psql -U postgres test_db -c "CREATE INDEX IF NOT EXISTS item_categories_cateogory_id_item_id_idx ON item_categories (category_id, item_id);"
```

```sql
docker exec -i postgres psql -U postgres test_db -c "explain analyze select i.id, i.created_at from items i join item_categories ic on i.id = ic.item_id WHERE ic.category_id in ('category-1', 'category-2', 'category-3') and (i.created_at > '2021-10-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) order by i.created_at desc, i.id desc limit 30"
                                                                                            QUERY PLAN
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=3732.32..3732.40 rows=30 width=45) (actual time=43.179..43.184 rows=30 loops=1)
   ->  Sort  (cost=3732.32..3742.81 rows=4196 width=45) (actual time=43.178..43.181 rows=30 loops=1)
         Sort Key: i.created_at DESC, i.id DESC
         Sort Method: top-N heapsort  Memory: 28kB
         ->  Hash Join  (cost=451.15..3608.40 rows=4196 width=45) (actual time=2.037..42.643 rows=4213 loops=1)
               Hash Cond: (i.id = ic.item_id)
               ->  Seq Scan on items i  (cost=0.00..2886.00 rows=61143 width=45) (actual time=0.012..32.996 rows=61065 loops=1)
                     Filter: ((created_at > '2021-10-01 00:00:00'::timestamp without time zone) OR ((created_at = '2022-01-01 00:00:00'::timestamp without time zone) AND (id < 'test'::text)))
                     Rows Removed by Filter: 38935
               ->  Hash  (cost=365.36..365.36 rows=6863 width=37) (actual time=2.010..2.011 rows=6913 loops=1)
                     Buckets: 8192  Batches: 1  Memory Usage: 530kB
                     ->  Index Only Scan using item_categories_cateogory_id_item_id_idx on item_categories ic  (cost=0.42..365.36 rows=6863 width=37) (actual time=0.054..1.280 rows=6913 loops=1)
                           Index Cond: (category_id = ANY ('{category-1,category-2,category-3}'::text[]))
                           Heap Fetches: 0
 Planning Time: 1.573 ms
 Execution Time: 43.247 ms
(16 rows)
```

1. Performance improvement: **381ms → 43 ms**

1. Before and After:

    ```sql
    ->  Parallel Seq Scan on item_categories ic  (cost=0.00..2448.82 rows=4037 width=37) (actual time=1.034..187.452 rows=3456 loops=2)
          Filter: (category_id = ANY ('{category-1,category-2,category-3}'::text[]))
          Rows Removed by Filter: 46544
    ```

    ```sql
    ->  Index Only Scan using item_categories_cateogory_id_item_id_idx on item_categories ic  (cost=0.42..365.36 rows=6863 width=37) (actual time=0.054..1.280 rows=6913 loops=1)
          Index Cond: (category_id = ANY ('{category-1,category-2,category-3}'::text[]))
          Heap Fetches: 0
    ```

### 2. Reduce seq scan + rows removed by filter (43 ms → 5ms)

Create index on `items`

```
docker exec -i postgres psql -U postgres test_db -c "CREATE INDEX IF NOT EXISTS items_created_at ON items(created_at);"
```

```sql
docker exec -i postgres psql -U postgres test_db -c "explain analyze select i.id, i.created_at from items i join item_categories ic on i.id = ic.item_id WHERE ic.category_id in ('category-1', 'category-2', 'category-3') and (i.created_at > '2021-10-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) order by i.created_at desc, i.id desc limit 30"
                                                                                           QUERY PLAN
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=22.44..675.08 rows=30 width=45) (actual time=5.170..5.173 rows=30 loops=1)
   ->  Incremental Sort  (cost=22.44..91305.80 rows=4196 width=45) (actual time=5.169..5.171 rows=30 loops=1)
         Sort Key: i.created_at DESC, i.id DESC
         Presorted Key: i.created_at
         Full-sort Groups: 1  Sort Method: quicksort  Average Memory: 27kB  Peak Memory: 27kB
         ->  Nested Loop  (cost=0.71..91116.98 rows=4196 width=45) (actual time=0.874..5.139 rows=31 loops=1)
               ->  Index Scan Backward using items_created_at on items i  (cost=0.29..7898.22 rows=61143 width=45) (actual time=0.057..0.941 rows=429 loops=1)
                     Filter: ((created_at > '2021-10-01 00:00:00'::timestamp without time zone) OR ((created_at = '2022-01-01 00:00:00'::timestamp without time zone) AND (id < 'test'::text)))
               ->  Index Only Scan using item_categories_cateogory_id_item_id_idx on item_categories ic  (cost=0.42..1.35 rows=1 width=37) (actual time=0.009..0.009 rows=0 loops=429)
                     Index Cond: ((category_id = ANY ('{category-1,category-2,category-3}'::text[])) AND (item_id = i.id))
                     Heap Fetches: 0
 Planning Time: 1.092 ms
 Execution Time: 5.215 ms
(13 rows)
```

1. Performance improvement: **43 ms → 5ms**
1. Before and After:

    ```sql
    ->  Seq Scan on items i  (cost=0.00..2886.00 rows=61143 width=45) (actual time=0.012..32.996 rows=61065 loops=1)
          Filter: ((created_at > '2021-10-01 00:00:00'::timestamp without time zone) OR ((created_at = '2022-01-01 00:00:00'::timestamp without time zone) AND (id < 'test'::text)))
          Rows Removed by Filter: 38935
    ```

    ```sql
    ->  Index Scan Backward using items_created_at on items i  (cost=0.29..7898.22 rows=61143 width=45) (actual time=0.057..0.941 rows=429 loops=1)
          Filter: ((created_at > '2021-10-01 00:00:00'::timestamp without time zone) OR ((created_at = '2022-01-01 00:00:00'::timestamp without time zone) AND (id < 'test'::text)))
    ```

## Example2

1. `i.status in (1, 2)` is added
<!-- 1. `category_id not in ()` -->

```sql
select i.id, i.created_at from items i join item_categories ic on i.id = ic.item_id WHERE i.status in (1, 2) AND ic.category_id in ('category-1', 'category-2', 'category-3') and (i.created_at > '2021-10-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) order by i.created_at desc, i.id desc limit 30
```

### 0. Baseline

```sql
docker exec -i postgres psql -U postgres test_db -c "explain analyze select i.id, i.created_at from items i join item_categories ic on i.id = ic.item_id WHERE i.status in (1, 2) AND ic.category_id in ('category-1', 'category-2', 'category-3') and (i.created_at > '2021-10-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) order by i.created_at desc, i.id desc limit 30"
                                                                                                                QUERY PLAN
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=23.88..719.91 rows=30 width=45) (actual time=5.697..5.700 rows=30 loops=1)
   ->  Incremental Sort  (cost=23.88..65056.27 rows=2803 width=45) (actual time=5.696..5.697 rows=30 loops=1)
         Sort Key: i.created_at DESC, i.id DESC
         Presorted Key: i.created_at
         Full-sort Groups: 1  Sort Method: quicksort  Average Memory: 27kB  Peak Memory: 27kB
         ->  Nested Loop  (cost=0.71..64930.14 rows=2803 width=45) (actual time=1.194..5.671 rows=31 loops=1)
               ->  Index Scan Backward using items_created_at on items i  (cost=0.29..8148.22 rows=40846 width=45) (actual time=0.032..1.064 rows=497 loops=1)
                     Filter: ((status = ANY ('{1,2}'::integer[])) AND ((created_at > '2021-10-01 00:00:00'::timestamp without time zone) OR ((created_at = '2022-01-01 00:00:00'::timestamp without time zone) AND (id < 'test'::text))))
                     Rows Removed by Filter: 251
               ->  Index Only Scan using item_categories_cateogory_id_item_id_idx on item_categories ic  (cost=0.42..1.38 rows=1 width=37) (actual time=0.008..0.009 rows=0 loops=497)
                     Index Cond: ((category_id = ANY ('{category-1,category-2,category-3}'::text[])) AND (item_id = i.id))
                     Heap Fetches: 0
 Planning Time: 0.514 ms
 Execution Time: 5.721 ms
(14 rows)
```

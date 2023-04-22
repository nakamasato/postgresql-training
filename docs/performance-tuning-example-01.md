## Example1: join on `items.id` and filter by `category_id` and `created_at` (i=100000,c=100)

```sql
SELECT i.id, i.created_at
FROM items i
JOIN item_categories ic
ON i.id = ic.item_id
WHERE ic.category_id IN ('category-1', 'category-2', 'category-3')
AND (i.created_at > '2021-10-01'
OR (i.created_at = '2022-01-01' AND i.id < 'test'))
ORDER BY i.created_at DESC, i.id DESC
LIMIT 30
```

### 0. Baseline (381ms)


```sql
docker exec -i postgres psql -U postgres test_db -c "EXPLAIN ANALYZE SELECT i.id, i.created_at FROM items i JOIN item_categories ic ON i.id = ic.item_id WHERE ic.category_id IN ('category-1', 'category-2', 'category-3') AND (i.created_at > '2021-10-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) ORDER BY i.created_at DESC, i.id DESC LIMIT 30"

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
docker exec -i postgres psql -U postgres test_db -c "EXPLAIN ANALYZE SELECT i.id, i.created_at FROM items i JOIN item_categories ic ON i.id = ic.item_id WHERE ic.category_id IN ('category-1', 'category-2', 'category-3') AND (i.created_at > '2021-10-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) ORDER BY i.created_at DESC, i.id DESC LIMIT 30"
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
docker exec -i postgres psql -U postgres test_db -c "EXPLAIN ANALYZE SELECT i.id, i.created_at FROM items i JOIN item_categories ic ON i.id = ic.item_id WHERE ic.category_id IN ('category-1', 'category-2', 'category-3') AND (i.created_at > '2021-10-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) ORDER BY i.created_at DESC, i.id DESC LIMIT 30"
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

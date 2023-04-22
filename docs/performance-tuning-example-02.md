
## Example2: join on `items.id` and filter by `status`, `category_id` and `created_at` (i=10000000,c=100)

`i.status in (1)` is added to the query above:

```sql
SELECT i.id, i.created_at
FROM items i
JOIN item_categories ic
ON i.id = ic.item_id
WHERE i.status IN (1)
AND ic.category_id IN ('category-1', 'category-2', 'category-3')
AND (i.created_at < '2022-01-01' OR (i.created_at = '2022-01-01' AND i.id < 'test'))
ORDER BY i.created_at DESC, i.id DESC
LIMIT 30
```

### 0. Baseline (24s)

```sql
docker exec -i postgres psql -U postgres test_db -c "EXPLAIN ANALYZE SELECT i.id, i.created_at FROM items i join item_categories ic ON i.id = ic.item_id WHERE i.status in (1) AND ic.category_id IN ('category-1', 'category-2', 'category-3') AND (i.created_at < '2022-01-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) ORDER BY i.created_at DESC, i.id DESC LIMIT 30"
                                                                                                    QUERY PLAN
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=37.54..1134.78 rows=30 width=45) (actual time=24527.139..24527.148 rows=30 loops=1)
   ->  Incremental Sort  (cost=37.54..4368770.52 rows=119446 width=45) (actual time=24527.138..24527.141 rows=30 loops=1)
         Sort Key: i.created_at DESC, i.id DESC
         Presorted Key: i.created_at
         Full-sort Groups: 1  Sort Method: quicksort  Average Memory: 27kB  Peak Memory: 27kB
         ->  Nested Loop  (cost=1.00..4363395.45 rows=119446 width=45) (actual time=24501.843..24527.052 rows=31 loops=1)
               ->  Index Scan Backward using items_created_at on items i  (cost=0.43..846283.83 rows=1762594 width=45) (actual time=24501.268..24507.501 rows=362 loops=1)
                     Filter: ((status = 1) AND ((created_at < '2022-01-01 00:00:00'::timestamp without time zone) OR ((created_at = '2022-01-01 00:00:00'::timestamp without time zone) AND (id < 'test'::text))))
                     Rows Removed by Filter: 4675811
               ->  Index Only Scan using item_categories_cateogory_id_item_id_idx on item_categories ic  (cost=0.56..1.99 rows=1 width=37) (actual time=0.051..0.052 rows=0 loops=362)
                     Index Cond: ((category_id = ANY ('{category-1,category-2,category-3}'::text[])) AND (item_id = i.id))
                     Heap Fetches: 0
 Planning Time: 6.728 ms
 Execution Time: 24527.310 ms
(14 rows)
```

### 1. Create an index on `items(status, created_at)` (24s → 7s)

Create a new index:
```
docker exec -i postgres psql -U postgres test_db -c "CREATE INDEX IF NOT EXISTS items_status_created_at_idx ON items(status, created_at);"
```

<details><summary>drop index</summary>

If you want to drop the index for comparison:

```
docker exec -i postgres psql -U postgres test_db -c "drop INDEX IF EXISTS items_status_created_at_idx;"
```

</details>

Run the query:
```sql
docker exec -i postgres psql -U postgres test_db -c "EXPLAIN ANALYZE SELECT i.id, i.created_at FROM items i JOIN item_categories ic ON i.id = ic.item_id WHERE i.status in (1) AND ic.category_id IN ('category-1', 'category-2', 'category-3') AND (i.created_at < '2022-01-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) ORDER BY i.created_at DESC, i.id DESC LIMIT 30"
docker exec -i postgres psql -U postgres test_db -c "EXPLAIN ANALYZE SELECT i.id, i.created_at FROM items i JOIN item_categories ic ON i.id = ic.item_id WHERE i.status in (1) AND ic.category_id in ('category-1', 'category-2', 'category-3') and (i.created_at < '2022-01-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) ORDER BY i.created_at DESC, i.id DESC LIMIT 30"

                                                                                           QUERY PLAN
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=35.16..1061.27 rows=30 width=45) (actual time=7470.450..7470.455 rows=30 loops=1)
   ->  Incremental Sort  (cost=35.16..4085502.22 rows=119446 width=45) (actual time=7470.449..7470.451 rows=30 loops=1)
         Sort Key: i.created_at DESC, i.id DESC
         Presorted Key: i.created_at
         Full-sort Groups: 1  Sort Method: quicksort  Average Memory: 27kB  Peak Memory: 27kB
         ->  Nested Loop  (cost=1.00..4080127.15 rows=119446 width=45) (actual time=7449.225..7470.379 rows=31 loops=1)
               ->  Index Scan Backward using items_status_created_at_idx on items i  (cost=0.43..563015.53 rows=1762594 width=45) (actual time=7445.111..7447.027 rows=362 loops=1)
                     Index Cond: (status = 1)
                     Filter: ((created_at < '2022-01-01 00:00:00'::timestamp without time zone) OR ((created_at = '2022-01-01 00:00:00'::timestamp without time zone) AND (id < 'test'::text)))
                     Rows Removed by Filter: 1559539
               ->  Index Only Scan using item_categories_cateogory_id_item_id_idx on item_categories ic  (cost=0.56..1.99 rows=1 width=37) (actual time=0.062..0.063 rows=0 loops=362)
                     Index Cond: ((category_id = ANY ('{category-1,category-2,category-3}'::text[])) AND (item_id = i.id))
                     Heap Fetches: 0
 Planning Time: 3.098 ms
 Execution Time: 7470.549 ms
(15 rows)
```

The new index `items_status_created_at_idx` is used.

### 2. `(i.created_at < '2022-01-01' OR (i.created_at = '2022-01-01' AND i.id < 'test'))` row-wise comparison (8s → 46ms)

Interestingly, `(i.created_at < '2022-01-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') )` is the part that makes the query slow.

```sql
->  Index Scan Backward using items_status_created_at_idx on items i  (cost=0.43..563015.53 rows=1762594 width=45) (actual time=7445.111..7447.027 rows=362 loops=1)
      Index Cond: (status = 1)
      Filter: ((created_at < '2022-01-01 00:00:00'::timestamp without time zone) OR ((created_at = '2022-01-01 00:00:00'::timestamp without time zone) AND (id < 'test'::text)))
      Rows Removed by Filter: 1559539
```

The index condition: `status = 1`
Filter: `created_at` and `id`
Rows Removed by Filter: `1559539`

`Where`:
1. **Access Predicate** (`Index Cond`): The access predicates express the start and stop conditions of the leaf node traversal.
1. **Index Filter Predicate** (`Index Cond`): Index filter predicates are applied during the leaf node traversal only. They do not contribute to the start and stop conditions and do not narrow the scanned range.
1. **Table level filter predicate** (`Filter`): Predicates on columns that are not part of the index are evaluated on the table level. We saw this in the above example.


You can see the result with the query without either of the before or after `OR` ([ref](https://dba.stackexchange.com/questions/241591/postgres-choosing-a-filter-instead-of-index-cond-when-or-is-involved)):

Only `i.created_at < '2022-01-01'`: `53ms`
Only `(i.created_at < '2022-01-01' )`: `53ms`

<details>

```sql
docker exec -i postgres psql -U postgres test_db -c "EXPLAIN ANALYZE SELECT i.id, i.created_at FROM items i join item_categories ic ON i.id = ic.item_id WHERE i.status in (1) AND ic.category_id IN ('category-1', 'category-2', 'category-3') AND i.created_at < '2022-01-01' ORDER BY i.created_at DESC, i.id DESC LIMIT 30"
                                                                                      QUERY PLAN
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=34.56..1042.56 rows=30 width=45) (actual time=35.202..35.207 rows=30 loops=1)
   ->  Incremental Sort  (cost=34.56..4013407.91 rows=119446 width=45) (actual time=35.201..35.203 rows=30 loops=1)
         Sort Key: i.created_at DESC, i.id DESC
         Presorted Key: i.created_at
         Full-sort Groups: 1  Sort Method: quicksort  Average Memory: 27kB  Peak Memory: 27kB
         ->  Nested Loop  (cost=1.00..4008032.84 rows=119446 width=45) (actual time=0.445..35.054 rows=31 loops=1)
               ->  Index Scan Backward using items_status_created_at_idx on items i  (cost=0.43..490921.22 rows=1762594 width=45) (actual time=0.196..8.728 rows=362 loops=1)
                     Index Cond: ((status = 1) AND (created_at < '2022-01-01 00:00:00'::timestamp without time zone))
               ->  Index Only Scan using item_categories_cateogory_id_item_id_idx on item_categories ic  (cost=0.56..1.99 rows=1 width=37) (actual time=0.069..0.071 rows=0 loops=362)
                     Index Cond: ((category_id = ANY ('{category-1,category-2,category-3}'::text[])) AND (item_id = i.id))
                     Heap Fetches: 0
 Planning Time: 5.499 ms
 Execution Time: 35.360 ms
(13 rows)
```

</details>

Only `i.created_at = '2022-01-01' AND i.id < 'test'`: 0.21ms

<details>

```sql
docker exec -i postgres psql -U postgres test_db -c "EXPLAIN ANALYZE SELECT i.id, i.created_at FROM items i join item_categories ic ON i.id = ic.item_id WHERE i.status in (1) AND ic.category_id IN ('category-1', 'category-2', 'category-3') AND i.created_at = '2022-01-01' AND i.id < 'test' ORDER BY i.created_at DESC, i.id DESC LIMIT 30"
                                                                         QUERY PLAN
-------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=22.20..22.20 rows=1 width=45) (actual time=0.150..0.150 rows=0 loops=1)
   ->  Sort  (cost=22.20..22.20 rows=1 width=45) (actual time=0.149..0.149 rows=0 loops=1)
         Sort Key: i.id DESC
         Sort Method: quicksort  Memory: 25kB
         ->  Nested Loop  (cost=1.00..22.19 rows=1 width=45) (actual time=0.116..0.117 rows=0 loops=1)
               ->  Index Scan using items_status_created_at_idx on items i  (cost=0.43..8.46 rows=1 width=45) (actual time=0.116..0.116 rows=0 loops=1)
                     Index Cond: ((status = 1) AND (created_at = '2022-01-01 00:00:00'::timestamp without time zone))
                     Filter: (id < 'test'::text)
               ->  Index Only Scan using item_categories_cateogory_id_item_id_idx on item_categories ic  (cost=0.56..13.72 rows=1 width=37) (never executed)
                     Index Cond: ((category_id = ANY ('{category-1,category-2,category-3}'::text[])) AND (item_id = i.id))
                     Heap Fetches: 0
 Planning Time: 2.430 ms
 Execution Time: 0.219 ms
(13 rows)
```

</details>

You can improve the query `(i.created_at < '2022-01-01' OR (i.created_at = '2022-01-01' AND i.id < 'test'))` to `(i.created_at, id) < ('2022-01-01', 'test')`

```sql
docker exec -i postgres psql -U postgres test_db -c "EXPLAIN ANALYZE SELECT i.id, i.created_at FROM items i JOIN item_categories ic ON i.id = ic.item_id WHERE i.status IN (1) AND ic.category_id IN ('category-1', 'category-2', 'category-3') AND (i.created_at, i.id) < ('2022-01-01', 'test') ORDER BY i.created_at DESC, i.id DESC LIMIT 30"
```

```sql
docker exec -i postgres psql -U postgres test_db -c "EXPLAIN ANALYZE SELECT i.id, i.created_at FROM items i JOIN item_categories ic ON i.id = ic.item_id WHERE i.status IN (1) AND ic.category_id IN ('category-1', 'category-2', 'category-3') AND (i.created_at, i.id) < ('2022-01-01', 'test') ORDER BY i.created_at DESC, i.id DESC LIMIT 30"
                                                                                      QUERY PLAN
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=34.63..1044.84 rows=30 width=45) (actual time=41.025..41.030 rows=30 loops=1)
   ->  Incremental Sort  (cost=34.63..4022220.90 rows=119446 width=45) (actual time=41.023..41.026 rows=30 loops=1)
         Sort Key: i.created_at DESC, i.id DESC
         Presorted Key: i.created_at
         Full-sort Groups: 1  Sort Method: quicksort  Average Memory: 27kB  Peak Memory: 27kB
         ->  Nested Loop  (cost=1.00..4016845.83 rows=119446 width=45) (actual time=0.308..40.879 rows=31 loops=1)
               ->  Index Scan Backward using items_status_created_at_idx on items i  (cost=0.43..499734.21 rows=1762594 width=45) (actual time=0.103..9.723 rows=362 loops=1)
                     Index Cond: ((status = 1) AND (created_at <= '2022-01-01 00:00:00'::timestamp without time zone))
                     Filter: (ROW(created_at, id) < ROW('2022-01-01 00:00:00'::timestamp without time zone, 'test'::text))
               ->  Index Only Scan using item_categories_cateogory_id_item_id_idx on item_categories ic  (cost=0.56..1.99 rows=1 width=37) (actual time=0.083..0.084 rows=0 loops=362)
                     Index Cond: ((category_id = ANY ('{category-1,category-2,category-3}'::text[])) AND (item_id = i.id))
                     Heap Fetches: 0
 Planning Time: 2.808 ms
 Execution Time: 41.172 ms
(14 rows)
```

[`ROW(a,b) < ROW(c,d)` = `a < c OR (a = c AND b < d)`](https://www.postgresql.org/docs/current/functions-comparisons.html#ROW-WISE-COMPARISON)

In our case:
1. a = created_at
1. b = id
1. c = '2021-10-01'
1. d = 'test'

```sql
(i.created_at, id) < ('2022-01-01', 'test')
```

is equivalent to

```sql
i.created_at < '2022-01-01' OR (i.created_at = '2022-01-01' AND id < 'test')
```

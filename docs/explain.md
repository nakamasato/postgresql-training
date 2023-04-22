## Explain

### i=10000,c=20

`EXPLAIN`:

```sql
docker exec -i postgres psql -U postgres test_db -c "EXPLAIN SELECT i.id, i.created_at FROM items i JOIN item_categories ic ON i.id = ic.item_id WHERE ic.category_id IN ('category-1', 'category-2', 'category-3') and (i.created_at > '2021-10-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) ORDER BY i.created_at DESC, i.id DESC LIMIT 30"
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
docker exec -i postgres psql -U postgres test_db -c "EXPLAIN ANALYZE SELECT i.id, i.created_at FROM items i JOIN item_categories ic ON i.id = ic.item_id WHERE ic.category_id IN ('category-1', 'category-2', 'category-3') AND (i.created_at > '2021-10-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) ORDER BY i.created_at DESC, i.id DESC LIMIT 30"
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
docker exec -i postgres psql -U postgres test_db -c "EXPLAIN SELECT i.id, i.created_at FROM items i JOIN item_categories ic ON i.id = ic.item_id WHERE ic.category_id IN ('category-1', 'category-2', 'category-3') and (i.created_at > '2021-10-01' OR (i.created_at = '2022-01-01' AND i.id < 'test') ) ORDER BY i.created_at DESC, i.id DESC LIMIT 30"
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

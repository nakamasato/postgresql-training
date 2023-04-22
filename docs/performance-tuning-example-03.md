## Example 3: Get items in the status 1 and created before 2022-01-01

```sql
SELECT i.id, i.created_at, ic.category_id
FROM items i
JOIN item_categories ic ON i.id = ic.item_id
WHERE i.status IN (1)
AND i.created_at < '2022-01-01'
ORDER BY i.created_at DESC, i.id DESC
LIMIT 30
```

### Original query seq scan 5s


```sql
docker exec -i postgres psql -U postgres test_db -c "EXPLAIN ANALYZE SELECT i.id, i.created_at, ic.category_id FROM items i JOIN item_categories ic ON i.id = ic.item_id AND i.status in (1) AND i.created_at < '2021-05-01' ORDER BY i.created_at DESC, i.id DESC LIMIT 30"
                                                                                     QUERY PLAN
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=467652.66..467656.16 rows=30 width=45) (actual time=4109.457..4374.930 rows=30 loops=1)
   ->  Gather Merge  (cost=467652.66..517845.70 rows=430196 width=45) (actual time=4095.844..4361.310 rows=30 loops=1)
         Workers Planned: 2
         Workers Launched: 2
         ->  Sort  (cost=466652.64..467190.38 rows=215098 width=45) (actual time=4034.965..4036.371 rows=24 loops=3)
               Sort Key: i.created_at DESC, i.id DESC
               Sort Method: top-N heapsort  Memory: 28kB
               Worker 0:  Sort Method: top-N heapsort  Memory: 28kB
               Worker 1:  Sort Method: top-N heapsort  Memory: 29kB
               ->  Parallel Hash Join  (cost=176763.48..460299.83 rows=215098 width=45) (actual time=3561.582..4008.396 rows=172105 loops=3)
                     Hash Cond: (ic.item_id = i.id)
                     ->  Parallel Seq Scan on item_categories ic  (cost=0.00..205601.81 rows=4166681 width=37) (actual time=0.196..1032.482 rows=3333333 loops=3)
                     ->  Parallel Hash  (cost=172183.76..172183.76 rows=215098 width=45) (actual time=1285.225..1285.229 rows=172105 loops=3)
                           Buckets: 65536  Batches: 16  Memory Usage: 3072kB
                           ->  Parallel Bitmap Heap Scan on items i  (cost=13139.83..172183.76 rows=215098 width=45) (actual time=250.811..1175.537 rows=172105 loops=3)
                                 Recheck Cond: ((status = 1) AND (created_at < '2021-05-01 00:00:00'::timestamp without time zone))
                                 Rows Removed by Index Recheck: 1830710
                                 Heap Blocks: exact=15258 lossy=22113
                                 ->  Bitmap Index Scan on items_status_created_at_idx  (cost=0.00..13010.77 rows=516234 width=0) (actual time=287.963..287.967 rows=516314 loops=1)
                                       Index Cond: ((status = 1) AND (created_at < '2021-05-01 00:00:00'::timestamp without time zone))
 Planning Time: 3.060 ms
 JIT:
   Functions: 37
   Options: Inlining false, Optimization false, Expressions true, Deforming true
   Timing: Generation 8.113 ms, Inlining 0.000 ms, Optimization 8.262 ms, Emission 30.223 ms, Total 46.598 ms
 Execution Time: 4432.604 ms
(26 rows)
```

-> You can find `Seq Scan` on `item_categories`

```sql
->  Parallel Seq Scan on item_categories ic  (cost=0.00..205601.81 rows=4166681 width=37) (actual time=0.196..1032.482 rows=3333333 loops=3)
```

Solution is obvious: Add an index to `item_categories` on `item_id`:

```
docker exec -i postgres psql -U postgres test_db -c "CREATE INDEX IF NOT EXISTS items_categories_item_id_idx ON item_categories(item_id);"
CREATE INDEX
```

```sql
docker exec -i postgres psql -U postgres test_db -c "EXPLAIN ANALYZE SELECT i.id, i.created_at, ic.category_id FROM items i JOIN item_categories ic ON i.id = ic.item_id AND i.status in (1) AND i.created_at < '2021-05-01' ORDER BY i.created_at DESC, i.id DESC LIMIT 30"
                                                                                 QUERY PLAN
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=4.31..104.07 rows=30 width=56) (actual time=6.659..6.663 rows=30 loops=1)
   ->  Incremental Sort  (cost=4.31..1716708.13 rows=516234 width=56) (actual time=6.659..6.660 rows=30 loops=1)
         Sort Key: i.created_at DESC, i.id DESC
         Presorted Key: i.created_at
         Full-sort Groups: 1  Sort Method: quicksort  Average Memory: 29kB  Peak Memory: 29kB
         ->  Nested Loop  (cost=1.00..1693592.99 rows=516234 width=56) (actual time=0.463..6.500 rows=31 loops=1)
               ->  Index Scan Backward using items_status_created_at_idx on items i  (cost=0.43..446217.52 rows=516234 width=45) (actual time=0.326..1.891 rows=31 loops=1)
                     Index Cond: ((status = 1) AND (created_at < '2021-05-01 00:00:00'::timestamp without time zone))
               ->  Index Scan using items_categories_item_id_idx on item_categories ic  (cost=0.56..2.41 rows=1 width=48) (actual time=0.147..0.147 rows=1 loops=31)
                     Index Cond: (item_id = i.id)
 Planning Time: 2.074 ms
 Execution Time: 6.778 ms
(12 rows)
```


Plan result on different conditions:

<details>

```
for y in 2021 2022; do for m in 01 02 03 04 05 06 07 08 09 10 11 12; do date=$y-$m-01; echo $date; docker exec -i postgres psql -U postgres test_db -c "EXPLAIN (ANALYZE true, COSTS true, FORMAT JSON) SELECT i.id, i.created_at, ic.category_id FROM items i JOIN item_categories ic ON i.id = ic.item_id AND i.status in (1) AND i.created_at < '$date' ORDER BY i.created_at DESC, i.id DESC LIMIT 30" | grep -v -E '(PLAN|row|---)' | sed 's/+//g' | jq | python analyze_explain.py ; done; done
2021-01-01
['Limit', 'Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 0.876
2021-02-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 8.713
2021-03-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 3.729
2021-04-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 3.158
2021-05-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 1.618
2021-06-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 1.492
2021-07-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 4.142
2021-08-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 3.977
2021-09-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 4.669
2021-10-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 4.301
2021-11-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 4.869
2021-12-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 3.708
2022-01-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 3.64
2022-02-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 3.392
2022-03-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 4.916
2022-04-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 4.048
2022-05-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 4.125
2022-06-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 4.278
2022-07-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 3.242
2022-08-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 3.117
2022-09-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 3.436
2022-10-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 3.185
2022-11-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 3.894
2022-12-01
['Limit', 'Incremental Sort', 'Nested Loop', 'Index Scan', 'Index Only Scan'] 1.2
```

</details>

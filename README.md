# Postgres Training

## Contents

1. [Prepara Data](docs/prepare-data.md)
1. [EXPLAIN](docs/explain.md)
1. [Example 01: Reduce seq scan + rows removed by filter by adding index](docs/performance-tuning-example-01.md)
1. [Example 02: Multicolumn index + row-wise comparison](docs/performance-tuning-example-02.md)
1. [Example 03: Reduce seq scan by adding index](docs/performance-tuning-example-03.md)

# References
1. [Distinguishing Access and Filter-Predicates](https://use-the-index-luke.com/sql/explain-plan/postgresql/filter-predicates)
1. [Postgres choosing a filter instead of index cond when OR is involved](https://dba.stackexchange.com/questions/241591/postgres-choosing-a-filter-instead-of-index-cond-when-or-is-involved)
1. [Row-wise comparison](https://www.postgresql.org/docs/current/functions-comparisons.html#ROW-WISE-COMPARISON)

# SWDB Query Explorer

A minimal Flask + Tabulator web app for running **read-only** SQL queries against the `swdb` PostgreSQL database and visualising the results in a responsive table.

## Prerequisites

- Python 3.9+
- Access to the PostgreSQL instance described in `.github/instructions/postgressql_connection.md`

## Installation

Create and activate a virtual environment (recommended), then install dependencies:

```bash
pip install flask psycopg2-binary
```

## Running the app

From the `flask_app` folder:

```bash
python app.py
```

Then open your browser at:

```text
http://127.0.0.1:5000/
```

## Usage

1. Type or edit a **SELECT** query in the SQL box at the top of the page.
2. Click **Run query**.
3. The results will appear in the Tabulator table below.
   - Columns are resizable and movable.
   - The table supports horizontal scrolling to accommodate many columns.

> Note: Only `SELECT` queries are allowed for safety; other statement types will be rejected.

## Select one entry per site
### Drop temp tables:
```sql
-- drop tables if they exist
DROP TABLE IF EXISTS temp_victims_and_sites;
DROP TABLE IF EXISTS temp_victims_sites_accounts;
DROP TABLE IF EXISTS zoominfo_ransomware_bb_domains;
DROP TABLE IF EXISTS temp_unique_entries;
```

### create table for hacked sites using victims list merging on domain name:
```sql
create table temp_victims_and_sites as
SELECT s.account_id, s.site_id, s.site_url from usa_2022_sites as s
JOIN zoominfo_bb_domains v ON s.site_url = v.domain;
```

### join temp_victims_and_sites and accounts
```sql
create table temp_victims_sites_accounts as
SELECT tvs.account_id, tvs.site_id, tvs.site_url, a.account_name, a.account_employees
from temp_victims_and_sites as tvs
join usa_2022_accounts as a on tvs.account_id = a.account_id;
```

### select distinct sire_url from temp_victims_sites_accounts, if there is more than 1 entry with the same site_url select the one with most highies revenue
```sql
CREATE TABLE temp_unique_entries AS
SELECT DISTINCT ON (site_url) *
FROM temp_victims_sites_accounts
WHERE site_type IN ('UH', 'HQ')
ORDER BY 
    site_url,
    CASE site_type
        WHEN 'UH' THEN 1
        WHEN 'HQ' THEN 2
    END,
    account_revenue DESC;
```

### Sanity Check count: total rows, unique site_url, unique account_id, unique account_name. do it using 1 query.
```sql
SELECT COUNT(*) AS total_rows,
       COUNT(DISTINCT site_url) AS unique_site_urls,
       COUNT(DISTINCT account_id) AS unique_account_ids,
       COUNT(DISTINCT account_name) AS unique_account_names
FROM temp_unique_entries;
```

### BIG JOIN
- joining tables with temp_unique_entries as u:
- victims as v on u.site_url = v.website
- usa_2022_accounts as a on a.account_id = u.account_id
- usa_2022_technologies as t on t.site_id = u.site_id
- create table temp_main_table as

```sql
drop table if exists temp_main_table;
create table temp_main_table as
select
    zoom.domain as site_url,
    a.account_name,
    a.account_employees,
    a.account_hw_spending,
    a.account_ict_spending,
    a.account_sw_spending,
    a.account_it_services_spending,
    a.account_revenue_usd,
    v.group_name,
    v.published,
    t.product,
    t.product_vendor,
    lp.product_category
from zoominfo_bb_domains as zoom
left join temp_unique_entries as u
    on u.site_url = zoom.domain
left join victims as v
    on v.website = zoom.domain
left join usa_2022_accounts as a
    on a.account_id = u.account_id
left join usa_2022_sites_technology as t
    on t.site_id = u.site_id
left join usa_2022_technology_lookup as lp
    on lp.product_id = t.product_id;
```

### Final select from temp_main_table
```sql
SELECT account_name, site_url, account_employees, account_hw_spending, account_ict_spending,
       account_sw_spending, account_it_services_spending, account_revenue_usd, group_name, published,
       JSONB_AGG(DISTINCT JSONB_BUILD_OBJECT(
        'product', product,
        'vendor', product_vendor,
        'category', product_category
)) AS technologies,
       CASE WHEN group_name IS NULL THEN 0 ELSE 1 END AS hacked
FROM temp_main_table
GROUP BY account_name, site_url, account_employees, account_hw_spending, account_ict_spending,
       account_sw_spending, account_it_services_spending, account_revenue_usd, group_name, published;
100 rows returned.
```

## General Methodology for selecting one entry per site
First we filtering all the websites domain names in the swdb SITES table (we are using sites table because it has more website domains).
Due to imperfect SWDB structure, same domain name could be associated with multiple sites, to select one entry per site we are using the following logic:
1. If there is only one entry for a domain name, we select that one.
2. If there are multiple entries for a domain name, we select the one with the highest site_type (UH > HQ > LQ) and if there are multiple entries with the same site_type, we select the one with the highest account_revenue.

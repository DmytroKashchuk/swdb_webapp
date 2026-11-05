# C&C v5.2 (2025) — Relational Data Format (RDF) Schema

Source: `RDF_v5.2_for_2025_C&C_data.xlsx` (Spiceworks Ziff-Davis data dictionary).
6 tables, 146 fields. Table names and field names are used verbatim as SQL identifiers.

Conventions: `PK` = primary key, `FK` = foreign key, `CPK` = composite primary key. Field types are `Text(max_length)`, `Numeric`, `Array(max_length)` (pipe/comma separated list stored as text), `Date`. `Default` is the value stored when no data is available (`NULL` means missing).

## Tables overview

| Table | Type | Fields | Description |
|---|---|---|---|
| `COMPANY` | data | 58 | Domain-based companies, with firmographics. 1 company can regroup 1 or several sites from SITE table. |
| `COMPANY_TECH_SIZING` | data | 19 | Company technology sizing attributes. |
| `COMPANY_TECHNOLOGY` | data | 8 | Company technographics. There can be multiple technology records for a given company. |
| `TECHNOLOGY_LOOKUP` | lookup | 8 | Technographics catalogue. |
| `SITE` | data | 42 | Business locations, with firmographics. 1 site always reports to a Company within the COMPANY table. |
| `SITE_TECH_SIZING` | data | 11 | Site technology sizing attributes. |

## Relationships

- `COMPANY` → `COMPANY_TECHNOLOGY` (1:N): `COMPANY_TECHNOLOGY.COMPANY_ID` = `COMPANY.COMPANY_ID`
- `TECHNOLOGY_LOOKUP` → `COMPANY_TECHNOLOGY` (1:N): `COMPANY_TECHNOLOGY.TECH_ID` = `TECHNOLOGY_LOOKUP.TECH_ID`
- `COMPANY` → `SITE` (1:N): `SITE.COMPANY_ID` = `COMPANY.COMPANY_ID`
- `COMPANY` → `COMPANY_TECH_SIZING` (1:1): `COMPANY_TECH_SIZING.COMPANY_ID` = `COMPANY.COMPANY_ID`
- `SITE` → `SITE_TECH_SIZING` (1:1): `SITE_TECH_SIZING.SITE_ID` = `SITE.SITE_ID`

Typical joins: `COMPANY` is the root entity; `SITE` rows belong to a company via `COMPANY_ID`; `COMPANY_TECHNOLOGY` lists installed technologies per company and resolves to `TECHNOLOGY_LOOKUP` via `TECH_ID`; `*_TECH_SIZING` tables extend their parent 1:1 on the same primary key.

## Changes vs. CCID v5.1 (2024)

- Added `COMPANY.COMPANY_ID_IMMEDIATE_PARENT` — COMPANY_ID associated to the immediate parent company
- Added `COMPANY.COMPANY_HIERARCHY_LEVEL` — Hierarchical level within the company family tree. Ultimate Parent companies are 0, their children are 1, their grandchildren are 2, etc..
- Added `COMPANY.COMPANY_DELIVERABLE` — Indicates whether the record is an active company (1) or not (<>1)
- Added `COMPANY_TECHNOLOGY.TECH_CONFIDENCE_SCORE` — Likelihood that the technology/product is present at the company

## Table `COMPANY` (data, 58 fields)

Domain-based companies, with firmographics. 1 company can regroup 1 or several sites from SITE table.

| # | Field | Type | Key | Definition | Topic | Possible values | Default | Notes |
|---|---|---|---|---|---|---|---|---|
| 3 | `COMPANY_PRIMARY_DOMAIN` | Text(128) |  | Primary domain of the company | Company Identification |  | No default value |  |
| 4 | `COMPANY_WEBSITE` | Text(512) |  | Website of the company | Company Identification |  | COMPANY_PRIMARY_DOMAIN |  |
| 5 | `COMPANY_NAME` | Text(128) |  | Legal/registered name of the company | Company Identification |  | No default value |  |
| 9 | `COMPANY_STOCK_SYMBOL` | Text(16) |  | Stock ticker of the company | Company Identification |  | NULL |  |
| 10 | `COMPANY_DOMAINS` | Array(512) |  | All domains related to the company | Company Identification |  | COMPANY_PRIMARY_DOMAIN |  |
| 11 | `COMPANY_START_YEAR` | Text(4) |  | Founding year of the company | Company Identification |  | NULL | Format: YYYY |
| 13 | `COMPANY_EMPLOYEES` | Numeric |  | Number of company employees | Company Sizing |  | NULL (cannot be 0) |  |
| 15 | `COMPANY_ANNUAL_REVENUE` | Numeric |  | Company annual revenue (in USD) | Company Sizing |  | NULL (cannot be 0) |  |
| 23 | `COMPANY_PRIMARY_SIC4_DESCRIPTION` | Text(64) |  | Primary 4-digit SIC description of the company | Company Industry |  | NULL |  |
| 32 | `COMPANY_LOCATION_CITY` | Text(64) |  | City of the parent location of the company | Company Location Identification |  | NULL |  |
| 35 | `COMPANY_LOCATION_COUNTRY` | Text(64) |  | Country of the parent location of the company | Company Location Identification |  | NULL |  |
| 39 | `COMPANY_LOCATION_TYPE` | Text(3) |  | Company location type: BRA=Branch, SLS=Single-location subsidiary, SHQ=Subsidiary HQ, STA=Standalone, UHQ=Ultimate HQ | Company Location Identification | BRA / SLS / SHQ / STA / UHQ | NULL |  |
| 40 | `COMPANY_LOCATION_DOMESTIC_HQ` | Numeric |  | Indicates whether the parent location of the company is a domestic parent entity (1) or not (0) | Company Location Identification | 0 / 1 | NULL |  |
| 41 | `COMPANY_LOCATION_LEGAL_STATUS` | Text(16) |  | Legal structure of the parent location of the company | Company Location Identification |  | NULL |  |
| 43 | `COMPANY_LOCATION_COUNTRY_REGION_CODE` | Text(5) |  | Country region code of the parent location of the company | Company Location Geo | Ant / APac / EMEA / LatAm / NA | NULL |  |
| 54 | `COMPANY_TYPE` | Text(2) |  | Company Type (ST=Standalone, SU=Subsidiary, UP=Ultimate Parent) | Company Identification | ST / SU / UP | NULL |  |
| 55 | `COMPANY_PUBLIC` | Numeric |  | Indicates whether the company is public (1) or private (0) | Company Identification | 0 / 1 | NULL |  |

## Table `COMPANY_TECH_SIZING` (data, 19 fields)

Company technology sizing attributes.

| # | Field | Type | Key | Definition | Topic | Possible values | Default | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `COMPANY_ID` | Text(128) | PK → `COMPANY.COMPANY_ID` | Unique ID associated to the company | Company Identification |  | No default value |  |
| 2 | `COMPANY_IT_EMPLOYEES` | Numeric |  | Estimated number of company employees in the IT department | Company Tech Sizing |  | NULL |  |
| 3 | `COMPANY_IT_EMPLOYEE_RANGE` | Text(32) |  | Range of the estimated number of company employees in the IT department | Company Tech Sizing |  | NULL |  |
| 4 | `COMPANY_ANNUAL_ICT_SPENDING` | Numeric |  | Estimated company annual ICT spending (USD) | Company Tech Sizing |  | NULL |  |
| 5 | `COMPANY_ANNUAL_ICT_SPENDING_RANGE` | Text(64) |  | Range of the estimated company annual ICT spending (USD) | Company Tech Sizing |  | NULL |  |
| 6 | `COMPANY_ANNUAL_HW_SPENDING` | Numeric |  | Estimated company annual ICT spending : Hardware (USD) | Company Tech Sizing |  | NULL |  |
| 7 | `COMPANY_ANNUAL_SW_SPENDING` | Numeric |  | Estimated company annual ICT spending : Software (USD) | Company Tech Sizing |  | NULL |  |
| 8 | `COMPANY_ANNUAL_IT_COMNET_SPENDING` | Numeric |  | Estimated company annual ICT spending : IT Communications/Network (USD) | Company Tech Sizing |  | NULL |  |
| 9 | `COMPANY_ANNUAL_IT_SERVICES_SPENDING` | Numeric |  | Estimated company annual ICT spending : IT Services (USD) | Company Tech Sizing |  | NULL |  |
| 10 | `COMPANY_ANNUAL_IT_STAFF_SPENDING` | Numeric |  | Estimated company annual ICT spending : IT Staff (USD) | Company Tech Sizing |  | NULL |  |
| 11 | `COMPANY_ANNUAL_TELCO_SPENDING` | Numeric |  | Estimated company annual ICT spending : Telecommunications (USD) | Company Tech Sizing |  | NULL |  |
| 12 | `COMPANY_SERVERS` | Numeric |  | Estimated number of servers at the company | Company Tech Sizing |  | NULL |  |
| 13 | `COMPANY_WORKSTATIONS` | Numeric |  | Estimated number of workstations at the company | Company Tech Sizing |  | NULL |  |
| 14 | `COMPANY_PCS` | Numeric |  | Estimated number of PCs at the company | Company Tech Sizing |  | NULL |  |
| 15 | `COMPANY_DESKTOPS` | Numeric |  | Estimated number of desktops at the company | Company Tech Sizing |  | NULL |  |
| 16 | `COMPANY_LAPTOPS` | Numeric |  | Estimated number of laptops at the company | Company Tech Sizing |  | NULL |  |
| 17 | `COMPANY_TABLETS` | Numeric |  | Estimated number of tablets at the company | Company Tech Sizing |  | NULL |  |
| 18 | `COMPANY_PRINTERS` | Numeric |  | Estimated number of printers at the company | Company Tech Sizing |  | NULL |  |
| 19 | `COMPANY_STORAGE` | Numeric |  | Estimated Storage Capacity (GB) at the company | Company Tech Sizing |  | NULL |  |

## Table `COMPANY_TECHNOLOGY` (data, 8 fields)

Company technographics. There can be multiple technology records for a given company.

| # | Field | Type | Key | Definition | Topic | Possible values | Default | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `COMPANY_TECH_ID` | Text(128) | PK | Unique ID associated to the technology at that company |  |  | No default value |  |
| 2 | `COMPANY_ID` | Text(128) | FK → `COMPANY.COMPANY_ID` | Unique ID associated to the company | Company Identification |  | No default value |  |
| 3 | `TECH_ID` | Numeric | FK → `TECHNOLOGY_LOOKUP.TECH_ID` | Unique ID associated to the technology |  |  | No default value |  |
| 4 | `TECH_VENDOR` | Text(128) |  | Technology vendor |  |  | NULL |  |
| 5 | `TECH_NAME` | Text(128) |  | Technology/Product/Service |  |  | No default value |  |
| 6 | `FIRST_SEEN_DATE` | Date(10) |  | Date when the technology was detected at that company for the first time |  |  | NULL | Format: YYYY-MM-DD |
| 7 | `LAST_SEEN_DATE` | Date(10) |  | Date when the technology was detected at that company for the last  time |  |  | NULL | Format: YYYY-MM-DD |
| 8 | `TECH_CONFIDENCE_SCORE` | Numeric |  | Likelihood that the technology/product is present at the company |  | 0 to 100 | No default value | New in C&C v5.2 (2025) |

## Table `TECHNOLOGY_LOOKUP` (lookup, 8 fields)

Technographics catalogue.

| # | Field | Type | Key | Definition | Topic | Possible values | Default | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `TECH_ID` | Numeric | PK | Unique ID associated to the technology |  |  | No default value |  |
| 2 | `TECH_SERIES` | Text(64) |  | Technology series |  |  | 'Other' |  |
| 3 | `TECH_CATEGORY` | Text(64) |  | Technology category, reports to a TECH_SERIES |  |  | 'Other' |  |
| 4 | `TECH_VENDOR` | Text(128) |  | Technology vendor |  |  | NULL |  |
| 5 | `TECH_VENDOR_URL` | Text(64) |  | Technology vendor URL |  |  | NULL |  |
| 6 | `TECH_NAME` | Text(128) |  | Technology/Product/Service |  |  | No default value |  |
| 7 | `TECH_HOSTING` | Text(64) |  | Technology hosting type |  |  | NULL |  |
| 8 | `TECH_URL` | Text(128) |  | Technology URL |  |  | NULL |  |

## Table `SITE` (data, 42 fields)

Business locations, with firmographics. 1 site always reports to a Company within the COMPANY table.

| # | Field | Type | Key | Definition | Topic | Possible values | Default | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `SITE_ID` | Text(128) | PK | Unique ID associated to the site | Site Identification |  | No default value |  |
| 2 | `COMPANY_ID` | Text(128) | FK → `COMPANY.COMPANY_ID` | Unique ID associated to the company | Site Identification |  | No default value |  |
| 3 | `SITE_NAME` | Text(128) |  | Legal/registered name of the site | Site Identification |  | No default value |  |
| 4 | `SITE_TRADE_NAME` | Text(128) |  | DBA/operating name of the site | Site Identification |  | SITE_NAME |  |
| 5 | `SITE_STANDARDIZED_NAME` | Text(128) |  | ASCII-converted name of the site (useful for matching) | Site Identification |  | SITE_NAME |  |
| 6 | `SITE_STREETADDRESS1` | Text(64) |  | Street address of the site | Site Identification |  | NULL |  |
| 7 | `SITE_STREETADDRESS2` | Text(64) |  | Street address 2 of the site | Site Identification |  | NULL |  |
| 8 | `SITE_CITY` | Text(64) |  | City of the site | Site Identification |  | NULL |  |
| 9 | `SITE_POSTAL_STATE` | Text(64) |  | Postal State of the site | Site Identification |  | NULL |  |
| 10 | `SITE_POSTAL_CODE` | Text(16) |  | Zip Code for the site | Site Identification |  | NULL |  |
| 11 | `SITE_COUNTRY` | Text(64) |  | Country of the site | Site Identification |  | NULL |  |
| 12 | `SITE_PHONE` | Text(32) |  | Switchboard phone number of the site | Site Identification |  | NULL |  |
| 13 | `SITE_FAX` | Text(32) |  | Fax Number of the site | Site Identification |  | NULL |  |
| 14 | `SITE_URL` | Text(128) |  | Website of the site | Site Identification |  | NULL |  |
| 15 | `SITE_URL_DOMAIN` | Text(128) |  | Domain of the site | Site Identification |  | NULL |  |
| 16 | `SITE_LANGUAGE` | Text(32) |  | Primary language spoken at the site | Site Identification |  | NULL |  |
| 17 | `SITE_TYPE` | Text(3) |  | Site type: BRA=Branch, SLS=Single-location subsidiary, SHQ=Subsidiary HQ, STA=Standalone, UHQ=Ultimate HQ | Site Identification | BRA / SLS / SHQ / STA / UHQ | NULL |  |
| 18 | `SITE_DOMESTIC_HQ` | Numeric |  | Indicates whether the site is a domestic parent entity (1) or not (0) | Site Identification | 0 / 1 | NULL |  |
| 19 | `SITE_FRANCHISE` | Text(2) |  | Indicates whether the site is a franchisee (FE) or a franchisor (FR) | Site Identification | FE / FR | NULL |  |
| 20 | `SITE_LEGAL_STATUS` | Text(16) |  | Legal structure of the site | Site Identification |  | NULL |  |
| 21 | `SITE_START_YEAR` | Text |  | Founding year of the site | Site Identification |  | NULL | Format: YYYY |
| 22 | `SITE_EMPLOYEES` | Numeric |  | Number of site employees | Site Sizing |  | NULL |  |
| 23 | `SITE_EMPLOYEES_RANGE` | Text(32) |  | Range of the number of site employees | Site Sizing |  | NULL |  |
| 24 | `SITE_PRIMARY_NAICS6_CODE` | Text(6) |  | Primary 6-digit NAICS code of the site | Site Industry |  | NULL |  |
| 25 | `SITE_PRIMARY_NAICS6_DESCRIPTION` | Text(128) |  | Primary 6-digit NAICS description of the site | Site Industry |  | NULL |  |
| 26 | `SITE_PRIMARY_SIC4_CODE` | Text(4) |  | Primary 4-digit SIC code of the site | Site Industry |  | NULL |  |
| 27 | `SITE_PRIMARY_SIC4_DESCRIPTION` | Text(64) |  | Primary 4-digit SIC description of the site | Site Industry |  | NULL |  |
| 28 | `SITE_PRIMARY_SUB_INDUSTRY` | Text(64) |  | Primary sub-industry of the site | Site Industry |  | NULL |  |
| 29 | `SITE_PRIMARY_INDUSTRY` | Text(64) |  | All sub-industries of the site | Site Industry |  | NULL |  |
| 30 | `SITE_CONTINENT` | Text(13) |  | Continent of the site | Site Geo |  | NULL |  |
| 31 | `SITE_COUNTRY_REGION_CODE` | Text(5) |  | Country region code of the site | Site Geo | Ant / APac / EMEA / LatAm / NA | NULL |  |
| 32 | `SITE_COUNTRY_CODE` | Text(2) |  | ISO 3166-1 alpha-2 country code of the site | Site Geo |  | NULL |  |
| 33 | `SITE_REGION` | Text(64) |  | Region of the site | Site Geo |  | NULL |  |
| 34 | `SITE_SUBREGION` | Text(64) |  | Sub-region of the site | Site Geo |  | NULL |  |
| 35 | `SITE_STATE` | Text(64) |  | Sate of the site | Site Geo |  | NULL |  |
| 36 | `SITE_COUNTY` | Text(64) |  | County of the site | Site Geo |  | NULL |  |
| 37 | `SITE_CBSA_CODE` | Text(5) |  | Core-Based Statistical Area code of the site | Site Geo |  | NULL | Applies to: USA only |
| 38 | `SITE_CBSA` | Text(64) |  | Core-Based Statistical Area of the site | Site Geo |  | NULL | Applies to: USA only |
| 39 | `SITE_CBSA_TYPE` | Text(4) |  | Core-Based Statistical Area type (MSA: metropolitan, MiSA: micropolitan) of the site | Site Geo |  | NULL | Applies to: USA only |
| 40 | `SITE_CSA_CODE` | Text(3) |  | Combined Statistical Area code of the site | Site Geo |  | NULL | Applies to: USA only |
| 41 | `SITE_CSA` | Text(64) |  | Combined Statistical Area of the site | Site Geo |  | NULL | Applies to: USA only |
| 42 | `SITE_LINKEDIN_LINK` | Text(128) |  | Linkedin URL of the site | Site Identification |  | NULL |  |

## Table `SITE_TECH_SIZING` (data, 11 fields)

Site technology sizing attributes.

| # | Field | Type | Key | Definition | Topic | Possible values | Default | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `SITE_ID` | Text(128) | PK → `SITE.SITE_ID` | Unique ID associated to the site | Site Tech Sizing |  | No default value |  |
| 2 | `SITE_IT_EMPLOYEES` | Numeric |  | Estimated number of site employees in the IT department | Site Tech Sizing |  | NULL |  |
| 3 | `SITE_IT_EMPLOYEES_RANGE` | Text(32) |  | Range of the estimated number of site employees in the IT department | Site Tech Sizing |  | NULL |  |
| 4 | `SITE_SERVERS` | Numeric |  | Estimated number of servers at the site | Site Tech Sizing |  | NULL |  |
| 5 | `SITE_WORKSTATIONS` | Numeric |  | Estimated number of workstations at the site | Site Tech Sizing |  | NULL |  |
| 6 | `SITE_PCS` | Numeric |  | Estimated number of PCs at the site | Site Tech Sizing |  | NULL |  |
| 7 | `SITE_DESKTOPS` | Numeric |  | Estimated number of desktops at the site | Site Tech Sizing |  | NULL |  |
| 8 | `SITE_LAPTOPS` | Numeric |  | Estimated number of laptops at the site | Site Tech Sizing |  | NULL |  |
| 9 | `SITE_TABLETS` | Numeric |  | Estimated number of tablets at the site | Site Tech Sizing |  | NULL |  |
| 10 | `SITE_PRINTERS` | Numeric |  | Estimated number of printers at the site | Site Tech Sizing |  | NULL |  |
| 11 | `SITE_STORAGE` | Numeric |  | Estimated storage capacity (GB) at the site | Site Tech Sizing |  | NULL |  |

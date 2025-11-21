-- source file: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2022/NACE_LooKuP/NACE_LooKuP.TXT
-- region: USA, year: 2022

CREATE TABLE IF NOT EXISTS usa_2022_nace_lookup (
    nace4_code       text,
    nace4_desc       text,
    nace3_code       text,
    nace3_desc       text,
    nace2_code       text,
    nace2_desc       text,
    nace1_code       text,
    nace1_desc       text,
    nace_subindustry text,
    nace_industry    text
);
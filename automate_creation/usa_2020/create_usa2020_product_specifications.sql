-- source file: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2020_RDFv3.14/ProductSpecifications.TXT
-- region: USA, year: 2020
-- add if does not exist
CREATE TABLE IF NOT EXISTS usa_2020_product_specifications (
    tabkey      text,
    class       text,
    manuf       text,
    model       text,
    group_code        text,
    series      text,
    devtype     text,
    description text,
    category    text
);
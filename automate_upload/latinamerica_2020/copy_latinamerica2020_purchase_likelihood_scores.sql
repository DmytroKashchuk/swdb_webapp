-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2020_RDFv3.14/PurchaseLikelihoodScores.TXT

\copy latinamerica_2020_purchase_likelihood_scores FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2020_RDFv3.14/PurchaseLikelihoodScores_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');

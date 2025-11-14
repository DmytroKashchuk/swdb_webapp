-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2018/PurchaseLikelihoodScores.TXT

\copy usa_2018_purchase_likelihood_scores
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2018/PurchaseLikelihoodScores_utf8.TXT'
WITH (FORMAT csv, HEADER true);
-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2016/PurchaseLikelihoodScores.TXT

\copy europe_2016_purchase_likelihood_scores FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2016/PurchaseLikelihoodScores_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');

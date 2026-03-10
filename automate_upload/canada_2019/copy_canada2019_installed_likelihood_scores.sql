-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2019/InstalledLikelihoodScores.TXT

\copy canada_2019_installed_likelihood_scores FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2019/InstalledLikelihoodScores_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');

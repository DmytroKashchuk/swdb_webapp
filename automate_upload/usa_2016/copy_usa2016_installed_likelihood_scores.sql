-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2016/InstalledLikelihoodScores.TXT

\copy usa_2016_installed_likelihood_scores FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2016/InstalledLikelihoodScores_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');

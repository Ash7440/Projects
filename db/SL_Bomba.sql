SELECT
    Players.Full_name,
    Clubs.Nazvn AS Club_name,
    Seasons.Nazvn AS Season_name,
    SUM(Player_stats.Goals) AS "Total goals",
    SUM(Player_stats.Games_played) AS "Total games",
    ROUND(
        IF(SUM(Player_stats.Games_played) > 0, 
           SUM(Player_stats.Goals) / SUM(Player_stats.Games_played), 
           0), 
        2
    ) AS "Goals/games"
FROM Teams_lineups
INNER JOIN Players ON Teams_lineups.Player_id = Players.Player_id
INNER JOIN Clubs ON Teams_lineups.Club_id = Clubs.Club_id
INNER JOIN Seasons ON Teams_lineups.Season_id = Seasons.Season_id
INNER JOIN Player_stats 
    ON Teams_lineups.Player_id = Player_stats.Player_id
    AND Teams_lineups.Club_id = Player_stats.Club_id
    AND Teams_lineups.Season_id = Player_stats.Season_id
GROUP BY 
    Players.Full_name, 
    Clubs.Nazvn, 
    Seasons.Nazvn
HAVING SUM(Player_stats.Goals) > 0
ORDER BY 
    SUM(Player_stats.Goals) DESC;
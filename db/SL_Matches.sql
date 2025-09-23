SELECT 
    Matches.Match_date,
    Matches.Match_time,
    Seasons.Nazvn AS Season_name,
    Matches.Stadium,
    home.Nazvn AS "Home team",
    CONCAT(Matches.Home_score, ':', Matches.Away_score) AS "Score",
    away.Nazvn AS "Guest team"
FROM Matches
INNER JOIN Seasons ON Matches.Season_id = Seasons.Season_id
INNER JOIN Clubs AS home ON Matches.Home_club_id = home.Club_id
INNER JOIN Clubs AS away ON Matches.Away_club_id = away.Club_id
ORDER BY Matches.Match_date DESC, Matches.Match_time DESC;
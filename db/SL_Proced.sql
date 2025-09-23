DELIMITER //
CREATE PROCEDURE GetClubPlayers(IN team_id INT, IN season_id INT)
BEGIN
    SELECT 
        m.Match_date,
        m.Match_time,
        s.Nazvn AS Season_name,
        m.Stadium,
        CASE 
            WHEN m.Home_club_id = team_id THEN home.Nazvn 
            ELSE away.Nazvn 
        END AS Team,
        CASE 
            WHEN m.Home_club_id = team_id THEN "Дома" 
            ELSE "В гостях" 
        END AS "Место",
        CONCAT(m.Home_score, ':', m.Away_score) AS Score,
        CASE 
            WHEN m.Home_club_id = team_id AND m.Home_score > m.Away_score THEN "Победа"
            WHEN m.Away_club_id = team_id AND m.Away_score > m.Home_score THEN "Победа"
            WHEN m.Home_score = m.Away_score THEN "Ничья"
            ELSE "Поражение"
        END AS Result,
        CASE 
            WHEN m.Home_club_id = team_id THEN away.Nazvn 
            ELSE home.Nazvn 
        END AS Opponent
    FROM Matches m
    JOIN Seasons s ON m.Season_id = s.Season_id
    JOIN Clubs home ON m.Home_club_id = home.Club_id
    JOIN Clubs away ON m.Away_club_id = away.Club_id
    WHERE 
        m.Season_id = season_id
        AND (m.Home_club_id = team_id OR m.Away_club_id = team_id)
    ORDER BY 
        m.Match_date DESC, 
        m.Match_time DESC;
END //
DELIMITER ;

CALL GetClubPlayers(15, 1);
SET @team_id = 1;     
SET @season_id = 1; 

SELECT 
    m.Match_date,
    m.Match_time,
    s.Nazvn AS Season_name,
    m.Stadium,
    (SELECT Nazvn FROM Clubs WHERE Club_id = @team_id) AS Team,
    CASE 
        WHEN m.Home_club_id = @team_id THEN "Дома" 
        ELSE "В гостях" 
    END AS "Место",
    CONCAT(m.Home_score, ':', m.Away_score) AS Score,
    CASE 
        WHEN m.Home_club_id = @team_id AND m.Home_score > m.Away_score THEN "Победа"
        WHEN m.Away_club_id = @team_id AND m.Away_score > m.Home_score THEN "Победа"
        WHEN m.Home_score = m.Away_score THEN "Ничья"
        ELSE "Поражение"
    END AS Result,
    COALESCE(
        (SELECT Nazvn FROM Clubs WHERE Club_id = 
            CASE 
                WHEN m.Home_club_id = @team_id THEN m.Away_club_id 
                ELSE m.Home_club_id 
            END)
    ) AS Apponent
FROM Matches m
INNER JOIN Seasons s ON m.Season_id = s.Season_id
WHERE 
    m.Season_id = @season_id
    AND (m.Home_club_id = @team_id OR m.Away_club_id = @team_id)
ORDER BY 
    m.Match_date DESC, 
    m.Match_time DESC;
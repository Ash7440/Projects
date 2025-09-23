SELECT 
    Clubs.Nazvn,
    days,
    start_time,
    duration,
    training_type
FROM Training_schedule
INNER JOIN Clubs ON Clubs.Club_id = Training_schedule.Club_id
WHERE days & 1
AND days & 4; 

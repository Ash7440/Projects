DROP TABLE Training_schedule;

CREATE TABLE Training_schedule (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    Club_id INT NOT NULL,
    days SET('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Субота', 'Воскресенье'),
    start_time TIME,
    duration INT,
    training_type ENUM('физическая', 'тактическая', 'восстановительная'), 
    FOREIGN KEY (Club_id) REFERENCES Clubs(Club_id)
)ENGINE=InnoDB;
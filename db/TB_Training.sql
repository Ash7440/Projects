DROP TABLE Training_schedule;

CREATE TABLE Training_schedule (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    Club_id INT NOT NULL,
    days SET('�����������', '�������', '�����', '�������', '�������', '������', '�����������'),
    start_time TIME,
    duration INT,
    training_type ENUM('����������', '�����������', '�����������������'), 
    FOREIGN KEY (Club_id) REFERENCES Clubs(Club_id)
)ENGINE=InnoDB;
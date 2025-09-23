drop table Staff;
drop table Player_stats;
drop table Teams_lineups;
drop table Matches;
drop table Players;
drop table Clubs;
drop table Seasons;

CREATE TABLE Players (
    Player_id INT PRIMARY KEY,
    Full_name VARCHAR(50) NOT NULL,
    Age TINYINT NOT NULL,
    Height TINYINT UNSIGNED NOT NULL,
    Weight TINYINT UNSIGNED NOT NULL,
    Nationality VARCHAR(50) NOT NULL
)ENGINE=InnoDB;

CREATE TABLE Clubs (
    Club_id INT PRIMARY KEY AUTO_INCREMENT,
    Nazvn VARCHAR(50) NOT NULL,
    Address VARCHAR(50) NOT NULL,
    Found_year SMALLINT NOT NULL
)ENGINE=InnoDB;

CREATE TABLE Staff (
    Staff_id INT PRIMARY KEY AUTO_INCREMENT,
    Club_id INT NOT NULL,
    Full_name VARCHAR(45) NOT NULL,
    Role VARCHAR(20) NOT NULL,
    FOREIGN KEY (Club_id) REFERENCES Clubs(Club_id)
)ENGINE=InnoDB;

CREATE TABLE Seasons (
    Season_id INT PRIMARY KEY AUTO_INCREMENT,
    Start_date DATE NOT NULL,
    End_date DATE NOT NULL,
    Nazvn CHAR(5) NOT NULL
)ENGINE=InnoDB;

CREATE TABLE Teams_lineups (
    Player_id INT NOT NULL,
    Club_id INT NOT NULL,
    Season_id INT NOT NULL,
    Player_number TINYINT UNSIGNED NOT NULL,
    Position VARCHAR(15) NOT NULL,
    PRIMARY KEY (Player_id, Club_id, Season_id),
    FOREIGN KEY (Player_id) REFERENCES Players(Player_id),
    FOREIGN KEY (Club_id) REFERENCES Clubs(Club_id),
    FOREIGN KEY (Season_id) REFERENCES Seasons(Season_id)
)ENGINE=InnoDB;

CREATE TABLE Matches (
    Match_id INT PRIMARY KEY AUTO_INCREMENT,
    Home_club_id INT NOT NULL,
    Away_club_id INT NOT NULL,
    Season_id INT NOT NULL,
    Match_date DATE NOT NULL,
    Match_time TIME NOT NULL,
    Stadium VARCHAR(35) NOT NULL,
    Home_score TINYINT UNSIGNED NOT NULL DEFAULT 0,
    Away_score TINYINT UNSIGNED NOT NULL DEFAULT 0,
    FOREIGN KEY (Home_club_id) REFERENCES Clubs(Club_id),
    FOREIGN KEY (Away_club_id) REFERENCES Clubs(Club_id),
    FOREIGN KEY (Season_id) REFERENCES Seasons(Season_id)
)ENGINE=InnoDB;

CREATE TABLE Player_stats (
    Stut_id INT PRIMARY KEY AUTO_INCREMENT,
    Player_id INT NOT NULL,
    Club_id INT NOT NULL,
    Season_id INT NOT NULL,
    Games_played TINYINT UNSIGNED NOT NULL DEFAULT 0,
    Goals INT NOT NULL DEFAULT 0,
    Assists TINYINT UNSIGNED NOT NULL DEFAULT 0,
    Yellow_cards TINYINT UNSIGNED NOT NULL DEFAULT 0,
    Red_cards TINYINT UNSIGNED NOT NULL DEFAULT 0,
    FOREIGN KEY (Player_id) REFERENCES Players(Player_id),
    FOREIGN KEY (Club_id) REFERENCES Clubs(Club_id),
    FOREIGN KEY (Season_id) REFERENCES Seasons(Season_id)
)ENGINE=InnoDB;
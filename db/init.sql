-- runs automatically on the first start of the postgres container

CREATE TABLE wanted_criminals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),                 -- real name, can be unknown (NULL)
    nickname VARCHAR(200) NOT NULL,
    reward NUMERIC(12, 2) NOT NULL CHECK (reward >= 0),
    latitude DOUBLE PRECISION,         -- last known coordinates (optional)
    longitude DOUBLE PRECISION,
    location_note TEXT,                -- or just a text note about location
    difficulty INT NOT NULL CHECK (difficulty BETWEEN 1 AND 10),
    armed BOOLEAN NOT NULL DEFAULT FALSE,
    has_crew BOOLEAN NOT NULL DEFAULT FALSE,
    escape_master BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE hunt_logs (
    id SERIAL PRIMARY KEY,
    criminal_id INT NOT NULL REFERENCES wanted_criminals(id) ON DELETE CASCADE,
    success BOOLEAN NOT NULL,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO wanted_criminals (name, nickname, reward, latitude, longitude, location_note, difficulty, armed, has_crew, escape_master) VALUES
('Asimov Solensan', 'Red Eye Dealer', 25000000, NULL, NULL, 'Last seen on Mars, Tharsis docks', 7, TRUE, TRUE, FALSE),
(NULL, 'Teddy Bomber', 300000000, NULL, NULL, 'Somewhere near Mars orbit', 8, TRUE, FALSE, TRUE),
('Mad Pierrot', 'Tongpu', 0, 12.5, -45.3, NULL, 10, TRUE, FALSE, TRUE),
('Abdul Hakim', 'The Thief', 1500000, NULL, NULL, 'Ganymede casino district', 4, FALSE, FALSE, TRUE),
('Vincent Volaju', 'Vincent', 500000000, 40.7, -74.0, 'Alba City, Mars', 9, TRUE, TRUE, FALSE),
('Rhint Celonias', 'Hacker Kid', 4000, NULL, NULL, 'Callisto, east sector', 2, FALSE, FALSE, FALSE),
('Gren', 'The Saxophonist', 3000, NULL, NULL, 'Titan, jazz bar', 5, TRUE, FALSE, FALSE);

INSERT INTO hunt_logs (criminal_id, success, notes) VALUES
(1, FALSE, 'Target escaped through an asteroid field.'),
(1, FALSE, 'Lost him in the crowd at the docks.'),
(1, TRUE, 'Captured after a short chase.'),
(2, FALSE, 'Bomb went off before we arrived.'),
(2, FALSE, 'Wrong tip, he was never there.'),
(3, FALSE, 'He was too fast, barely survived.'),
(4, TRUE, 'Caught him at the casino.'),
(5, FALSE, 'Gate explosion, had to retreat.'),
(6, TRUE, 'Easy catch, he gave up immediately.'),
(7, FALSE, 'Bar fight, he slipped away.'),
(5, FALSE, 'Tracked him to Alba City but lost signal.');

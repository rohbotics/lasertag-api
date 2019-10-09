CREATE TABLE users (                                                       
	id bigint NOT NULL PRIMARY KEY DEFAULT generate_uid(),
	email varchar(64) NOT NULL UNIQUE,
	password varchar NOT NULL,
	name varchar(64)
);

CREATE TABLE games (
	id bigint NOT NULL PRIMARY KEY DEFAULT generate_uid(),
	start timestamp,
	finish timestamp
);

CREATE TYPE team_type AS ENUM ('individual', 'group');

CREATE TABLE teams (
	id bigint NOT NULL PRIMARY KEY DEFAULT generate_uid(),
	name varchar,
	type team_type NOT NULL
);

CREATE TABLE shots (
	id bigint NOT NULL PRIMARY KEY DEFAULT generate_uid(),
	time timestamp NOT NULL,
	game bigint NOT NULL REFERENCES games(id) ON DELETE RESTRICT,
	shooter bigint NOT NULL REFERENCES users(id),
	target bigint NOT NULL REFERENCES users(id) 
);

CREATE TABLE game_teams (
	game bigint NOT NULL REFERENCES games(id),
	team bigint NOT NULL REFERENCES teams(id)
);

CREATE TABLE team_users (
	team bigint NOT NULL REFERENCES teams(id),
	member bigint NOT NULL REFERENCES users(id)
);

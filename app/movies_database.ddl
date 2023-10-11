CREATE SCHEMA IF NOT EXISTS content;
CREATE TYPE gender AS ENUM ('male', 'female');

CREATE TABLE IF NOT EXISTS content.film_work (
  id uuid PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  creation_date DATE,
  file_path TEXT,
  rating FLOAT,
  type TEXT NOT NULL,
  created TIMESTAMP WITH TIME ZONE,
  modified TIMESTAMP WITH TIME ZONE,
  certificate VARCHAR(512)
);

CREATE TABLE IF NOT EXISTS content.genre (
  id uuid PRIMARY KEY,
  name VARCHAR(32) NOT NULL,
  description TEXT,
  created TIMESTAMP WITH TIME ZONE,
  modified TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
  id uuid PRIMARY KEY,
  film_work_id uuid NOT NULL,
  genre_id uuid NOT NULL,
  created TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS content.person (
  id uuid PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL,
  created TIMESTAMP WITH TIME ZONE,
  modified TIMESTAMP WITH TIME ZONE,
  gender "gender"
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
  id uuid PRIMARY KEY,
  film_work_id uuid NOT NULL,
  person_id uuid NOT NULL,
  role VARCHAR(32) NOT NULL,
  created TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS film_work_creation_date_idx ON content.film_work (creation_date);
CREATE UNIQUE INDEX IF NOT EXISTS film_work_genre_idx ON content.genre_film_work (film_work_id, genre_id);
CREATE UNIQUE INDEX IF NOT EXISTS film_work_person_role_idx ON content.person_film_work (film_work_id, person_id, role);

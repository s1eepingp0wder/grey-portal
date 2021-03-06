DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS assignments CASCADE;
DROP TABLE IF EXISTS course_sessions CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS user_assignments CASCADE;

CREATE TABLE users (
    id bigserial PRIMARY KEY,
    email text UNIQUE NOT NULL,
    first_name text NOT NULL,
    last_name text NOT NULL,
    password text NOT NULL,
    role varchar(7) NOT NULL CHECK (role IN ('teacher', 'student'))
);

-- Teacher has courses
CREATE TABLE courses (
    course_id bigserial PRIMARY KEY,
    course_number text UNIQUE NOT NULL,
    course_name text UNIQUE NOT NULL,
    description text NOT NULL,
    teacher_id bigserial NOT NULL REFERENCES users(id)
);

-- Students prevented from making session python-side
-- When we get into the code, just check roles.-Danny
CREATE TABLE course_sessions (
    id bigserial PRIMARY KEY,
    course_id bigint REFERENCES courses(course_id) NOT NULL,
    time text NOT NULL,
    number_students int NOT NULL
);

CREATE TABLE user_sessions (
    student_id bigint REFERENCES users(id),
    session_id bigint REFERENCES course_sessions(id),
    CONSTRAINT user_session_key PRIMARY KEY (student_id, session_id)
);

CREATE TABLE assignments (
    assignment_id bigserial UNIQUE PRIMARY KEY,
    assignment_name text NOT NULL,
    points_earned int,
    points_available int NOT NULL,
    instructions text NOT NULL,
    due_date text NOT NULL,
    sesh_id bigserial NOT NULL REFERENCES course_sessions(id)
 );

 CREATE TABLE user_assignments (
     point_earned int,
     assignment_id bigserial NOT NULL REFERENCES assignments(assignment_id),
     student_id bigserial NOT NULL REFERENCES users(id)
 );

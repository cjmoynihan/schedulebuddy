create table if not exists users(
    user_id INTEGER primary key autoincrement,
    username text not null,
    password text not null
);
create table if not exists events(
    event_id INTEGER primary key autoincrement,
    event_name text not null,
    user_id int not null,
    start_time int not null,
    end_time int not null
);
create table if not exists recurring(
    event_id INTEGER primary key autoincrement,
    mon bool not null,
    tue bool not null,
    wed bool not null,
    thur bool not null,
    fri bool not null,
    sat bool not null,
    sun bool not null
)
create table if not exists friends(
    user_id int not null,
    friend_id int not null
);

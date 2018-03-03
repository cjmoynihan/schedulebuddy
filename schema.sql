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
-- To be executed to initialize the database

drop table if exists Engagements;
drop table if exists IncomingData;
drop table if exists OutgoingData;

create table Engagements(project text,
    date_started date,
    owner text,
    comments text,
    primary key(project(200))
    );

create table IncomingData(
    project text not null, 
    dataset text, 
    version text, 
    timestamp datetime, 
    urls text, 
    checksums text, 
    metadata_url text, 
    comments text, 
    username text, 
    hostname text
    );

create table OutgoingData(
    project text not null,
    dataset text,
    version integer,
    timestamp datetime,
    urls text,
    checksums text,
    metadata_url text,
    comments text,
    username text,
    hostname text
    );

--- bcb indicators
create table if not exists bcb_indicators (
    id serial primary key,
    series_code integer not null,
    series_name varchar(255) not null,
    reference_date date not null,
    indicator_value decimal(20, 10) not null,
    ingestion_date timestamp default current_timestamp,
    constraint unique_series_date unique (series_code, reference_date)
);
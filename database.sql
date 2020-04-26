create or replace schema books collate utf8mb4_general_ci;

create or replace table authors
(
	id_authors int auto_increment
		primary key,
	name text not null
);

create or replace table shops
(
	id_shops int auto_increment
		primary key,
	name text null
);

create or replace table titles
(
	id_titles int auto_increment
		primary key,
	title text null
);

create or replace table ISBN_titles
(
	ISBN mediumtext null,
	id_titles int null,
	constraint ISBN_titles_titles_id_titles_fk
		foreign key (id_titles) references titles (id_titles)
);

create or replace table authors_titles
(
	id_titles int null,
	id_authors int null,
	constraint authors_titles_authors_id_author_fk
		foreign key (id_authors) references authors (id_authors),
	constraint authors_titles_titles_id_titles_fk
		foreign key (id_titles) references titles (id_titles)
);

create or replace table prices
(
	id_prices int auto_increment
		primary key,
	id_titles int null,
	id_shops int null,
	price double null,
	link text null,
	add_time datetime default current_timestamp() null,
	constraint prices_shops_id_shops_fk
		foreign key (id_shops) references shops (id_shops),
	constraint prices_titles_id_titles_fk
		foreign key (id_titles) references titles (id_titles)
);


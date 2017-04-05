CREATE TABLE IF NOT EXISTS USERS(id integer PRIMARY KEY AUTOINCREMENT, userName VARCHAR(30), teamName VARCHAR(30));
CREATE TABLE IF NOT EXISTS REPOS(id integer PRIMARY KEY AUTOINCREMENT, name VARCHAR(30) UNIQUE);
CREATE TABLE IF NOT EXISTS PullRequests(
    id integer PRIMARY KEY,
    user VARCHAR(30),
	number VARCHAR(30),
	repo VARCHAR(30),
	title VARCHAR(200),
	body TEXT,
	state VARCHAR(30),
	merged VARCHAR(30),
	comments_count VRACHAR(30),
	createDate TEXT,
	endDate TEXT);
CREATE TABLE IF NOT EXISTS Comments(
	id integer PRIMARY KEY,
	id_pr integer,
	repo VARCHAR(30),
	from_user VARCHAR(30),
	to_user VARCHAR(30),
	body TEXT,
	isApproved integer,
	submitDate TEXT);
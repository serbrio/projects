-- Represent users, which are supposed to use this DB
CREATE TABLE `users` (
    `id` SMALLINT UNSIGNED AUTO_INCREMENT,
    `first_name` VARCHAR(32),
    `last_name` VARCHAR(32),
    `username` VARCHAR(32) NOT NULL UNIQUE,
    `born` YEAR NOT NULL,
    PRIMARY KEY(`id`)
);

-- Represent languages available in ISO 639-1: alpha2(two-letters), English name
CREATE TABLE `languages` (
    `id` TINYINT UNSIGNED AUTO_INCREMENT,
    `alpha2` VARCHAR(2) NOT NULL UNIQUE,
    `name` VARCHAR(80) NOT NULL,
    PRIMARY KEY(`id`)
);

-- Load data from csv file resided locally on client into table 'languages'
-- https://dev.mysql.com/doc/refman/8.0/en/load-data.html
-- https://stackoverflow.com/questions/59993844/error-loading-local-data-is-disabled-this-must-be-enabled-on-both-the-client
LOAD DATA LOCAL INFILE 'language-codes.csv' INTO TABLE `languages`
    FIELDS TERMINATED BY ',' ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 LINES
    (`alpha2`, `name`);

-- Represent books
CREATE TABLE `books` (
    `id` SMALLINT UNSIGNED AUTO_INCREMENT,
    `title` VARCHAR(100) NOT NULL,
    `orig_title` VARCHAR(100) NOT NULL,
    `lang` TINYINT UNSIGNED NOT NULL,
    `orig_lang` TINYINT UNSIGNED NOT NULL,
    `genre` ENUM('fiction', 'non-fiction', 'traditional', 'biography', 'picture books', 'poetry') NOT NULL,
    `age_category` ENUM('pre-readers', 'early-readers', 'intermediate', 'middle grade', 'young adults', 'adults') NOT NULL,
    PRIMARY KEY(`id`),
    FOREIGN KEY(`lang`) REFERENCES `languages`(`id`),
    FOREIGN KEY(`orig_lang`) REFERENCES `languages`(`id`)
);

-- Represent ISBNS - available editions of the book
CREATE TABLE `isbns` (
    `book_id` SMALLINT UNSIGNED NOT NULL,
    `isbn` VARCHAR(17) NOT NULL UNIQUE,
    PRIMARY KEY(`book_id`, `isbn`),
    FOREIGN KEY(`book_id`) REFERENCES `books`(`id`)
);

-- Represent writers, which can be both authors and translators
-- Assume there are no writers with the same first and last name pair
-- Below UNIQUE INDEX created for last and first names pair
CREATE TABLE `writers` (
    `id` SMALLINT UNSIGNED AUTO_INCREMENT,
    `first_name` VARCHAR(32) NOT NULL,
    `last_name` VARCHAR(32) NOT NULL,
    `born` YEAR,
    PRIMARY KEY(`id`)
);

-- Represent authored - relationship between books and writers:
-- by which writer (if any) is the book authored
CREATE TABLE `authored` (
    `book_id` SMALLINT UNSIGNED NOT NULL,
    `writer_id` SMALLINT UNSIGNED NOT NULL,
    FOREIGN KEY(`book_id`) REFERENCES `books`(`id`),
    FOREIGN KEY(`writer_id`) REFERENCES `writers`(`id`),
    PRIMARY KEY(`book_id`, `writer_id`)
);

-- Represent translated - relationship between books and writers:
-- by which writer (if any) is the book translated translated
CREATE TABLE `translated` (
    `book_id` SMALLINT UNSIGNED NOT NULL,
    `writer_id` SMALLINT UNSIGNED NOT NULL,
    FOREIGN KEY(`book_id`) REFERENCES `books`(`id`),
    FOREIGN KEY(`writer_id`) REFERENCES `writers`(`id`),
    PRIMARY KEY(`book_id`, `writer_id`)
);

-- Represent desired - relationship between users and books:
-- which book (if any) desires to read the user
CREATE TABLE `desired` (
    `book_id` SMALLINT UNSIGNED NOT NULL,
    `user_id` SMALLINT UNSIGNED NOT NULL,
    FOREIGN KEY(`book_id`) REFERENCES `books`(`id`),
    FOREIGN KEY(`user_id`) REFERENCES `users`(`id`),
    PRIMARY KEY(`book_id`, `user_id`)
);

-- Represent reads - relationship between users and books:
-- user can have read some books
CREATE TABLE `reads` (
    `id` INT UNSIGNED AUTO_INCREMENT,
    `book_id` SMALLINT UNSIGNED NOT NULL,
    `user_id` SMALLINT UNSIGNED NOT NULL,
    `started` DATE NOT NULL,
    `finished` DATE,
    FOREIGN KEY(`book_id`) REFERENCES `books`(`id`),
    FOREIGN KEY(`user_id`) REFERENCES `users`(`id`),
    PRIMARY KEY(`id`)
);

-- Represent comments which user can leave for a read
CREATE TABLE `comments` (
    `id` INT UNSIGNED AUTO_INCREMENT,
    `read_id` INT UNSIGNED NOT NULL,
    `content` VARCHAR(3000) NOT NULL,
    `timestamp` TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY(`id`),
    FOREIGN KEY(`read_id`) REFERENCES `reads`(`id`)
);

-- Create indexes to speed up common searches

-- According to the MySQL documentation at <https://dev.mysql.com/doc/refman/8.4/en/primary-key-optimization.html>,
-- there is no need to create INDEX for 'desired', 'authored', 'translated',
-- because these tables consist of two keys, both of which are included in PRIMARY KEY,
-- and thus both automatically indexed.
--
-- This indexes are used in:
-- authored(book_id) - for search of book in authored while creating the VIEW books_with_authors
-- authored(writer_id) - for search of writer in authored, neede for
--      the functions:
--          get_bookId()
--      the stored procedures:
--          comments_on_book
-- desired(user_id) - for search of user in desired, needed for
--      the functions:
--          get_writerId(), get_bookId()
--      the stored procedures:
--          books_desired_by, books_desired_never_started_by, comments_on_book


-- Create index to speed up search of books by genre, needed for
-- the stored procedures:
--      books_in_genre
CREATE INDEX `book_genre_search` ON `books` (`genre`);

-- Create index to speed up search of books by age category, needed for
-- the stored procedures:
--      books_in_age_cat
CREATE INDEX `book_age_category_search` ON `books` (`age_category`);

-- Create index for search of writer in writers, needed for
-- the functions:
--      get_writerId(), get_bookId()
-- the stored procedure:
--      books_written_by
CREATE UNIQUE INDEX `writer_search` ON `writers` (`last_name`, `first_name`);

-- Create index for search of username in users, needed for
-- the functions:
--      get_userId()
-- the stored procedures:
--      comments_on_book, start_reading, finish_reading, leave_comment
CREATE INDEX `username_search` ON `users` (`username`);

-- Create index for search of language code in languages, needed for
-- the functions:
--      get_langId()
-- the stored procedures:
--      add_new_book
CREATE INDEX `alpha2_lang_search` ON `languages` (`alpha2`);

-- Create index for search of book's title in books, needed for
-- the functions:
--      get_bookId()
-- the stored procedures:
--      comments_on_book
CREATE INDEX `book_title_search` ON `books` (`title`);

-- Create index for search of user in reads, needed for
-- the functions:
--      get_latter_read(), get_latter_started(), get_latter_finished()
-- the stored procedures:
--      books_desired_never_started_by, books_started_never_finished_by,
--      books_ever_finished_by, books_started_notyet_finished_by,
--      finish_reading, leave_comment
CREATE INDEX `reads_user_id_search` ON `reads` (`user_id`);

-- Create index for search of book in reads, needed for
-- the functions:
--      get_latter_read(), get_latter_started(), get_latter_finished(),
-- the stored procedures:
--      books_started_never_finished_by, books_ever_finished_by,
--      books_started_notyet_finished_by, finish_reading, leave_comment
CREATE INDEX `reads_book_id_search` ON `reads` (`book_id`);

-- Create index for search of read_id in comments, needed for
-- the stored procedure:
--      comments_on_book
CREATE INDEX `comments_read_id_search` ON `comments` (`read_id`);



-- Create function to find user_id by username
delimiter //
CREATE FUNCTION `get_userId`(`u_name` VARCHAR(32))
    RETURNS SMALLINT UNSIGNED DETERMINISTIC
BEGIN
    DECLARE `found_id` SMALLINT UNSIGNED;
    SELECT `id` INTO `found_id` FROM `users`
    WHERE `username` = `u_name`;
    RETURN `found_id`;
END//
delimiter ;

-- Create function to find writer_id by first_name and last_name
delimiter //
CREATE FUNCTION `get_writerId`(`first` VARCHAR(32), `last` VARCHAR(32))
    RETURNS SMALLINT UNSIGNED DETERMINISTIC
BEGIN
    DECLARE `found_id` SMALLINT UNSIGNED;
    SELECT `id` INTO `found_id` FROM `writers`
    WHERE `last_name` = `last`
    AND `first_name` = `first`;
    RETURN `found_id`;
END//
delimiter ;

-- Create function to find language id by alpha2
delimiter //
CREATE FUNCTION `get_langId`(`a2` VARCHAR(2))
    RETURNS TINYINT UNSIGNED DETERMINISTIC
BEGIN
    DECLARE `found_id` TINYINT UNSIGNED;
    SELECT `id` INTO `found_id` FROM `languages`
    WHERE `alpha2` = `a2`;
    RETURN `found_id`;
END//
delimiter ;

-- Create function to find book_id by title and author first and last name.
delimiter //
CREATE FUNCTION `get_bookId`(`t` VARCHAR(100), `first` VARCHAR(32), `last` VARCHAR(32))
    RETURNS SMALLINT UNSIGNED DETERMINISTIC
BEGIN
    DECLARE `found_id` SMALLINT UNSIGNED;
    SELECT `id` INTO `found_id` FROM `books`
    WHERE `title` = `t`
    AND `id` IN (
        SELECT `book_id` FROM `authored`
        WHERE `writer_id` = (SELECT get_writerId(`first`, `last`))
    );
    RETURN `found_id`;
END//
delimiter ;

-- Create function to find the writer's full name (given writer's id)
delimiter //
CREATE FUNCTION `get_writerFullName`(`w_id` SMALLINT UNSIGNED)
    RETURNS VARCHAR(65) DETERMINISTIC
BEGIN
    DECLARE `found_name` VARCHAR(65);
    SELECT CONCAT_WS(' ', `first_name`, `last_name`) INTO `found_name` FROM `writers`
    WHERE `id` = `w_id`;
    RETURN `found_name`;
END//
delimiter ;

-- Create function to find id of latter started reading
-- (given book_id, user_id)
delimiter //
CREATE FUNCTION `get_latter_read`(`b_id` SMALLINT UNSIGNED, `u_id` SMALLINT UNSIGNED)
    RETURNS INT UNSIGNED DETERMINISTIC
BEGIN
    DECLARE `found_id` INT UNSIGNED;
    SELECT `id` INTO `found_id` FROM `reads`
    WHERE `user_id` = u_id
    AND `book_id` = b_id
    ORDER BY `started` DESC
    LIMIT 1;
    RETURN `found_id`;
END//
delimiter ;

-- Create function to find the latter started read for the book by the user
delimiter //
CREATE FUNCTION `get_latter_started`(`bookId` SMALLINT UNSIGNED, `userId` SMALLINT UNSIGNED)
    RETURNS DATE DETERMINISTIC
BEGIN
    DECLARE `found_date` DATE;
    SELECT MAX(`started`) INTO `found_date` FROM `reads`
    WHERE `book_id` = `bookId`
    AND `user_id` = `userId`;
    RETURN `found_date`;
END//
delimiter ;

-- Create function to find the latter finished read for the book by the user
delimiter //
CREATE FUNCTION `get_latter_finished`(`bookId` SMALLINT UNSIGNED, `userId` SMALLINT UNSIGNED)
    RETURNS DATE DETERMINISTIC
BEGIN
    DECLARE `found_date` DATE;
    SELECT MAX(`finished`) INTO `found_date` FROM `reads`
    WHERE `book_id` = `bookId`
    AND `user_id` = `userId`;
    RETURN `found_date`;
END//
delimiter ;




-- Create view of books in original language
CREATE VIEW `books_original_language` AS
    SELECT * FROM `books`
    WHERE `lang` = `orig_lang`;

-- Create view of books not in original language (translated)
CREATE VIEW `books_translated` AS
    SELECT * FROM `books`
    WHERE `lang` != `orig_lang`;

-- Create view of books with athors,
-- authors for one book represented in array by full name ("first_name last_name")
CREATE VIEW `books_with_authors` AS
    SELECT `id`, `title`, `lang`, `orig_lang`, `genre`, `age_category`,
        JSON_ARRAYAGG(get_writerFullName(`writer_id`)) AS `writer`
    FROM `books`
    LEFT JOIN `authored` ON `authored`.`book_id` = `books`.`id`
    GROUP BY `books`.`id`;

-- Create view of books with authors and ISBNs,
-- for each book:
-- authors are represented in array by full name("first_name last_name"),
-- isbns are represented in array ("isbn1, isbn2")
CREATE VIEW `books_with_authors_isbns` AS
    SELECT `id`, `title`, `lang`, `orig_lang`, `genre`, `age_category`, `writer`,
        JSON_ARRAYAGG(`isbn`) AS `isbn`
    FROM `books_with_authors`
    LEFT JOIN `isbns` ON `isbns`.`book_id` = `id`
    GROUP BY `id`;





-- Create procedure to find books of the given genre
delimiter //
CREATE PROCEDURE `books_in_genre`(IN `genre_name` VARCHAR(13))
BEGIN
    SELECT * FROM `books_with_authors`
    WHERE `genre` = `genre_name`;
END//
delimiter ;

-- Create procedure to find books in the given age category
delimiter //
CREATE PROCEDURE `books_in_age_cat`(IN `category` VARCHAR(13))
BEGIN
    SELECT * FROM `books_with_authors`
    WHERE `age_category` = `category`;
END//
delimiter ;

-- Create procedure to find books written by the writer (given first_name, last_name)
delimiter //
CREATE PROCEDURE `books_written_by`(IN `first` VARCHAR(32), IN `last` VARCHAR(32))
BEGIN
    SELECT * FROM `books`
    WHERE `id` IN (
        SELECT DISTINCT `book_id` FROM `authored`
        JOIN `writers` ON `writers`.`id` = `authored`.`writer_id`
        WHERE `last_name` = `last` AND `first_name` = `first`
    );
END//
delimiter ;

-- Create procedure to find books desired by the user (given username)
delimiter //
CREATE PROCEDURE `books_desired_by`(IN `u_name` VARCHAR(32))
BEGIN
    SELECT get_userId(`u_name`) INTO @u_id;
    SELECT * FROM `books_with_authors`
    WHERE `id` IN (
        SELECT `book_id` FROM `desired`
        WHERE `user_id` = @u_id
    );
END//
delimiter ;

-- Create procedure to find books desired but never started by the user (given username)
delimiter //
CREATE PROCEDURE `books_desired_never_started_by`(IN `u_name` VARCHAR(32))
BEGIN
    SELECT get_userId(`u_name`) INTO @u_id;
    SELECT * FROM `books_with_authors`
    WHERE `id` IN (
        SELECT `book_id` FROM `desired`
        WHERE `user_id` = @u_id
        EXCEPT
        SELECT DISTINCT `book_id` FROM `reads`
        WHERE `user_id` = @u_id
    );
END//
delimiter ;

-- Create procedure to find books desired but never finished by the user (given username)
delimiter //
CREATE PROCEDURE `books_desired_never_finished_by`(IN `u_name` VARCHAR(32))
BEGIN
    SELECT get_userId(`u_name`) INTO @u_id;
    SELECT *, get_latter_started(`id`, @u_id) AS `latter_started` FROM `books_with_authors`
    WHERE `id` IN (
        SELECT `book_id` FROM `desired`
        WHERE `user_id` = @u_id
        EXCEPT
        SELECT DISTINCT `book_id` FROM `reads`
        WHERE `user_id` = @u_id
        AND `finished` != NULL
    );
END//
delimiter ;

-- Create procedure to find books started but never finished by the user
-- (given username)
delimiter //
CREATE PROCEDURE `books_started_never_finished_by`(IN `u_name` VARCHAR(32))
BEGIN
    SELECT get_userId(`u_name`) INTO @u_id;
    SELECT *, get_latter_started(`id`, @u_id) AS `latter_started` FROM `books_with_authors`
    WHERE `id` IN (
        SELECT DISTINCT `book_id` FROM `reads`
        WHERE `user_id` = @u_id
        AND `finished` = NULL
        EXCEPT
        SELECT DISTINCT `book_id` FROM `reads`
        WHERE `user_id` = @u_id
        AND `finished` != NULL
    );
END//
delimiter ;

-- Create procedure to find books ever finished by the user (given username)
delimiter //
CREATE PROCEDURE `books_ever_finished_by`(IN `u_name` VARCHAR(32))
BEGIN
    SELECT get_userId(`u_name`) INTO @u_id;
    SELECT * , get_latter_finished(`id`, @u_id) AS `latter_finished` FROM `books_with_authors`
    WHERE `id` IN (
        SELECT DISTINCT `book_id` FROM `reads`
        WHERE `user_id` = @u_id
        AND `finished` != NULL
    );
END//
delimiter ;

-- Create procedure to find books started (restarted) but not finished yet by the user
-- (given username)
delimiter //
CREATE PROCEDURE `books_started_notyet_finished_by`(IN `u_name` VARCHAR(32))
BEGIN
    SELECT get_userId(`u_name`) INTO @u_id;
    SELECT *, get_latter_started(`id`, @u_id) AS `latter_started`,
        get_latter_finished(`id`, @u_id) AS `latter_finished`
    FROM `books_with_authors`
    WHERE `id` IN (
        SELECT DISTINCT `book_id` FROM `reads`
        WHERE `user_id` = @u_id
        AND `finished` = NULL
    );
END//
delimiter ;

 -- Create procedure to find books with latter start for the user (given username)
 -- those not started are not included, those already finished are included
delimiter //
CREATE PROCEDURE `books_latter_started_by`(IN `u_name` VARCHAR(32))
BEGIN
    SELECT get_userId(`u_name`) INTO @u_id;
    SELECT `id`, `title`, `lang`, `orig_lang`, `genre`, `age_category`, `writer`,
        get_latter_started(`id`, @u_id) AS `latter_started`,
        get_latter_finished(`id`, @u_id) AS `latter_finished`
    FROM `books_with_authors` `b_a`
    JOIN `desired` ON `desired`.`book_id` = `b_a`.`id`
    WHERE `user_id` = @u_id
    GROUP BY `book_id`;
END//
delimiter ;

-- Create procedure to find all comments (with timestamps) ever left while reading book by the user
-- (given username, book_id)
delimiter //
CREATE PROCEDURE `comments_on_book`(IN `u_name` VARCHAR(32), IN `b_id` SMALLINT UNSIGNED)
BEGIN
    SELECT get_userId(`u_name`) INTO @u_id;
    SELECT `read_id`, `content`, `timestamp`
    FROM `comments`
    WHERE `read_id` IN (
        SELECT `id` FROM `reads`
        WHERE `user_id` = @u_id
        AND `book_id` = b_id
    )
    ORDER BY `read_id`, `timestamp`;
END//
delimiter ;

-- Create stored procedure to add new book along with adding it into authored
-- (given data for the book and writer's id)
delimiter //
CREATE PROCEDURE `add_new_book`(IN `t` VARCHAR(100), IN `orig_t` VARCHAR(100),
     `l` VARCHAR(2), `orig_l` VARCHAR(2), `g` VARCHAR(13),
     `a_cat` VARCHAR(13), `w_id` SMALLINT UNSIGNED)
BEGIN
    SELECT get_langId(`l`) INTO @l;
    SELECT get_langId(`orig_l`) INTO @orig_l;
    INSERT INTO `books`(`title`, `orig_title`, `lang`, `orig_lang`, `genre`, `age_category`)
    VALUES (`t`, `orig_t`, @l, @orig_l, `g`, `a_cat`);
    SELECT LAST_INSERT_ID() INTO @b_id;
    IF `w_id` IS NOT NULL THEN
        INSERT INTO `authored` (`book_id`, `writer_id`)
        VALUES (@b_id, `w_id`);
    END IF;
END//
delimiter ;

-- Create stored procedure to start reading a book
-- (given book_id, user_id, DATE)
delimiter //
CREATE PROCEDURE `start_reading`(IN `b_id` SMALLINT UNSIGNED, IN `u_name` VARCHAR(32), `d` DATE)
BEGIN
    SELECT get_userId(`u_name`) INTO @u_id;
    INSERT INTO `reads` (`book_id`, `user_id`, `started`)
    VALUES (b_id, @u_id, d);
END//
delimiter ;

-- Create stored procedure to finish reading a book:
-- update the latter reading attempt for the given book_id, username, DATE
delimiter //
CREATE PROCEDURE `finish_reading`(IN `b_id` SMALLINT UNSIGNED, IN `u_name` VARCHAR(32), `d` DATE)
BEGIN
    SELECT get_userId(`u_name`) INTO @u_id;
    SELECT get_latter_read(b_id, @u_id) INTO @read_id;
    UPDATE `reads` SET `finished` = d
    WHERE `id` = @read_id;
END//
delimiter ;

-- Create procedure to leave a comment for the latter started read of a book
-- (given user_id, book_id)
delimiter //
CREATE PROCEDURE `leave_comment`(IN `b_id` SMALLINT UNSIGNED, IN `u_name` VARCHAR(32), IN `comment` VARCHAR(3000))
BEGIN
    SELECT get_userId(`u_name`) INTO @u_id;
    SELECT get_latter_read(b_id, @u_id) INTO @r_id;
    INSERT INTO `comments` (`read_id`, `content`)
    VALUES (@r_id, `comment`);
END//
delimiter ;


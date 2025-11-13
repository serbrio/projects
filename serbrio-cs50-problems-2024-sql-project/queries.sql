-- In this SQL file, write (and comment!) the typical SQL queries users will run on your database

-- Find books of the given genre
SELECT * FROM books_with_authors
WHERE `genre` = 'biography';
-- It is possible to use stored procedure for this
CALL books_in_genre('biography');

-- Find books in the given age category
SELECT * FROM books_with_authors
WHERE `age_category` = 'adults';
-- It is possible to use stored procedure for this
CALL books_in_age_cat('adults');

-- Find books written by the writer (given first_name, last_name)
SELECT * FROM books
WHERE `id` IN (
    SELECT DISTINCT `book_id` FROM `authored`
    JOIN `writers` ON `writers`.`id` = `authored`.`writer_id`
    WHERE `last_name` = 'Pinker' AND `first_name` = 'Steven');
-- It is possible to use stored procedure for this
CALL books_written_by('Steven', 'Pinker');

-- Find books desired by the user (given username)
SELECT * FROM books_with_authors
WHERE `id` IN (
    SELECT `book_id` FROM `desired`
    WHERE `user_id` = get_userId('miamia')
);
-- It is possible to use stored procedure for this
CALL books_desired_by('miamia');

-- Find books desired but never started by the user (given username)
SELECT get_userId('bookworm') INTO @u_id;
SELECT * FROM books_with_authors
WHERE `id` IN (
    SELECT `book_id` FROM `desired`
    WHERE `user_id` = @u_id
    EXCEPT
    SELECT DISTINCT `book_id` FROM `reads`
    WHERE `user_id` = @u_id
);
-- It is possible to use stored procedure for this
CALL books_desired_never_started_by('bookworm');

-- Find books started but never finished by the user
-- (given username)
SELECT get_userId('bookworm') INTO @u_id;
SELECT *, get_latter_started(`id`, @u_id) AS `latter_started`
FROM books_with_authors
WHERE `id` IN (
    SELECT DISTINCT `book_id` FROM `reads`
    WHERE `user_id` = @u_id
    AND `finished` = NULL
    EXCEPT
    SELECT DISTINCT `book_id` FROM `reads`
    WHERE `user_id` = @u_id
    AND `finished` != NULL
);
-- It is possible to use stored procedure for this
CALL books_started_never_finished_by('bookworm');

-- Find books ever finished by the user (given username)
SELECT get_userId('enigma') INTO @u_id;
SELECT * , get_latter_finished(`id`, @u_id) AS `latter_finished`
FROM books_with_authors
WHERE `id` IN (
    SELECT DISTINCT `book_id` FROM `reads`
    WHERE `user_id` = @u_id
    AND `finished` != NULL
);
-- It is possible to use stored procedure for this
CALL books_ever_finished_by('enigma');

-- Find books started (restarted) but not finished yet by the user
-- (given username)
SELECT get_userId('benvenuto') INTO @u_id;
SELECT *, get_latter_started(`id`, @u_id) AS `latter_started`,
    get_latter_finished(`id`, @u_id) AS `latter_finished`
FROM books_with_authors
WHERE `id` IN (
    SELECT DISTINCT `book_id` FROM `reads`
    WHERE `user_id` = @u_id
    AND `finished` = NULL
);
-- It is possible to use stored procedure for this
CALL books_started_notyet_finished_by('benvenuto');

-- Find all comments (with timestamps) ever left while reading the book by the user
-- (given username, book_id)
-- Find book_id by title and writers first and last name
SELECT get_bookId('Enlightenment Now', 'Steven', 'Pinker') INTO @b_id;
-- Find user_id by username
SELECT get_userId('miamia') INTO @u_id;
--
SELECT `read_id`, `content`, `timestamp`
FROM `comments`
WHERE `read_id` IN (
    SELECT `id` FROM `reads`
    WHERE `user_id` = @u_id
    AND `book_id` = @b_id
)
ORDER BY `read_id`, `timestamp`;
-- It is possible to use stored procedure for this
CALL comments_on_book('miamia', @b_id);


-- Below are actions to be shown in the presentation of the project,
-- including those, commented out.

-- Add new writers
INSERT INTO `writers` (`first_name`, `last_name`, `born`)
VALUES
('Steven', 'Pinker', 1954),
('Daniel', 'Kahneman', 1934);

-- Add new books
CALL add_new_book('Enlightenment Now', 'Enlightenment Now', 'en', 'en', 'non-fiction', 'adults',
    get_writerId('Steven', 'Pinker'));
CALL add_new_book('Rationality', 'Rationality', 'en', 'en', 'non-fiction', 'adults',
    get_writerId('Steven', 'Pinker'));
CALL add_new_book('The Blank Slate', 'The Blank slate', 'en', 'en', 'non-fiction', 'adults',
    get_writerId('Steven', 'Pinker'));
CALL add_new_book('Thinking, Fast and Slow', 'Thinking, Fast and Slow', 'en', 'en', 'non-fiction', 'adults',
    get_writerId('Daniel', 'Kahneman'));

-- CALL books_written_by('Steven', 'Pinker');

-- Add new users
INSERT INTO `users` (`first_name`, `last_name`, `username`, `born`)
VALUES
('Mia', 'Miassini', 'miamia', 1990),
('Jorge', 'Borges', 'bookworm', 1901),
('Sam', 'Cellini', 'benvenuto', 1959),
('Mira', 'Donowitz', 'donner', 2016);

-- Add to desired new pair: a user desires a book
INSERT INTO `desired` (`book_id`, `user_id`) VALUES
       (get_bookId('Enlightenment Now', 'Steven', 'Pinker'), get_userId('miamia')),
       (get_bookId('Thinking, Fast and Slow', 'Daniel', 'Kahneman'), get_userId('bookworm')),
       (get_bookId('Rationality', 'Steven', 'Pinker'), get_userId('bookworm')),
       (get_bookId('The Blank Slate', 'Steven', 'Pinker'), get_userId('bookworm')),
       (get_bookId('Rationality', 'Steven', 'Pinker'), get_userId('benvenuto'));

-- CALL books_desired_by('bookworm');

-- Add new read (a user started reading a book)
CALL start_reading(get_bookId('Rationality', 'Steven', 'Pinker'), 'bookworm', CURDATE() - INTERVAL 100 DAY);
CALL start_reading(get_bookId('Thinking, Fast and Slow', 'Daniel', 'Kahneman'), 'bookworm', CURDATE() - INTERVAL 99 DAY);
CALL start_reading(get_bookId('Rationality', 'Steven', 'Pinker'), 'donner', CURDATE() - INTERVAL 1 DAY);
CALL start_reading(get_bookId('Rationality', 'Steven', 'Pinker'), 'benvenuto', CURDATE() - INTERVAL 3 DAY);
CALL start_reading(get_bookId('Rationality', 'Steven', 'Pinker'), 'bookworm', CURDATE() - INTERVAL 2 DAY);

-- Add new comment (a user leaves comment while reading a book)
CALL leave_comment(get_bookId('Rationality', 'Steven', 'Pinker'), 'bookworm',
    'Great book! I would recommend it to anybody, who wants to learn, how rational people are.');

-- Update read (a user finished reading a book)
CALL finish_reading(get_bookId('Rationality', 'Steven', 'Pinker'), 'bookworm', CURDATE());

-- CALL books_ever_finished_by('bookworm');
-- CALL books_desired_never_started_by('bookworm');

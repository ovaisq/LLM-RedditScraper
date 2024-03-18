--all subreddits an author has posted to or commented in
SELECT post_author, subreddit
FROM (
    SELECT post_author, subreddit
    FROM posts
    UNION
    SELECT comment_author as author_id, subreddit
    FROM comments
) AS subreddits_by_author
ORDER BY post_author, subreddit;
--all posts and comments from the author
SELECT
    posts.post_id AS post_id,
    posts.post_title AS post_title,
    posts.post_body AS post_body,
    posts.post_created_utc AS post_created_utc,
    posts.post_author AS post_author,
    comments.comment_author AS comment_author,
    comments.comment_id AS comment_id,
    comments.comment_body AS comment_body,
    comments.comment_created_utc AS comment_created_utc
FROM
    posts
JOIN
    comments ON posts.post_author = comments.comment_author
WHERE
    posts.post_author = comments.comment_author
    and posts.post_body NOT IN ('[removed]', '');

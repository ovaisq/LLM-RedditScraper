--all subreddits an author has posted to or commented in
SELECT post_author, subreddit
FROM (
    SELECT post_author, subreddit
    FROM post
    UNION
    SELECT comment_author as author_id, subreddit
    FROM comment
) AS subreddits_by_author
ORDER BY post_author, subreddit;
--all posts and comments from the author
SELECT
    post.post_id AS post_id,
    post.post_title AS post_title,
    post.post_body AS post_body,
    post.post_created_utc AS post_created_utc,
    post.post_author AS post_author,
    comment.comment_author AS comment_author,
    comment.comment_id AS comment_id,
    comment.comment_body AS comment_body,
    comment.comment_created_utc AS comment_created_utc
FROM
    post
JOIN
    comment ON post.post_author = comment.comment_author
WHERE
    post.post_author = comment.comment_author
    and post.post_body NOT IN ('[removed]', '');

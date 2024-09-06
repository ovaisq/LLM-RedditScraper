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
--AVG Prompt Completion Time Per Model
SELECT model AS model,
       AVG(avg_completion_time) AS "AVG(avg_completion_time)"
FROM
  (SELECT model,
          AVG(prompt_completion_time) AS avg_completion_time
   FROM prompt_completion_details pcd
   GROUP BY model) AS virtual_table
GROUP BY model
ORDER BY "AVG(avg_completion_time)" DESC
LIMIT 10000;
--Total Successful Prompt Completions Per Day
SELECT DATE_TRUNC('day', date) AS date,
       sum(num_analysis_documents) AS "SUM(num_analysis_documents)"
FROM
  (SELECT DATE(timestamp) AS date,
          COUNT(*) as num_analysis_documents
   FROM analysis_documents ad
   WHERE analysis_document IS NOT NULL
   GROUP BY DATE
   order by date) AS virtual_table
WHERE date >= TO_DATE('2024-08-22', 'YYYY-MM-DD')
  AND date < TO_DATE('2024-09-07', 'YYYY-MM-DD')
GROUP BY DATE_TRUNC('day', date)
ORDER BY "SUM(num_analysis_documents)" DESC
LIMIT 50000;
--Reddit Scraper Table Row Counts
SELECT table_name AS table_name,
                     rows_n AS rows_n
FROM
  (WITH tbl AS
     (SELECT table_schema,
             table_name
      FROM information_schema.tables
      WHERE table_name NOT LIKE 'pg_%'
        AND table_schema IN ('public') ) SELECT table_name,
                                                (xpath('/row/c/text()', query_to_xml(format('SELECT count(*) AS c FROM %I.%I', table_schema, table_name), false, true, '')))[1]::text::int AS rows_n
   FROM tbl
   ORDER BY 2 DESC) AS virtual_table
WHERE table_name != 'parent_child_tree_data'
  AND table_name != 'websearch_results_ts'
LIMIT 1000;
--Top 10 Posts by Upvote Count of all Subreddits in the database
SELECT post_title AS post_title,
       post_upvote_count AS post_upvote_count,
       subreddit AS subreddit
FROM
  (select post_title,
          post_upvote_count,
          subreddit
   from posts
   where post_upvote_count > 100
   order by post_upvote_count desc
   limit 10) AS virtual_table
ORDER BY post_upvote_count DESC
LIMIT 1000;
--Most Recent 10 Posrts per Subreddit
SELECT subreddit AS subreddit,
       top_ten_posts AS top_ten_posts,
       max_post_upvote_count AS max_post_upvote_count
FROM
  (SELECT subreddit AS subreddit,
          top_ten_posts AS top_ten_posts,
          max_post_upvote_count AS max_post_upvote_count
   FROM
     (WITH top_posts AS
        (SELECT subreddit,
                post_title,
                post_upvote_count,
                post_id,
                ROW_NUMBER() OVER (PARTITION BY subreddit
                                   ORDER BY post_id DESC) as rank
         FROM public.posts
         WHERE post_title not in ('[deleted by user]',
                                  '[deleted]')
           AND subreddit in ('democrats',
                             'Republican',
                             'Libertarian') ) SELECT subreddit,
                                                     post_title AS top_ten_posts,
                                                     post_upvote_count AS max_post_upvote_count
      FROM top_posts
      WHERE rank <= 10
      ORDER BY subreddit,
               post_upvote_count DESC) AS virtual_table
   GROUP BY subreddit,
            top_ten_posts,
            max_post_upvote_count
   order by subreddit,
            max_post_upvote_count desc) AS virtual_table
LIMIT 1000;

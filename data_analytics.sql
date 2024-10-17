--Queries for Apache Superset Dashboard
--©2024, Ovais Quraishi
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
   GROUP BY model, id
   ORDER BY id DESC) AS virtual_table
GROUP BY model
ORDER BY "AVG(avg_completion_time)" DESC;
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
--Average Successful Prompt Completion time per model per Ollama Release
SELECT ollama_ver::semver, model AS model,
       AVG(avg_completion_time) AS "AVG(avg_completion_time)"
FROM
  (SELECT ollama_ver::semver, model,
          AVG(prompt_completion_time) AS avg_completion_time
   FROM prompt_completion_details pcd
   where ollama_ver != 'false'
   GROUP BY ollama_ver::semver, model, id order by id desc) AS virtual_table
GROUP BY ollama_ver::semver, model
ORDER BY ollama_ver::semver, model, "AVG(avg_completion_time)" desc;
--Average Tokens Per Second Per Model
SELECT model AS model,
       AVG("AVG(avg_tokens_per_second)") AS "AVG(AVG(avg_tokens_per_second))"
FROM
  (SELECT model AS model,
          AVG(avg_tokens_per_second) AS "AVG(avg_tokens_per_second)"
   FROM
     (SELECT model,
             AVG(tokens_per_second) AS avg_tokens_per_second
      FROM prompt_completion_details pcd
      WHERE ollama_ver NOT IN ('false',
                               '0.3.10-rc1')
			AND tokens_per_second IS NOT NULL
      GROUP BY model,
               id
      ORDER BY id DESC) AS virtual_table
   GROUP BY model
   ORDER BY "AVG(avg_tokens_per_second)" DESC
   LIMIT 10000) AS virtual_table
GROUP BY model
ORDER BY "AVG(AVG(avg_tokens_per_second))" DESC
LIMIT 10000;

--Number of remaining comments and posts to be analyzed by LLMs
WITH filtered_comments AS (
    SELECT comment_id
    FROM comments
    WHERE comment_body NOT IN ('', '[removed]', '[deleted]')
),
filtered_posts AS (
    SELECT post_id
    FROM posts
    WHERE post_body NOT IN ('', '[removed]', '[deleted]')
)
SELECT 'comments' AS label, COUNT(c.comment_id) AS count
FROM filtered_comments c
LEFT JOIN analysis_documents ad
ON (ad.analysis_document ->> 'comment_id' = c.comment_id OR ad.analysis_document ->> 'reference_id' = c.comment_id)
WHERE ad.analysis_document IS NULL

UNION ALL

SELECT 'posts' AS label, COUNT(p.post_id) AS count
FROM filtered_posts p
WHERE NOT EXISTS (
        SELECT 1
        FROM analysis_documents
        WHERE analysis_document ->> 'post_id' = p.post_id
            AND analysis_document ->> 'post_id' IS NOT NULL
    )
AND NOT EXISTS (
        SELECT 1
        FROM analysis_documents
        WHERE analysis_document ->> 'reference_id' = p.post_id
            AND analysis_document ->> 'reference_id' IS NOT NULL
    );

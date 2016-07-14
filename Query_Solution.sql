######################Queries for the ACM dataset######################

1. Collaborative community: Find the communities that consist of authors who collaborate 
with each other to publish articles together.  (S_a1 AUTHOR <-> COAUTHORSHIP)

About 1 sec
CREATE UNGRAPH coauthorship AS
(
	SELECT w1.Aid AS Aid, w2.Aid AS CoAid
	FROM WRITES AS w1, WRITES AS w2
	WHERE w1.Pid = w2.Pid AND w1.Aid != w2.Aid
);

About 2 sec
SELECT ClusterID, Size, Members 
FROM CLUSTER(coauthorship, MC)
ORDER BY Size DESC; 


3. Influence of article

About 1 sec
CREATE DIGRAPH citation AS
(
	SELECT Pid, CitedPid FROM CITES
);


About 1 sec
SELECT VertexID, Value
FROM RANK(citation, pagerank);


4. Top 3 Influential article: Find the top 3 influential article together with the authors of the article. (S_a2 ARTICLE <-> CITATION)

About 2 sec
SELECT Aid, Pid FROM WRITES
WHERE Pid in 
(
	SELECT VertexID
	FROM RANK(citation, pagerank)
	LIMIT 3
);


5. Find the shortest path between author Doug Burger and author David Mount

About 1 sec
SELECT *
FROM PATH(coauthorship, V1//V2)
WHERE V1 AS
( SELECT Aid FROM AUTHOR where Fname = 'Doug' and Lname = 'Burger')
AND V2 AS
( SELECT Aid FROM AUTHOR where Fname = 'David' and Lname = 'Mount')
ORDER BY Length ASC LIMIT 10;


######################Queries for the ACM dataset######################

######################Queries for the StackOverflow dataset######################
1. Python user: Users who have replied to questions that are labelled by "Python" tag

About 40 Sec
SELECT Owner_id FROM ANSWER
WHERE Parent_Qid IN
(
	SELECT Qid FROM LABELLED_BY
	WHERE Tid IN
	(
		SELECT Tid FROM TAG
		WHERE Tag_label = 'python'
	)
);


2. Influence of users (S_s1 USER <-> GETTING ANSWER)

About 40 Sec
CREATE DIGRAPH getting_answer AS
(
	SELECT q.Owner_id AS Q_User, a.Owner_id AS A_User
	FROM QUESTION as q, ANSWER as a
	WHERE q.Accepted_Aid = a.Aid AND q.Owner_id != a.Owner_id
)

About 102 Sec
SELECT VertexID, Value
FROM RANK(getting_answer, pagerank);


3.Python experts (Top k): Top 10 users who often reply python questions and their answers 
are often accepted.  (S_s1 USER <-> GETTING ANSWER)

About 75 Sec
SELECT VertexID, Value
FROM RANK(getting_answer, pagerank)
WHERE VertexID IN
(
	SELECT Owner_id FROM ANSWER
	WHERE Parent_Qid IN
	(
		SELECT Qid FROM LABELLED_BY
		WHERE Tid IN
		(
			SELECT Tid FROM TAG
			WHERE Tag_label = 'python'
		)
	)
)
LIMIT 10;


4.Biggest community of correlation users: Find the biggest community of users 
who often reply same questions (they may have common interest)
(S_s2 USER <-> User Correlation)

About 40 Sec
CREATE UNGRAPH user_correlation AS
(
	SELECT a1.Owner_id AS User, a2.Owner_id AS R_User
	FROM ANSWER AS a1, ANSWER AS a2
	WHERE a1.Parent_Qid = a2.Parent_Qid AND a1.Owner_id != a2.Owner_id
);

Overnight About 9 hours (28,501,214 records)
SELECT ClusterID, Size, Members 
FROM CLUSTER(user_correlation, MC)
ORDER BY Size DESC
LIMIT 1; 

5.Competitive users: users who are in the biggest community of correlative users and 
they also have big influence in the community (one of their answers may be accepted).
(S_s1 USER <-> GETTING ANSWER) AND (S_s2 USER <-> User Correlation)

Overnight About 9 hours (28,501,214 records)
SELECT r.VertexID
FROM RANK(getting_answer, pagerank) AS r,
(
	SELECT Members 
	FROM CLUSTER(user_correlation, MC)
	ORDER BY Size DESC
	LIMIT 1
) AS c
WHERE r.VertexID = ANY(c.Members);


6. Related Question:Find the correlation groups of questions which often use same tags
(S_s3 QUESTION <-> QUESTION CORRELATION)

About 3 sec
CREATE UNGRAPH question_correlation AS
(
	SELECT l1.Qid AS Qid, l2.Qid AS R_Qid
	FROM LABELLED_BY AS l1, LABELLED_BY AS l2
	WHERE l1.Tid = l2.Tid AND l1.Qid != l2.Qid
	limit 100000
);

About 241 sec
SELECT ClusterID, Size, Members 
FROM CLUSTER(question_correlation, MC)
ORDER BY Size DESC;


7. Related Tag:Find the correlation groups of tags which are often used on 
same questions (S_s4 TAG <-> TAG CORRELATION)

About 13 sec
CREATE UNGRAPH tag_correlation AS
(
	SELECT l1.Tid AS Tid, l2.Tid AS R_Tid
	FROM LABELLED_BY AS l1, LABELLED_BY AS l2
	WHERE l1.Qid = l2.Qid AND l1.Tid != l2.Tid
	limit 100000
);

About 60 sec
SELECT ClusterID, Size, Members 
FROM CLUSTER(tag_correlation, MC)
ORDER BY Size DESC;

######################Queries for the StackOverflow dataset######################

######################Queries for the Twitter dataset######################

1.Popularity of user (S_t1 USER <-> FOLLOWING)

About 8 sec
CREATE DIGRAPH following AS
(
	SELECT Uid, Follower_ID FROM FOLLOW
	LIMIT 10000000
);

About 150 sec
SELECT VertexID, Value
FROM RANK(following, pagerank);


2.Users mentioned in tweets about iPhone

About 1 sec
SELECT Uid FROM MENTIONED_IN
WHERE TWid IN
(
	SELECT TWid FROM LABELLED_BY
	WHERE Tid IN
	(
		SELECT Tid FROM TAG
		WHERE Tag_Label = 'iPhone'
	)
);


3.Popular Users mentioned in tweets about iPhone
(S_t1 USER <-> FOLLOWING)

About 88 sec
SELECT VertexID, Value
FROM RANK(following, pagerank)
WHERE VertexID IN
(
	SELECT Uid FROM MENTIONED_IN
	WHERE TWid IN
	(
		SELECT TWid FROM LABELLED_BY
		WHERE Tid IN
		(
			SELECT Tid FROM TAG
			WHERE Tag_Label = 'iPhone'
		)
	)
)
LIMIT 10;


4.Related users: users who are often mentioned in same tweets
(S_t2 USER <-> USER CORRELATION)

About 4 sec
CREATE UNGRAPH user_correlation AS
(
	SELECT m1.Uid AS Uid, m2.Uid AS R_Uid
	FROM MENTIONED_IN AS m1, MENTIONED_IN AS m2
	WHERE m1.TWid = m2.TWid AND m1.Uid != m2.Uid
)

About 4 hours (1689146 records)
SELECT ClusterID, Size, Members 
FROM CLUSTER(user_correlation, MC)
ORDER BY Size DESC;


5.Related tags: tags that are often used in same tweets
(S_t4 TAG <-> TAG CORRELATION)

About 1 Sec
CREATE UNGRAPH tag_correlation AS
(
	SELECT l1.Tid AS Tid, l2.Tid AS R_Tid
	FROM LABELLED_BY AS l1, LABELLED_BY AS l2
	WHERE l1.TWid = l2.TWid AND l1.Tid != l2.Tid
	limit 100000
);

About 58 Sec
SELECT ClusterID, Size, Members 
FROM CLUSTER(tag_correlation, MC)
ORDER BY Size DESC;


6. Find the shortest path between user mac and user Starbucks

About 160 Sec
SELECT *
FROM PATH(following, V1//V2)
WHERE V1 AS
( SELECT uid FROM TWEET_USER where display_name = 'mac')
AND V2 AS
( SELECT uid FROM TWEET_USER where display_name = 'Starbucks')
ORDER BY Length ASC LIMIT 10;

######################Queries for the Twitter dataset######################

1. Python user: Users who have replied to questions that are labelled by "Python" tag

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

CREATE DIGRAPH getting_answer AS
(
	SELECT q.Owner_id AS Q_User, a.Owner_id AS A_User
	FROM QUESTION as q, ANSWER as a
	WHERE q.Accepted_Aid = a.Aid AND q.Owner_id != a.Owner_id
);

SELECT VertexID, Value
FROM RANK(getting_answer, pagerank);



3.Python experts (Top k): Top 10 users who often reply python questions and their answers 
are often accepted.  (S_s1 USER <-> GETTING ANSWER)

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

CREATE UNGRAPH user_correlation AS
(
	SELECT a1.Owner_id AS User, a2.Owner_id AS R_User
	FROM ANSWER AS a1, ANSWER AS a2
	WHERE a1.Parent_Qid = a2.Parent_Qid AND a1.Owner_id != a2.Owner_id
	LIMIT 1000
);

SELECT ClusterID, Size, Members 
FROM CLUSTER(user_correlation, GN)
ORDER BY Size DESC
LIMIT 1; 


5.Competitive users: users who are in the biggest community of correlative users and 
they also have big influence in the community (one of their answers may be accepted).
(S_s1 USER <-> GETTING ANSWER) AND (S_s2 USER <-> User Correlation)

SELECT r.VertexID
FROM RANK(getting_answer, pagerank) AS r,
(
	SELECT Members 
	FROM CLUSTER(user_correlation, CNM)
	ORDER BY Size DESC
	LIMIT 1
) AS c
WHERE r.VertexID = ANY(c.Members);


6. Related Question:Find the correlation groups of questions which often use same tags
(S_s3 QUESTION <-> QUESTION CORRELATION)

CREATE UNGRAPH question_correlation AS
(
	SELECT l1.Qid AS Qid, l2.Qid AS R_Qid
	FROM LABELLED_BY AS l1, LABELLED_BY AS l2
	WHERE l1.Tid = l2.Tid AND l1.Qid != l2.Qid
	LIMIT 1000
);

SELECT ClusterID, Size, Members 
FROM CLUSTER(question_correlation, CNM)
ORDER BY Size DESC;


7. Related Tag:Find the correlation groups of tags which are often used on 
same questions (S_s4 TAG <-> TAG CORRELATION)

CREATE UNGRAPH tag_correlation AS
(
	SELECT l1.Tid AS Tid, l2.Tid AS R_Tid
	FROM LABELLED_BY AS l1, LABELLED_BY AS l2
	WHERE l1.Qid = l2.Qid AND l1.Tid != l2.Tid
	LIMIT 1000
);

SELECT ClusterID, Size, Members 
FROM CLUSTER(tag_correlation, MC) 
ORDER BY Size DESC;


8. Finding Path: see how the 'c++' tag connects with the 'html' tag

SELECT * FROM PATH(tag_correlation, V1//V2)
WHERE V1 AS
(SELECT Tid FROM TAG WHERE Tag_Label = 'c++')
AND V2 AS
(SELECT Tid FROM TAG WHERE Tag_Label = 'html')
ORDER BY Length;

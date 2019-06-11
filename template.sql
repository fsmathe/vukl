-- TODO: CREATE VIEW, CREATE TRIGGER

-- questions given on the sheets
CREATE TABLE IF NOT EXISTS 'questions' (
	'id' INTEGER PRIMARY KEY,
	'question_type' TEXT, -- question type, eg. single or open
	'positive', -- index of choice considered positive
	'range' INTEGER -- number of different choices
);

CREATE TABLE IF NOT EXISTS 'question_texts' (
	'question' INTEGER REFERENCES questions,
	'lang' TEXT, -- language code
	'text' TEXT, -- the question as given on the evaluation sheets (up to typography)
	'original' TEXT, -- the question as given on the evaluation sheets
	'left' TEXT, -- text corresponding to smallest choice
	'right' TEXT, -- text corresponding to largest choice
	PRIMARY KEY ("question","lang")
);

-- choices for single and multiple choice questions
/* To get the question texts together with
	the texts of the possible answers one could use
SELECT questions.text, choices.text
FROM questions JOIN choices
	ON questions.id=choices.question
*/
CREATE TABLE IF NOT EXISTS 'choices' (
	'question' INTEGER REFERENCES questions,
	'choice' INTEGER,
	'lang' TEXT,
	'text',
	PRIMARY KEY ("question","choice","lang")
);

-- order in which the questions appear on the different forms
CREATE TABLE IF NOT EXISTS 'form_structure' (
	'form' TEXT,
	'position' INTEGER,
	'question' INTEGER REFERENCES questions,
	'multiple' INTEGER,
	PRIMARY KEY ("form","position")
);

-- evaluated courses
CREATE TABLE IF NOT EXISTS 'courses' (
	'id' INTEGER PRIMARY KEY,
	'Kennung',
	'Teilbereich',
	'Anrede',
	'Titel',
	'Vorname',
	'Nachname',
	'Lehrveranstaltung',
	'Periode'
);

-- the evaluations done in a course
CREATE TABLE IF NOT EXISTS 'evaluations' (
	'course' TEXT REFERENCES courses,
	'form' TEXT
);

-- answers given in the evaluations
/* To get the question texts together with the given answers one could use
SELECT questions.text, answers.text
FROM questions JOIN answers
	ON questions.id=answers.question

 * To get the answers in text form for all questions
	including multiple choice one could use
SELECT coalesce(choices.text, answers.text)
FROM answers LEFT JOIN choices USING (question,text)
 * ("course","question","form","sheet") is unique unless
	"question" is a multiple choice question.
 * If "question" is single/multiple choice, 
	then "text"="choices"."choice" AND "question"="choices"."question" should
	be satisfied for exactly one entry of "choices" per language.
*/
CREATE TABLE IF NOT EXISTS 'answers' (
	'course' INTEGER REFERENCES courses,
	'form',
	'sheet',
	'question' INTEGER REFERENCES questions,
	'value'
);

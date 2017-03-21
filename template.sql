-- questions given on the sheets
CREATE TABLE questions (
	'id' INTEGER PRIMARY KEY,
	'type' TEXT, -- question type, eg. single or open
	'text_de' TEXT NOT NULL, -- the question as given on the evaluation sheets (up to typography)
	'text_en' TEXT NOT NULL,
	'original_de' TEXT NOT NULL, -- the question as given on the evaluation sheets
	'original_en' TEXT NOT NULL,
	'polLeft_de' TEXT, -- text corresponding to smallest choice
	'polLeft_en' TEXT,
	'polRight_de' TEXT, -- text corresponding to largest choice
	'polRight_en' TEXT,
	'positive', -- index of choice considered positive
	'range' INTEGER -- number of different choices
);

-- choices for single and multiple choice questions
/* to get the question texts together with
 * the texts of the possible answers one could use
	SELECT questions.text, choices.text
	FROM questions JOIN choices
		ON questions.id=choices.question
*/
CREATE TABLE choices (
	'question' INTEGER REFERENCES questions,
	'choice',
	'text',
	PRIMARY KEY ('question','choice')
);

-- order in which the questions appear on the different sheets
CREATE TABLE sheetstructure (
	'type' TEXT,
	'number' INTEGER,
	'question' INTEGER REFERENCES questions,
	PRIMARY KEY ('type','number')
);

-- evaluated courses
CREATE TABLE courses (
	id TEXT PRIMARY KEY, -- Kennung
	'Teilbereich',
	'Anrede',
	'Titel',
	'Vorname',
	'Nachname',
	'Lehrveranstaltung',
	'Lehrveranstaltung_en', -- has to be given by hand
	--'RaumTermin', -- not set
	--'Subdozent', -- not set
	'Periode'
	--'Studiengang', -- not set
	--'Vertiefungsgebiet', -- ???
);

-- the evaluations done in a course
CREATE TABLE evaluations (
	'course' TEXT REFERENCES courses,
	'type' TEXT
);

-- answers given in the evaluations
/* to get the question texts together with
 * the given answers one could use
	SELECT questions.text, answers.text
	FROM questions JOIN answers
		ON questions.id=answers.question

 * to get the answers in text form for all questions
 * including multiple choice one could use
	SELECT coalesce(choices.text, answers.text)
	FROM answers LEFT JOIN choices USING (question,text)
*/
CREATE TABLE answers (
	'course' TEXT REFERENCES courses,
	'question' INTEGER REFERENCES questions,
	'Bogen',
	'text',
	PRIMARY KEY ('course','question','Bogen')
	-- if answers.question=choices.question holds at least once,
	-- then also answers.text=choices.choice must hold at least once.
);

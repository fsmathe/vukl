CREATE VIEW IF NOT EXISTS 'choices_de_en' AS
	SELECT "question","choice",
		"c_de"."text" AS 'text_de',"c_en"."text" AS 'text_en'
	FROM "choices" AS 'c_de' JOIN "choices" AS 'c_en'
		USING("question","choice")
	WHERE "c_de"."lang"='de' AND "c_en"."lang"='en';

CREATE VIEW IF NOT EXISTS 'question_meta' (
	'id', 'key', 'Q_de', 'Q_en', 'Type',
	'PolLeft_de', 'PolRight_de', 'PolLeft_en', 'PolRight_en',
	'Single_de_1', 'Single_en_1', 'Single_de_2', 'Single_en_2',
	'Single_de_3', 'Single_en_3', 'Single_de_4', 'Single_en_4',
	'Single_de_5', 'Single_en_5', 'Single_de_6', 'Single_en_6',
	'Single_de_7', 'Single_en_7', 'Single_de_8', 'Single_en_8',
	'Single_de_9', 'Single_en_9', 'Single_de_10','Single_en_10',
	'Single_de_11','Single_en_11','Single_de_12','Single_en_12'
) AS SELECT
	"questions"."id",
	"form_structure"."form"||'_'||"form_structure"."position",
	"question_de"."text", "question_en"."text", NULL,
	"question_de"."left", "question_de"."right",
	"question_en"."left", "question_en"."right",
	 "c1"."text_de", "c1"."text_en", "c2"."text_de", "c2"."text_en",
	 "c3"."text_de", "c3"."text_en", "c4"."text_de", "c4"."text_en",
	 "c5"."text_de", "c5"."text_en", "c6"."text_de", "c6"."text_en",
	 "c7"."text_de", "c7"."text_de", "c8"."text_en", "c8"."text_en",
	 "c9"."text_de", "c9"."text_en","c10"."text_de","c10"."text_en",
	"c11"."text_de","c11"."text_en","c12"."text_de","c12"."text_en"
FROM "questions"
	JOIN "question_texts" AS 'question_de'
		ON "question_de"."question"="questions"."id"
		AND "question_de"."lang"='de'
	JOIN "question_texts" AS 'question_en'
		ON "question_en"."question"="questions"."id"
		AND "question_en"."lang"='en'
	JOIN "form_structure" ON "form_structure"."question"="questions"."id"
	LEFT JOIN "choices_de_en" AS 'c1'  ON  "c1"."question"="questions"."id" AND  "c1"."choice"= 1
	LEFT JOIN "choices_de_en" AS 'c2'  ON  "c2"."question"="questions"."id" AND  "c2"."choice"= 2
	LEFT JOIN "choices_de_en" AS 'c3'  ON  "c3"."question"="questions"."id" AND  "c3"."choice"= 3
	LEFT JOIN "choices_de_en" AS 'c4'  ON  "c4"."question"="questions"."id" AND  "c4"."choice"= 4
	LEFT JOIN "choices_de_en" AS 'c5'  ON  "c5"."question"="questions"."id" AND  "c5"."choice"= 5
	LEFT JOIN "choices_de_en" AS 'c6'  ON  "c6"."question"="questions"."id" AND  "c6"."choice"= 6
	LEFT JOIN "choices_de_en" AS 'c7'  ON  "c7"."question"="questions"."id" AND  "c7"."choice"= 7
	LEFT JOIN "choices_de_en" AS 'c8'  ON  "c8"."question"="questions"."id" AND  "c8"."choice"= 8
	LEFT JOIN "choices_de_en" AS 'c9'  ON  "c9"."question"="questions"."id" AND  "c9"."choice"= 9
	LEFT JOIN "choices_de_en" AS 'c10' ON "c10"."question"="questions"."id" AND "c10"."choice"=10
	LEFT JOIN "choices_de_en" AS 'c11' ON "c11"."question"="questions"."id" AND "c11"."choice"=11
	LEFT JOIN "choices_de_en" AS 'c12' ON "c12"."question"="questions"."id" AND "c12"."choice"=12
ORDER BY "form_structure"."form","form_structure"."position";

CREATE VIEW IF NOT EXISTS 'meta' (
	'ID', 'Q_de', 'Q_en', 'DataType', 'Type',
	'PolLeft_de', 'PolRight_de', 'PolLeft_en', 'PolRight_en',
	'Positive', 'Neutral', 'Range',
	'Single_de_1', 'Single_en_1', 'Single_de_2', 'Single_en_2',
	'Single_de_3', 'Single_en_3', 'Single_de_4', 'Single_en_4',
	'Single_de_5', 'Single_en_5', 'Single_de_6', 'Single_en_6',
	'Single_de_7', 'Single_en_7', 'Single_de_8', 'Single_en_8',
	'Single_de_9', 'Single_en_9', 'Single_de_10','Single_en_10',
	'Single_de_11','Single_en_11','Single_de_12','Single_en_12'
) AS SELECT
	"m"."key", "m"."Q_de", "m"."Q_en", NULL, "m"."Type",
	"m"."PolLeft_de", "m"."PolRight_de", "m"."PolLeft_en", "m"."PolRight_en",
	"questions"."positive", NULL, "questions"."range",
	"m"."Single_de_1", "m"."Single_en_1", "m"."Single_de_2", "m"."Single_en_2",
	"m"."Single_de_3", "m"."Single_en_3", "m"."Single_de_4", "m"."Single_en_4",
	"m"."Single_de_5", "m"."Single_en_5", "m"."Single_de_6", "m"."Single_en_6",
	"m"."Single_de_7", "m"."Single_en_7", "m"."Single_de_8", "m"."Single_en_8",
	"m"."Single_de_9", "m"."Single_en_9", "m"."Single_de_10","m"."Single_en_10",
	"m"."Single_de_11","m"."Single_en_11","m"."Single_de_12","m"."Single_en_12"
FROM "questions" JOIN "question_meta" AS 'm' USING("id")
ORDER BY "m"."key";

CREATE TRIGGER IF NOT EXISTS 'insert_choices_de_en'
	INSTEAD OF INSERT ON "choices_de_en"
	WHEN NEW."text_de" NOTNULL AND NEW."text_de"!=''
	BEGIN
		INSERT INTO "choices"("question","choice","lang","text") VALUES(NEW."question", NEW."choice",'de',NEW."text_de");
		INSERT INTO "choices"("question","choice","lang","text") VALUES(NEW."question", NEW."choice",'en',NEW."text_en");
	END;

CREATE TRIGGER IF NOT EXISTS 'insert_question_meta'
	INSTEAD OF INSERT ON "question_meta"
	BEGIN
		INSERT INTO "form_structure"
			("form","position","question","multiple")
			VALUES(substr(NEW."key",1,instr(NEW."key",'_')-1),
				substr(NEW."key",instr(NEW."key",'_')+1),
				NEW."id",
				CASE NEW."Type" WHEN 'Multiple' THEN
					(SELECT count()+1 FROM "form_structure" WHERE substr(NEW."key",1,instr(NEW."key",'_')-1)="form_structure"."form")
				ELSE NULL END);
		INSERT INTO "question_texts"("question","lang","text","left","right")
			VALUES(NEW."id", 'de', NEW."Q_de", NEW."PolLeft_de", NEW."PolRight_de");
		INSERT INTO "question_texts"("question","lang","text","left","right")
			VALUES(NEW."id", 'en', NEW."Q_en", NEW."PolLeft_en", NEW."PolRight_en");
		INSERT INTO "choices_de_en"("question","choice","text_de","text_en") VALUES(NEW."id", 1,NEW."Single_de_1" ,NEW."Single_en_1" );
		INSERT INTO "choices_de_en"("question","choice","text_de","text_en") VALUES(NEW."id", 2,NEW."Single_de_2" ,NEW."Single_en_2" );
		INSERT INTO "choices_de_en"("question","choice","text_de","text_en") VALUES(NEW."id", 3,NEW."Single_de_3" ,NEW."Single_en_3" );
		INSERT INTO "choices_de_en"("question","choice","text_de","text_en") VALUES(NEW."id", 4,NEW."Single_de_4" ,NEW."Single_en_4" );
		INSERT INTO "choices_de_en"("question","choice","text_de","text_en") VALUES(NEW."id", 5,NEW."Single_de_5" ,NEW."Single_en_5" );
		INSERT INTO "choices_de_en"("question","choice","text_de","text_en") VALUES(NEW."id", 6,NEW."Single_de_6" ,NEW."Single_en_6" );
		INSERT INTO "choices_de_en"("question","choice","text_de","text_en") VALUES(NEW."id", 7,NEW."Single_de_7" ,NEW."Single_en_7" );
		INSERT INTO "choices_de_en"("question","choice","text_de","text_en") VALUES(NEW."id", 8,NEW."Single_de_8" ,NEW."Single_en_8" );
		INSERT INTO "choices_de_en"("question","choice","text_de","text_en") VALUES(NEW."id", 9,NEW."Single_de_9" ,NEW."Single_en_9" );
		INSERT INTO "choices_de_en"("question","choice","text_de","text_en") VALUES(NEW."id",10,NEW."Single_de_10",NEW."Single_en_10");
		INSERT INTO "choices_de_en"("question","choice","text_de","text_en") VALUES(NEW."id",11,NEW."Single_de_11",NEW."Single_en_11");
		INSERT INTO "choices_de_en"("question","choice","text_de","text_en") VALUES(NEW."id",12,NEW."Single_de_12",NEW."Single_en_12");
	END;

CREATE TRIGGER IF NOT EXISTS 'insert_meta'
	INSTEAD OF INSERT ON "meta"
	BEGIN
		INSERT INTO "questions"("question_type","positive","range")
			VALUES(NEW."Type",NEW."Positive",NEW."Range");
		INSERT INTO "question_meta" VALUES(
			last_insert_rowid(), NEW."ID", NEW."Q_de", NEW."Q_en", NEW."Type",
			NEW."PolLeft_de", NEW."PolRight_de", NEW."PolLeft_en", NEW."PolRight_en",
			NEW."Single_de_1", NEW."Single_en_1", NEW."Single_de_2", NEW."Single_en_2",
			NEW."Single_de_3", NEW."Single_en_3", NEW."Single_de_4", NEW."Single_en_4",
			NEW."Single_de_5", NEW."Single_en_5", NEW."Single_de_6", NEW."Single_en_6",
			NEW."Single_de_7", NEW."Single_en_7", NEW."Single_de_8", NEW."Single_en_8",
			NEW."Single_de_9", NEW."Single_en_9", NEW."Single_de_10",NEW."Single_en_10",
			NEW."Single_de_11",NEW."Single_en_11",NEW."Single_de_12",NEW."Single_en_12"
		);
	END;

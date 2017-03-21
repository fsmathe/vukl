#!/usr/bin/python3

# Copyright 2014-2016 Florian Schwahn, Markus Kurtz

# This file is part of VUKL.
#
# VUKL is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# VUKL is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VUKL.  If not, see <http://www.gnu.org/licenses/>.

__author__ = 'kurtz'

import sqlite3
import csv
import readline

csv_delim = '\t'
coursedict = {s:s for s in ['Teilbereich', 'Anrede', 'Titel', 'Vorname', 'Nachname', 'Lehrveranstaltung', 'Lehrveranstaltung_en']}
coursedict['id'] = 'Kennung'

csv_titles_start = ["Teilbereich", "Anrede", "Titel", "Vorname", "Nachname",
    "Lehrveranstaltung", "Kennung", "Studiengang", "Raum",
    "Lehrveranstaltungsart", "Teilnehmer", "Sekundärdozenten", "Periode",
    "Bogen"]
csv_titles_end = ["Datensatz-Ursprung"]

def verify_titles(l):
    '''Raise an error if the argument is not as specified.'''
    if l[:len(csv_titles_start)] != csv_titles_start:
        raise Exception('The beginning of the first line is not as expected.')
    if l[-len(csv_titles_end):] != csv_titles_end:
        raise Exception('The end of the first line is not as expected.')

def extract_questions(l):
    '''Return the part of the line that contains the questions.'''
    return l[len(csv_titles_start):-len(csv_titles_end)]

def get_questions_from_sheet(sheet):
    '''Return all questions ordered by their number on the evaluation sheet.'''
    return first_cursor.execute(
        'SELECT `question` FROM `sheets` WHERE `type`=? ORDER BY `number`',
        sheet).fetchall()


def readfile(name, evaluation_type = None):
    '''Insert data from the given file into the database.'''
    with open(name,newline='') as f:
        reader = csv.reader(f, delimiter=csv_delim)
        csv_titles = next(reader)
        verify_titles(csv_titles)
        original_question_texts = extract_questions(csv_titles)
        # verify questions and evaluation_type or even set evaluation_type
        for row in reader:
            # add new course (does nothing if course already exists in db)
            insert('courses', {sql_key: reader[csv_key]
                for sql_key,csv_key in coursedict.items()})
            # get the questions for the given type of evaluations
            q = 
            # add all the answers
            for question in row.values()[42:]: #TODO
                # insert data into answers with according question
                insert('answers', {'course': })


def insert(table, d):
    questionmarks = ','.join('?' for q in d)
    con.execute('INSERT INTO `'+table+'` ('+questionmarks+')
        VALUES ('+questionmarks+')', tuple(d.keys()+d.values()))

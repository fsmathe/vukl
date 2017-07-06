#!/usr/bin/python3

# Copyright 2014-2017 Florian Schwahn, Markus Kurtz

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

from .. import db
import csv
import itertools

csv_delim = '\t'
csv_encoding = 'latin1'
course_field_names = ['Kennung','Teilbereich', 'Anrede', 'Titel', 'Vorname', 'Nachname', 'Lehrveranstaltung','Periode']

def read(csv_file, form = None, db_file = None):
    reader = EvaluationReader(db_file, form)
    reader.read_file(csv_file)

class EvaluationReader(db.DataConnector):
    def __init__(self, db_file = None, form = None):
        super().__init__(db_file)
        self._form = form

    def read_file(self, filename):
        '''Read a csv file and save it to the database.'''
        raw_data = self.csv2matrix(filename)
        answers_data = self.restructure_answers(raw_data)
        questions = self.get_form_structure()
        for course,sheet,row in zip(*answers_data):
            for (question, multiple), answer in zip(questions, row):
                answer = self.preprocess_answer(answer, multiple)
                self.insert_answer(course, sheet, question, answer)
        self._con.commit()

    def csv2matrix(self, filename):
        '''Convert given file into a column based matrix.'''
        with open(filename, encoding=csv_encoding, newline='') as f:
            f.readline()
            #TODO: verify questions and form or even set form
            #csv_header = next(reader)
            #verify_header(csv_header)
            #original_question_texts = self.extract_questions(csv_header)
            reader = csv.reader(f, delimiter=csv_delim,
                    quoting=csv.QUOTE_NONNUMERIC)
            return list(reader)

    def restructure_answers(self, raw_data):
        '''Preprocess matrix of answers.'''
        answers = [self.extract_questions(row) for row in raw_data]
        course_ids = [self.get_or_create_course(row) for row in raw_data]
        sheet_ids = [int(row[csv_header_start.index('Bogen')]) for row in raw_data]
        return (course_ids, sheet_ids, answers)

    @staticmethod
    def extract_questions(l):
        '''Return the part of the line that contains the questions.'''
        return l[len(csv_header_start):-len(csv_header_end)]

    def get_or_create_course(self, row):
        '''Return course id of given metadata, create new course if necessary.'''
        return self.get_or_create('courses',
                {key: row[csv_header_start.index(key)]
                for key in course_field_names})

    def get_form_structure(self):
        '''Return structure of current evaluation type.'''
        return self.select(['question','multiple'], 'form_structure',
                '"form"=?', 'position', (self._form,))

    @staticmethod
    def preprocess_answer(answer, multiple):
        '''Return answer to save into database or None.'''
        if multiple == None:
            if answer == '' or answer == '[BILD]':
                return None
            return int(answer) if isinstance(answer,float) else answer
        if answer:
            # Return the answer as number of the selected choice:
            return multiple
        return None

    def insert_answer(self, course, sheet, question, answer):
        '''Insert a new answer into the database.'''
        if answer != None:
            self.insert('answers',
                {'course': course, 'form': self._form,
                'sheet': sheet, 'question': question, 'value': answer})

### TODO: Use this

# The csv files given consist of a header line and then one line per
# scanned evaluation sheet.
# The fields as specified in the header start with
csv_header_start = ['Teilbereich', 'Anrede', 'Titel', 'Vorname', 'Nachname',
    'Lehrveranstaltung', 'Kennung', 'Studiengang', 'Raum',
    'Lehrveranstaltungsart', 'Teilnehmer', 'Sekundärdozenten', 'Periode',
    'Bogen']
# and end with
csv_header_end = ['Datensatz-Ursprung']
# In the case the given header is not as expected,
# raise an InconsistencyException in this function:
def verify_header(l):
    '''Raise an error if the given list is not as specified.'''
    if len(l) < len(csv_header_start)+len(csv_header_end):
        raise InconsistencyException('The header line is to short.')
    if l[:len(csv_header_start)] != csv_header_start:
        raise InconsistencyException(
            'The first fields of the header line are not as expected.')
    if l[-len(csv_header_end):] != csv_header_end:
        raise InconsistencyException(
            'The last fields of the header line are not as expected.')


class InconsistencyException(Exception):
    '''Exceptions for inconsistent data.'''
    pass

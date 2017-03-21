# Copyright 2017 Markus Kurtz

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


import sqlite3

# TODO: Give conditions in an abstract fashion (unlike `key`='value')

class Filter:
    def __str__(self):
        return '1'

class AnswerFilter(Filter):
    sql = '? IN (SELECT text FROM answers WHERE course=? AND question=? AND Bogen=?)'
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer

class DataSelector:
    def __init__(self, db, lang='de'):
        self._db = db
        self._cur_firstcolumn = db.cursor()
        self._cur_firstcolumn.row_factory = lambda cursor, row: row[0]
        self._cur_row = db.cursor()
        self._cur_row.row_factory = sqlite3.Row
        self.lang = lang
    def select(self, selection='*', table='sqlite_master', where='1',
            distinct=False):
        """Return column of SQL query specified by the arguments."""
        query = "SELECT " + ("DISTINCT " if distinct else "") + selection +\
            " FROM " + table +\
            " WHERE " + where
        return self._cur_firstcolumn.execute(query).fetchall()
    def alias_lang(self, key):
        if '_' not in key:
            return "`" + key + "`"
        if '_'+self.lang in key:
            return "`" + key + "` AS '" + key.replace('_'+self.lang,'') + "'"
        else:
            return None

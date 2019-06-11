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

SQL_DATABASE = 'db/vukl.db'

class DataConnector:
    SQL_TEMPLATE = 'template.sql'
    def __init__(self, db_file = None):
        if not db_file:
            db_file = SQL_DATABASE
        self._con = sqlite3.connect(db_file)
        self._cur_firstcolumn = self._con.cursor()
        self._cur_firstcolumn.row_factory = lambda cursor, row: row[0]
        self._cur_row = self._con.cursor()
        self._cur_row.row_factory = sqlite3.Row
        self._cur = self._con.cursor()
        self._cur.executescript(open(self.SQL_TEMPLATE).read())

    def __del__(self):
        self._con.commit()
        self._con.close()

    def get_or_create(self, table, d, key='ROWID'):
        '''Return key of table entry with values given in dict d.

        If there are entries with values corresponding to d,
        return the key of any of them.
        Otherwise insert a new entry with these values and return the new key.
        '''
        names, placeholder, values = self.dict2sqlkeyvalues(d)
        entries = self._cur_firstcolumn.execute('SELECT ' + key +
            ' FROM ' + table +
            ' WHERE ' + names + '=' + placeholder,
            values).fetchall()
        if entries:
            return entries[0]
        # Insert new row in the database, if no entry was selected.
        self.insert(table, d)
        return self._cur.execute('SELECT last_insert_rowid()').\
                fetchone()[0]

    def insert(self, table, d):
        names, placeholder, values = self.dict2sqlkeyvalues(d)
        self._cur.execute('INSERT INTO ' + table + names +
                ' VALUES' + placeholder, values)

    @staticmethod
    def dict2sqlkeyvalues(d):
        names = '("' + '","'.join(d.keys()) + '")'
        placeholder = '(' + ','.join('?' for _ in d) + ')'
        return names, placeholder, tuple(d.values())

    def _select(self, selection='*', table='sqlite_master', where='1',
            order=None, parameters=(), column=False, distinct=False):
        '''Return result of SQL query specified by plain SQL arguments.'''
        query = 'SELECT ' + ('DISTINCT ' if distinct else '') + selection +\
            ' FROM ' + table +\
            ' WHERE ' + where +\
            (' ORDER BY '+order if order!=None else '')
        return (self._cur_firstcolumn if column else self._cur)\
                .execute(query,parameters).fetchall()

    def select(self, selection=None, table='sqlite_master', where='1',
            order='', parameters=(), column=None, distinct=False):
        '''Return result of SQL query specified by the arguments.'''
        if column == None:
            column = isinstance(selection,str)
        selection = '*' if selection == None else self.sqlkeyword(selection)
        if order != None:
            order = self.sqlkeyword(order)
        table = self.sqlkeyword(table)
        return self._select(selection, table, where, order,
                parameters, column, distinct)

    @staticmethod
    def sqlkeyword(x):
        '''Return (list of) quoted keyword(s) from a (list of) string(s).'''
        return '"' + (x if isinstance(x,str) else '","'.join(x)) + '"'

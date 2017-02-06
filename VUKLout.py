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

__author__ = 'fschwahn'

import sqlite3
import sys
import os
import codecs
import readline
import re

####### SETTINGS #######

# database
DB_FILE = 'db/vukl.db'

# output schemes
SCHEME_FOLDER = 'scheme/'
SCHEME_FILE_ENCODING = 'utf-8-sig'

# LaTeX output file
LATEX_OUTPUT_FILE_NAME = "tex/vukl.tex"
LATEX_OUTPUT_FILE_ENCODING = "utf-8"

# TODO: refactor to capital names
const_lbgeneral = 5  # Bei weniger Teilnehmenden wird generell keine Auswertung erstellt
const_lbvorlesung = 8  # Bei weniger Teilnehmenden wird zu den folgenden Veranstaltungen keine Auswertung erstellt
const_vorlesung = 'Ma[GH](Vor|VL\d\d)'  # Regulärer Ausdruck (matcht etwa MaHVor oder MaGVL01)
str_language = "de"
multisplit_current_value = "DUMMY"
multisplit_questions = []


########################





def proper_input(x_n):
    """Outputs an integer from 0 to n for given input"""
    x = input()
    if not x.isdigit():
        result = 0
    elif int(x) < 1 or int(x) > x_n:
        result = 0
    else:
        result = int(x)
    return result


def part_after_underscore(x_string_old):
    """Gibt den Substring nach dem letzten Unterstrich im String aus"""
    x_string_old_split = x_string_old.split('_')
    return x_string_old_split[-1]


def part_before_underscore(x_string_old):
    """Gibt den Substring vor dem ersten Unterstrich im String aus"""
    x_string_old_split = x_string_old.split('_')
    return x_string_old_split[0]


# Forme eine Liste in Textform um.
# Beispiel: [1,4,9,16] resultiert in '1, 4, 9 und 16'.
# Nimmt an, dass die Liste mindestens ein Element enthält.
def list_to_text(x_list):
    x_string = ""
    # ", " zwischen Auflistungspunkte setzen,
    for item in x_list[:-1]:
        x_string += item + ", "
    # außer zwischen den letzten beiden, falls mehr als ein Punkt vorkommt,
    if len(x_list) > 1:
        # dort dann ", " durch " und " ersetzen.
        x_string = x_string[:-2] + ' und '
    # Schließlich letztes Element anfügen.
    x_string += x_list[-1]
    return x_string


# Gesamtheit aller als wahr interpretierten Einträge einer Liste sortiert ausgeben.
# Beispiel: [7,0,3,8,3,8] resultiert in [3,7,8].
def sort_unique(x_list):
    x_set = set()
    for item in x_list:
        if item[0]:
            x_set.add(item[0])
    return sorted(list(x_set))


# x_keys = Liste an Schlüsseln für die ein Datensatz bestimmte Werte annehmen muss.
#   Einträge hiervon können auch wiederum Listen sein für den Fall, dass ein Wert an
#   verschiedenen Stellen stehen kann.
#   Genutzt werden kann dies etwa, wenn man an mehreren Stellen angeben kann, wer die
#   Übungen gehalten hat, etwa weil man auf einem Bogen Rückmeldungen zu zwei Personen
#   geben soll, die die Übung gemeinsam hielten.
# x_lv   = Liste, mit erlaubten Werten für die entsprechenden Schlüssel in x_keys.
# Gibt eine verundete WHERE-Klausel zurück mit jedem Eintrag
# entweder 'Schlüssel=Wert' oder 'Wert IN (Schlüssel …)'
def values_keys_to_string(x_lv, x_keys):
    result = " WHERE "
    if len(x_keys) == len(x_lv):
        for i, key in enumerate(x_keys):  # falls i/key eine liste sind, das ganze mit "oder" verknüpfen
            if isinstance(key, str):
                result += key + "='" + x_lv[i] + "' AND "
            elif all(isinstance(item, str) for item in key):
                result += " '" + x_lv[i] + "' IN ("
                for sub_key in key:
                    result += sub_key + ","
                result = result[:-1] + ") AND "
                multisplit_current_value = x_lv[i]
            else:
                print("values_keys_to_string: Die Schluessel muessen Strings oder Listen von Strings sein.")
    else:
        print("values_keys_to_string: Die Anzahl stimmt nicht überein")
        return ""
    return result[:-4]


# x_keys = Liste an Schlüsseln für die ein Datensatz bestimmte Werte annehmen muss.
# x_lv   = Liste, mit erlaubten Wertelisten für die entsprechenden Schlüssel in x_keys.
# asserts len(x_keys)==len(x_lv)
# Gibt eine Liste von verundeten Ausdrücken zurück
# mit einem Eintrag für jede Kombination von Werten in x_lv.
# Die Liste entspricht also $\bigtimes_{x\in x_lv} x$ in lexikographischer Ordnung.
# Beispiel: values_keys_to_string_list(['A','B','C'],[['1','2'],'3',['5','6']]) resutltiert in
# ['A=1 AND B=3 AND C=5','A=1 AND B=3 AND C=6','A=2 AND B=3 AND C=5','A=2 AND B=3 AND C=6']
def values_keys_to_string_list(x_lv, x_keys):
    if len(x_lv) != len(x_keys):
        print("values_keys_to_string_list: Es sollte genau so viele Schlüssel wie Werte geben!")
        return [""]
    if len(x_lv) == 0:
        return [""]
    key = x_keys[0]
    value = x_lv[0]
    if isinstance(key, str):
        return [key + "='" + value + "' AND " + i for i in values_keys_to_string_list(x_lv[1:], x_keys[1:])]
    if all(isinstance(item, str) for item in key):
        return [sub_key + "='" + value + "' AND " + i for i in values_keys_to_string_list(x_lv[1:], x_keys[1:]) for
                sub_key in key]
    print("values_keys_to_string_list: Du hast es kaputt gemacht :(")


# list_list_x = Liste von Listen der Form ['Tabelle_Nr',w_1,…,w_n],
# wobei 'Tabelle' der Name einer Tabelle, `Q_Nr` ein Feld dieser Tabelle und
# w_1,…,w_n mögliche Werte für `Q_Nr` sind.
# Ergebnis ist ein String beginnend mit AND und bestehend aus AND-verknüpften
# Bedingungen 'Q_Nr IN (w_1,…,w_n)' für jede Liste zur Tabelle x_table_name.
# Beispiel: filter_to_string([['MaGVL01_1',1,4,9],['MaGVL01_3','foo'],['MaHVL01_5',2,4]],'MaGVL01')
# gibt 'AND `Q_1` IN ('1','4','9') AND `Q_3` IN ('foo')'
def filter_to_string(list_list_x, x_table_name):
    """Outputs a string for a list of filter rules"""
    result = ""
    short_list_list_x = []
    for list_x in list_list_x:
        if part_before_underscore(list_x[0]) == x_table_name:
            short_list_list_x.append(list_x)
    if short_list_list_x:
        for list_x in short_list_list_x:
            result = result + " AND `Q_" + part_after_underscore(list_x[0]) + "` IN ("
            for x in list_x[1]:
                result += "'" + x + "',"
            result = result[:-1] + ")"
    return result


def choose_from_list(x_list):
    """Gibt die nummerierten Elemente der Liste aus, fragt welches ausgewählt werden soll -> return string"""
    for i in range(len(x_list)):
        print("ID", i, ":\t", x_list[i])
    print("Bitte geben Sie die ID an:", end=" ")
    i = proper_input(len(x_list))
    return x_list[i]


# Ersetzt in x_string Vorkommen von '[Stichwort]' oder aber '[Tabelle_Nr]' durch eine in Worten gefasste Liste
# aller Einträge von `Q_Nr` in Tabelle; etwa um Personennamen oder Lehrveranstaltungsnamen auszugeben.
# x_lv, x_keys werden an values_keys_to_string(_list|) und
# x_list_filter wird an filter_to_string weitergereicht,
# um eine Auswahl an Inhalten zu erhalten.
def substitute_square_brackets(x_string, x_lv, x_keys, x_list_filter):
    result = x_string
    # Ersetzung von '[Tabelle_Nr]'
    for ersetzung in re.findall('\[[^][]*\]', x_string):  # Über alle Vorkommen von '[…]' iterieren
        fragen = ersetzung[1:-1].split()  # '[' und ']' rausschneiden
        x_rohdaten = []  # Liste aller Einträge durch die '[…]' ersetzt werden soll
        if len(fragen) == 1:
            # Falls ein '[Tabelle_Nr]' ersetzt werden soll:
            if fragen[0] in list_fragen:
                # Lese Einträge zu `Q_Nr` in Tabelle entsprechend momentaner Auswahl
                vukl_cursor.execute(
                    "SELECT `Q_" + part_after_underscore(fragen[0]) + "` FROM " + repr(
                        part_before_underscore(fragen[0]))
                    + values_keys_to_string(x_lv, keys)  # WHERE „ist passende Lehrveranstaltung“
                    + filter_to_string(x_list_filter,
                                       part_before_underscore(fragen[0])))  # AND „passt auf momentane Filter“
                x_rohdaten = vukl_cursor.fetchall()
        else:
            # Falls verschiedene Ergebnisse für verschiedene Lehrveranstaltungen kumuliert werden sollen:
            where_statements = values_keys_to_string_list(x_lv, x_keys)
            for i in range(len(fragen)):
                # '[Tabelle1_x1 Tabelle2_x2 … Tabellen_xn]' mit Zahlen 'xi' ersetzen durch …
                if fragen[0] in list_fragen:
                    # Einträge zu `Q_xi` aus Tabellei für i-te Lehrveranstaltungs-Kombination auswählen.
                    vukl_cursor.execute('SELECT `Q_' + part_after_underscore(fragen[i]) +
                                        '` FROM ' + repr(part_before_underscore(fragen[i])) +
                                        ' WHERE ' + where_statements[i][:-5])
                    x_rohdaten += vukl_cursor.fetchall()
        if len(x_rohdaten) > 0:  # Falls es Ergebnisse gab …
            # überall '[Tabelle_Nr]' durch die Gesamtheit aller Nicht-NULL-Einträge
            # in x_rohdaten sortiert und in Textform ausgeben.
            result = result.replace(ersetzung, list_to_text(sort_unique(x_rohdaten)))
    for keyword in ['Lehrveranstaltung', 'Subdozent', 'Studiengang', 'Teilbereich', 'Anrede', 'Titel', 'Vorname',
                    'Nachname', 'LVTyp', 'Vertiefungsgebiet', 'RaumTermin', 'Periode']:
        if '[' + keyword + ']' in result:
            x_set_rohdaten = set()
            str_q_substitute = ""
            for table in table_names:
                # Lese Einträge zu `keyword` in Tabelle entsprechend momentaner Auswahl
                vukl_cursor.execute("SELECT " + keyword + " FROM " + repr(table) + values_keys_to_string(x_lv, x_keys)
                                    + filter_to_string(x_list_filter, table))
                x_rohdaten = vukl_cursor.fetchall()
                for item in x_rohdaten:
                    if item[0]:
                        x_set_rohdaten.add(item[0])
            if len(x_rohdaten) > 0:  # Falls es Ergebnisse gab '[$keyword]' wie oben ersetzen.
                result = result.replace(('[' + keyword + ']'), list_to_text(sorted(list(x_set_rohdaten))))
    if '[Teilnehmerzahl]' in result:  # Gibt an, wieviele Bögen maximal von einem Typ abgegeben wurden
        max_zahl_teilnehmer = 0
        for table in table_names:
            vukl_cursor.execute("SELECT COUNT(*) FROM " + repr(table) + values_keys_to_string(x_lv, x_keys)
                                + filter_to_string(x_list_filter, table))
            x_rohdaten = vukl_cursor.fetchall()
            if x_rohdaten[0][0] > max_zahl_teilnehmer:
                max_zahl_teilnehmer = x_rohdaten[0][0]
        result = result.replace('[Teilnehmerzahl]', str(max_zahl_teilnehmer))
    return result


# list_x = Liste, mit Einträgen 0 bis range (und ignorierten weiteren Einträgen, z. B. NULL)
# Beispiele:
# raw_to_distribution([2,3,1,1,0,3,0,3,3,0], 3, false) ergibt '{{2}{1}{4}}'
# raw_to_distribution([2,3,1,1,0,3,0,3,3,0], 2, false) ergibt '{{2}{1}}'
# raw_to_distribution([2,3,1,1,0,3,0,3,3,0], 3, true ) ergibt '{3}{{2}{1}{4}}'
# raw_to_distribution([2,3,1,1,0,3,0,3,3,0], 2, true ) ergibt '{3}{{2}{1}}'
def raw_to_distribution(list_x, x_range, x_bool_neutral):
    """Outputs a string with the summed up values of all answers in the format
    {{number of 1s}{number of 2s}...} or {number of 0s}{{number of 1s}...}"""
    result = ""
    if x_range.isdigit():
        result = "{"
        counter = 0
        if x_bool_neutral:
            for item in list_x:
                if item.isdigit():
                    if int(item) == 0:
                        counter += 1
            result = "{" + str(counter) + "}{"
        for i in range(int(x_range)):
            counter = 0
            for item in list_x:
                if item.isdigit():
                    if int(item) - 1 == i:
                        counter += 1
            result += "{" + str(counter) + "}"
        result += "}"
    else:
        print("Der Wert Range in der meta-Tabelle enthält keine Zahl, es wird aber eine benötigt!")
    return result


def data_to_tex(x_list_auswahl_lv, x_list_scheme, x_list_filter):
    for lv in x_list_auswahl_lv:
        tex_file.write("\n\n")
        x_number_splits = 0
        append_to_question = []
        for i, style in enumerate(x_list_scheme):
            # # # # # Split "Klammern" erkennen (und überspringen)
            if x_number_splits > 0:
                if style[0] == 'unsplit':
                    x_number_splits -= 1
                if style[0] == 'split':
                    x_number_splits += 1
                continue
            # # # # # Print
            if style[0] == 'print':
                tex_file.write(substitute_square_brackets(style[1], lv, keys, x_list_filter) + "\n")
            # # # # # Append
            elif style[0] == 'append':
                append_to_question.append(style[1])
            elif style[0] == 'unappend':
                append_to_question.pop()
            # # # # # Chapter, Section, Subsection
            elif style[0] == 'section' or style[0] == 'subsection' \
                    or style[0] == 'chapter' or style[0] == 'kurzchapter':
                tex_file.write("\\" + style[0] + "{"
                               + substitute_square_brackets(style[1], lv, keys, x_list_filter) + "}\n")
            # # # # # Filter
            elif style[0] == 'filter':
                if style[1] in list_fragen:
                    x_list_filter.append((style[1], style[2:]))
                else:
                    print(style[1] + " nach dem filter-Befehl ist KEINE Frage aus der meta-Tabelle. "
                                     "Syntax des Schemas anpassen und VUKL neu starten!")
            elif style[0] == 'unfilter':
                x_list_filter.pop()
            # # # # # Split
            # Bei Split nach mehreren Fragen <FrageS1> ... <FrageSn>, müssen diese für jeden Datensatz paarweise disjunkte Werte besitzen.
            # Es werden dann alle in einer der Fragen vorkommenden Werte $i der Reihe nach durchgegangen
            # und die bis zum entsprechenden Unsplit angegebenen Zeilen ausgegeben.
            # Hierbei können in jeder Zeile ebenso viele Fragen <FrageA1> ... <FrageAn> im Schema angegeben werden.
            # Zur Ausgabe verwendet werden dann die mit Vielfachheiten versehenen Mengen
            # { D(<FrageAj>) | D(<FrageSj>) == $i UND j in 1..n UND D ein Datensatz gemäß der sonstigen Bedingungen },
            # wobei D(<FrageX>) der Wert von D bei der entsprechenden Frage ist
            # und die sonstigen Bedingungen durch Lehrveranstaltung und vorherige Splits und Filter gegeben sind.
            # Genutzt wird dies etwa, wenn man mehrere verschiedene Personen auf einem Bogen bewerten soll.
            elif style[0] == 'split':
                x_number_splits = 1  # wenn das aufgerufen wird, dann waren es vorher null splits
                new_list_scheme = []
                for scheme in x_list_scheme[i + 1:]:
                    if scheme[0] == 'unsplit' and x_number_splits == 1:
                        break  # letztes unsplit wird nicht mehr weitergegeben an rek. Funktionsaufruf
                    elif scheme[0] == 'unsplit':
                        x_number_splits -= 1
                    elif scheme[0] == 'split':
                        x_number_splits += 1
                    else:
                        if len(scheme) > 1:
                            if scheme[1] in list_fragen:
                                if not part_before_underscore(scheme[1]) == part_before_underscore(style[1]):
                                    print("In einem 'Split'-Bereich dürfen keine Fragen von anderen Fragebögen genutzt "
                                          "werden. Die entsprechenden Fragen entfallen daher einfach.")
                                    continue
                    new_list_scheme.append(scheme)
                list_split_values = []
                multisplit_number = len(style[1:])
                multisplit_questions = style[1:]
                for splitstyle in multisplit_questions:
                    if splitstyle not in list_fragen:
                        print("Der Split ", end="")
                        print(multisplit_questions)
                        print(" enthält im Weiteren ungültige Fragen. Das Ergebnis wird fehlerhaft ausgegeben.")
                for splitstyle in style[1:]:
                    vukl_cursor.execute("SELECT `Q_" + part_after_underscore(splitstyle) + "` FROM "
                                        + repr(part_before_underscore(splitstyle)) + values_keys_to_string(lv, keys)
                                        + filter_to_string(x_list_filter, part_before_underscore(splitstyle)))
                    list_split_values += vukl_cursor.fetchall()
                if len(style[1:]) > 1:
                    or_keys = []
                    for splitstyle in style[1:]:
                        or_keys.append("`Q_" + part_after_underscore(splitstyle) + "`")
                    keys.append(or_keys)
                else:
                    keys.append("`Q_" + part_after_underscore(style[1]) + "`")
                set_values = set()
                for value in list_split_values:
                    if value[0]:  # sonst leere strings
                        set_values.add(value[0])
                list_values = sorted(set_values)
                new_list_auswahl_lv = []
                for value in list_values:
                    new_list_auswahl_lv.append(lv + (value,))
                data_to_tex(new_list_auswahl_lv, new_list_scheme, x_list_filter)
                keys.pop()
            # # # # # Semester
            elif style[0] == 'semester':
                if style[1] in table_names:
                    vukl_cursor.execute("SELECT * FROM meta WHERE ID LIKE '%" + style[1] + "%' AND Type='SemesterBA'")
                    meta_q = vukl_cursor.fetchone()
                    meta_dict_1 = dict(zip(meta_keys, meta_q))
                    if meta_dict_1['Neutral'] == 'True' or meta_dict_1['Neutral'] == 'true':
                        meta_dict_1['Neutral'] = True
                    else:
                        meta_dict_1['Neutral'] = False
                    vukl_cursor.execute("SELECT * FROM meta WHERE ID LIKE '%" + style[1] + "%' AND Type='SemesterMA'")
                    meta_q = vukl_cursor.fetchone()
                    meta_dict_2 = dict(zip(meta_keys, meta_q))
                    if meta_dict_2['Neutral'] == 'True' or meta_dict_2['Neutral'] == 'true':
                        meta_dict_2['Neutral'] = True
                    else:
                        meta_dict_2['Neutral'] = False
                    vukl_cursor.execute("SELECT `Q_" + part_after_underscore(meta_dict_1['ID']) + "`, `Q_"
                                        + part_after_underscore(meta_dict_2['ID']) + "` FROM "
                                        + repr(style[1]) + values_keys_to_string(lv, keys)
                                        + filter_to_string(x_list_filter, style[1]))
                    rohdaten_q_raw = vukl_cursor.fetchall()
                    if len(rohdaten_q_raw) > const_lbgeneral:
                        rohdaten_q_1 = []
                        rohdaten_q_2 = []
                        for row in rohdaten_q_raw:  # Falls beides: Bachelorstudent
                            if (row[0] and row[1]) or row[0]:
                                rohdaten_q_1.append(row[0])
                            else:
                                rohdaten_q_2.append(row[1])
                        semester_string = "\\semester{Semester: }{"
                        for i in range(int(meta_dict_1['Range'])):
                            semester_string += "{" + meta_dict_1['Single_' + str_language + '_' + str(i + 1)] + "}"
                        semester_string += "}" + raw_to_distribution(rohdaten_q_1, meta_dict_1['Range'],
                                                                     meta_dict_1['Neutral']) + "{"
                        for j in range(int(meta_dict_2['Range'])):
                            semester_string += "{" + meta_dict_2['Single_' + str_language + '_' + str(j + 1)] + "}"
                        semester_string += "}" + raw_to_distribution(rohdaten_q_2, meta_dict_2['Range'],
                                                                     meta_dict_1['Neutral']) + "\n"
                        tex_file.write(semester_string)
                else:
                    print("Der folgende Style startet mit einem Tabellennamen, hat aber keine bekannte Option.")
                    print(style)
                    # # # # # Ausgabe der tatsächlichen Fragen
            elif style[0] in list_fragen:
                if len(style) == 1:
                    vukl_cursor.execute("SELECT `Q_" + part_after_underscore(style[0]) + "` FROM "
                                        + repr(part_before_underscore(style[0])) + values_keys_to_string(lv, keys)
                                        + filter_to_string(x_list_filter, part_before_underscore(style[0])))
                    rohdaten_q_raw = vukl_cursor.fetchall()
                else:  # Funktioniert nur, wenn zuvor 'split <FrageA> <FrageB> ...' genutzt wurde.
                    # Bestimmt mittels globaler Variable `multisplit_current_value`, welche der Fragen <FrageA>, <FrageB>, ... den momentanen Wert annimmt.
                    where_statements = values_keys_to_string_list(lv, keys)
                    rohdaten_q_raw = []
                    for i in range(len(style)-1):
                        vukl_cursor.execute('SELECT `Q_' + part_after_underscore(style[i]) +
                                            '` FROM ' + repr(part_before_underscore(style[i])) +
                                            ' WHERE ' + where_statements[i][:-5])
                        rohdaten_q_raw += vukl_cursor.fetchall()
                # Ausgabe unterbinden, falls zu wenige Datensätze vorliegen
                if len(rohdaten_q_raw) < const_lbgeneral:
                    continue
                # Bei Vorlesungen gilt eine weitere (schärfere) Schranke
                if re.fullmatch(const_vorlesung, part_before_underscore(style[0])) and len(
                        rohdaten_q_raw) < const_lbvorlesung:
                    continue
                rohdaten_q = []
                for item in rohdaten_q_raw:
                    if item[0]:
                        rohdaten_q.append(item[0])
                vukl_cursor.execute("SELECT * FROM meta WHERE ID='" + style[0] + "'")
                meta_q = vukl_cursor.fetchone()
                meta_dict = dict(zip(meta_keys, meta_q))
                if (len(rohdaten_q) == 0) and (meta_dict['Type'] != 'Offen'):
                    continue
                if meta_dict['Neutral'] == 'True' or meta_dict['Neutral'] == 'true':
                    meta_dict['Neutral'] = True
                else:
                    meta_dict['Neutral'] = False
                question = meta_dict['Q_' + str_language] + ''.join(append_to_question)
                if meta_dict['Type'] == 'Skala':
                    tex_file.write("\\skala{" + meta_dict['Positive'] + "}{" + question + "}{"
                                   + meta_dict['PolLeft_' + str_language] + "}{" + meta_dict['PolRight_' + str_language]
                                   + "}" + raw_to_distribution(rohdaten_q, meta_dict['Range'], meta_dict['Neutral'])
                                   + "\n")
                elif meta_dict['Type'] == 'Single' or meta_dict['Type'] == 'SemesterBA' \
                        or meta_dict['Type'] == 'SemesterMA' or meta_dict['Type'] == 'SingleGraph':
                    if meta_dict['Range'] == '2' and meta_dict['Single_de_1'] == 'ja' \
                            and meta_dict['Single_de_2'] == 'nein':
                        tex_file.write("\\janein{" + question + "}"
                                       + raw_to_distribution(rohdaten_q, meta_dict['Range'], meta_dict['Neutral'])
                                       + "\n")
                    else:
                        single_string = "\\single"
                        if meta_dict['Type'] == 'SingleGraph':
                            single_string += "graph"
                        single_string += "{" + question + "}{"
                        for i in range(int(meta_dict['Range'])):
                            single_string += "{" + meta_dict['Single_' + str_language + '_' + str(i + 1)] + "}"
                        single_string += "}" \
                                         + raw_to_distribution(rohdaten_q, meta_dict['Range'], meta_dict['Neutral']) \
                                         + "\n"
                        tex_file.write(single_string)
                elif meta_dict['Type'] == 'YesNoComment':
                    tex_file.write("\\yesnocomment{" + question + "}" +
                                   raw_to_distribution(rohdaten_q, meta_dict['Range'], meta_dict['Neutral'])[
                                   1:-1] + "\n")
                elif meta_dict['Type'] == 'Offen':
                    offen_string = "\\offen{" + question + "}{%\n"
                    set_rohdaten_q = set(rohdaten_q)
                    for row in set_rohdaten_q:
                        if rohdaten_q.count(row) > 1:
                            offen_string += "\\item " + row + " \((" + str(rohdaten_q.count(row)) + "\\times)\)\n"
                        else:
                            offen_string += "\\item " + row + "\n"
                    offen_string += "}\n"
                    tex_file.write(offen_string)
                elif meta_dict['Type'] == 'Auswahl':
                    pass
                else:
                    print("Der 'Type' " + str(meta_dict['Type'])
                          + " ist bisher nicht vorgesehen in VUKLout. Die Auswertung der Frage wird daher ausgesetzt")
                    continue
            else:
                print("Kein bekannter Befehl: " + style[0])
    return 0


vukl_db = sqlite3.connect(DB_FILE)
with vukl_db:
    vukl_cursor = vukl_db.cursor()
    # # # # # table_names: Enthält die Namen aller Fragebögen
    vukl_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_names_raw = vukl_cursor.fetchall()
    table_names = []
    for row in table_names_raw:
        table_names.append(row[0])
    table_names.remove('meta')
    # # # # # meta_keys: Enthält die Spaltenbezeichnungen der meta Tabelle
    vukl_cursor.execute("SELECT * FROM meta")
    vukl_cursor.fetchone()
    meta_keys = list(map(lambda x: x[0], vukl_cursor.description))
    # # # # # list_veranstaltungen: Enthält eine Liste aller eindeutigen Tupel aus Semester, Vorlesung, Dozent
    set_veranstaltungen = set()
    for table in table_names:
        vukl_cursor.execute("SELECT Periode, Lehrveranstaltung, Nachname, Vorname FROM " + repr(table) + " ")
        set_veranstaltungen = set_veranstaltungen | set(vukl_cursor.fetchall())
    list_veranstaltungen = sorted(set_veranstaltungen)
    # # # # #  list_fragen: Enthält eine Liste aller Fragen die bereits in meta definiert sind
    vukl_cursor.execute("SELECT ID FROM meta")
    list_fragen_raw = vukl_cursor.fetchall()
    list_fragen = []
    for item in list_fragen_raw:
        list_fragen.append(item[0])
    # # # # # list_auswahlfragen
    vukl_cursor.execute("SELECT ID FROM meta WHERE Type='Auswahl'")
    list_auswahlfragen_raw = vukl_cursor.fetchall()
    list_auswahlfragen = []
    for item in list_auswahlfragen_raw:
        list_auswahlfragen.append(item[0])
    # # # # # list_auswahlwerte
    list_auswahlwerte_raw = []
    for frage in list_auswahlfragen:
        vukl_cursor.execute(
            "SELECT `Q_" + part_after_underscore(frage) + "` FROM " + repr(part_before_underscore(frage)) + "")
        list_auswahlwerte_raw.extend(vukl_cursor.fetchall())
    set_auswahlwerte = set()
    for item in list_auswahlwerte_raw:
        set_auswahlwerte.add(item[0])
    list_auswahlwerte = sorted(set_auswahlwerte)

    # # # # # Ausgabe
    print("### \t VUKLout \t ###")
    print("\t Ausgaberoutine von VUKL \n")

    # # # # # Lehrveranstaltungen auswählen
    print("Welche Auswahl von Veranstaltungen möchten Sie auswerten?")
    print("\t any: \t komplettes Semester")
    print("\t   1: \t Alle Veranstaltungen eines Dozenten")
    print("\t   2: \t Alle Veranstaltungen eines Übungsleiters")
    print("\t   3: \t Einzelne Lehrveranstaltungen")
    typ_auswahl = proper_input(3)
    leiter_filter = []
    if typ_auswahl == 0:
        set_semester = set()
        for item in list_veranstaltungen:
            set_semester.add(item[0])
        list_semester = sorted(set_semester)
        semester = choose_from_list(list_semester)
        list_auswahl_lv = []
        for item in list_veranstaltungen:
            if item[0] == semester:
                list_auswahl_lv.append(item)
    if typ_auswahl == 1:
        set_dozent = set()
        for item in list_veranstaltungen:
            set_dozent.add((item[2], item[3]))
        list_dozent = sorted(set_dozent)
        dozent = choose_from_list(list_dozent)
        list_auswahl_lv = []
        for item in list_veranstaltungen:
            if item[2] == dozent[0] and item[3] == dozent[1]:
                list_auswahl_lv.append(item)
    if typ_auswahl == 2:
        # Eine_n Übungsleiter_in $leiter aus allen in der Datenbank auswählen.
        leiter = choose_from_list(list_auswahlwerte)
        list_leiterauswahl = []
        for frage in list_auswahlfragen:
            vukl_cursor.execute("SELECT Periode, Lehrveranstaltung, Nachname, Vorname FROM "
                                + repr(part_before_underscore(frage)) + " WHERE `Q_"
                                + part_after_underscore(frage) + "`='" + leiter + "'")
            list_leiterauswahl.extend(vukl_cursor.fetchall())
        set_leiterauswahl = set(list_leiterauswahl)
        # Liste der Lehrveranstaltungen einschränken auf solche, in denen $leiter eine Übung leitet.
        list_auswahl_lv = sorted(set_leiterauswahl)
        # leiter_filter auf [[frage, leiter] | frage in list_auswahlfragen] setzen.
        for frage in list_auswahlfragen:
            leiter_filter.append([frage, leiter])
    if typ_auswahl == 3:
        list_auswahl_lv = []
        fertig = False
        while not fertig:
            list_auswahl_lv.append(choose_from_list(list_veranstaltungen))
            print("Wollen Sie eine weitere Lehrveranstaltung hinzufügen (y/any)?", end=" ")
            fertig_input = input()
            if fertig_input == 'y' or fertig_input == 'Y':
                fertig = False
            else:
                fertig = True
    keys = ["Periode", "Lehrveranstaltung", "Nachname", "Vorname"]

    # # # # # list_scheme: Enthält das Auswertungsschema als listlist schon passend aufgeteilt
    print("\nDiese Auswertungsschemata stehen zur Verfügung")
    bool_noschemefile = True
    for file in os.listdir(SCHEME_FOLDER):
        if file.endswith('.txt'):
            print("\t", file[:-4])
            bool_noschemefile = False
    if bool_noschemefile:
        print("Es wurde keine 'txt' Datei im Ordner gefunden.")
        sys.exit(0)
    print("Welches Schema soll genutzt werden?", end=" ")
    scheme_file_name = input()
    if scheme_file_name.count('.') == 0:  # falls kein Punkt im Namen enthalten ist, so wird automatisch '.csv'
        #  ergänzt; andere 'Fehler'berichtigung gibt es nicht
        scheme_file_name += '.txt'
    with codecs.open(SCHEME_FOLDER + scheme_file_name, "r", encoding=SCHEME_FILE_ENCODING) as scheme_file:
        list_scheme_raw = list(scheme_file)
        list_scheme = []
        for item_raw in list_scheme_raw:
            item_line = ((item_raw.split("%"))[0]).strip()
            if item_line.startswith("print"):  # falls print wird Rest nicht gesplittet
                list_scheme.append(("print", item_line[6:]))
            elif item_line.startswith("append"):  # dito
                list_scheme.append(("append", item_line[7:]))
            elif item_line.startswith("chapter"):  # dito
                list_scheme.append(("chapter", item_line[8:]))
            elif item_line.startswith("kurzchapter"):  # dito
                list_scheme.append(("kurzchapter", item_line[12:]))
            elif item_line.startswith("section"):  # dito
                list_scheme.append(("section", item_line[8:]))
            elif item_line.startswith("subsection"):  # dito
                list_scheme.append(("subsection", item_line[11:]))
            elif item_line:
                item = []
                item_line_split = item_line.split()
                for cell in item_line_split:
                    if "," in cell:
                        item.append(cell.split(","))
                    else:
                        item.append(cell)
                list_scheme.append(item)

                # # # # # LaTeX Datei schreiben, data_to_tex aufrufen
    with codecs.open(LATEX_OUTPUT_FILE_NAME, "w", encoding=LATEX_OUTPUT_FILE_ENCODING) as tex_file:
        # TeX-Code in tex_file schreiben, hierbei ist list_auswahl_lv eine Liste, deren Einträge die Form
        # [Periode, Lehrveranstaltung, Nachname, Vorname] haben.
        # Ferner ist list_scheme eine Liste, deren Einträge den Zeilen der scheme-Datei entsprechen.
        # leiter_filter enthält Paare an Fragen und Name der_des Übungsleiter_in
        data_to_tex(list_auswahl_lv, list_scheme, leiter_filter)

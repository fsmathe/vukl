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
import time
import readline

####### SETTINGS #######

# input csv file
CSV_DELIMINITER = '|'
CSV_FILE_ENCODING = 'latin-1'
CSV_DIRECTORY = 'csv/'

# database
DB_FILE = 'db/vukl.db'

########################


def cut_quote(any_str):
    if any_str.startswith('"') and any_str.endswith('"'):
        return_str = any_str[1:-1]
    else:
        return_str = any_str
    return return_str


print("### \t VUKLin \t ###")
print("\t Einleseroutine von VUKL \n")

# ask for CSV input file if not passed as command line argument
if sys.argv == 0 and os.path.isfile(sys.argv[0]):
    print("Folgende Dateien wurden im Ordner " + CSV_DIRECTORY + "gefunden:")
    bool_nocsvfile = True
    for file in os.listdir(CSV_DIRECTORY):
        if file.endswith('.csv'):
            print("\t", file)
            bool_nocsvfile = False
    if bool_nocsvfile:
        print("Es wurde keine '.csv' Datei im Ordner gefunden.")
        sys.exit(0)
    csv_file_name = input("\tWelche Datei soll eingelesen werden? ")
    if csv_file_name.count('.') == 0:
        csv_file_name += '.csv'
else:
    csv_file_name = sys.argv[1]
    if os.path.isfile(csv_file_name):
        csv_file_name = csv_file_name.replace(CSV_DIRECTORY, '', 1)
    else:
        print("ERROR: Übergebene Datei existiert nicht!")
        sys.exit(1)
print("Datei " + csv_file_name + " wird eingelesen.")


# # # # # Nachfragen ob Bögen englisch oder deutsch sind
csv_language = input("Sind die Daten von einem deutschen (default) oder englischen Fragebogen (en)? ")
if csv_language != 'en':
    csv_language = 'de'
# # # # # csv in dictlist einlesen
start_time = time.time()
with codecs.open(CSV_DIRECTORY + csv_file_name, "r", encoding=CSV_FILE_ENCODING) as csv_file:
    # hier muss auch ggf die Kodierung der Datei geändert werden zB utf-8
    headline = csv_file.readline()
    headline_split_with_quote = [x.strip() for x in headline.split(CSV_DELIMINITER)]
    headline_split = [cut_quote(x) for x in headline_split_with_quote]
    if headline_split[-1] == "Datensatz-Ursprung" and headline_split[-2] == "Zeitstempel":
        anzahl_fragen = len(headline_split) - 17
    elif headline_split[-1] == "Datensatz-Ursprung":
        anzahl_fragen = len(headline_split) - 16
    else:
        print("Die Kopfzeile der Datei hat als letzten Eintrag nicht 'Datensatz-Ursprung' wie bisher, "
              "da Electric Paper den Export geändert hat. Der Python Code muss an dieser Stelle angepasst werden."
              "Eventuell wurde auch einfach nur nicht das richtige Trennzeichen verwendet (siehe csv_delim in VUKLin).")
        print(headline_split[-1])
        sys.exit(0)
    keys_list = ['Teilbereich', 'Anrede', 'Titel',
                 'Vorname', 'Nachname', 'Lehrveranstaltung',
                 'Lehrveranstaltung_englisch', 'RaumTermin', 'Subdozent',
                 'Periode', 'Studiengang', 'LVTyp',
                 'Vertiefungsgebiet', 'DatensatzUrsprung', 'Bogen']
    for i in range(anzahl_fragen):
        keys_list.append('Q_' + str(i + 1))
    keys = tuple(keys_list)
    dictlist = []
    for row in csv_file:
        csv_datarow_with_quote = [x.strip() for x in row.split(CSV_DELIMINITER)]
        csv_datarow = [cut_quote(x) for x in csv_datarow_with_quote]
        if len(csv_datarow) == len(headline_split):
            csv_to_dict_datarow = [csv_datarow[0], csv_datarow[1], csv_datarow[2], csv_datarow[3], csv_datarow[4],
                                   csv_datarow[5], csv_datarow[5], '', '', csv_datarow[12], '', '', '',
                                   csv_datarow[-1], csv_language + csv_datarow[13]] + csv_datarow[14:14 + anzahl_fragen]
            dictlist.append(dict(zip(keys, tuple(csv_to_dict_datarow))))
        else:
            print("Folgende Zeile hat nicht die passende Anzahl an Feldern/Tabulatoren "
                  "und wird daher nicht verarbeitet:")
            print(row)
end_time = time.time() - start_time

# # # # # [BILD] entfernen
for row in dictlist:
    for key in keys:
        if row[key] == "[BILD]":
            row[key] = ""
print("Hat solange gedauert die Datei in dictlist zu speichern: " + str(end_time))

# # # # # Datenbanktabelle aussuchen
# TODO: create database if not existing
vukl_db = sqlite3.connect(DB_FILE)
with vukl_db:
    vukl_cursor = vukl_db.cursor()
    vukl_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = vukl_cursor.fetchall()
print("\nFolgende Tabellen wurden in der Datenbank bereits gefunden:")
for table in table_names:
    if table[0] != 'meta':
        print("\t", table[0])
if not table_names:
    print("-> Keine Tabelle vorhanden!")
db_table_name = input(
    "Welcher Tabelle sollen die Daten angefügt werden, bzw. wie soll die neue Tabelle genannt werden? ")

# # # # # Neue Tabelle einfügen
if (db_table_name,) not in table_names:
    print("Eine neue Tabelle", db_table_name, "wird erstellt.")
    str_create_table = "CREATE TABLE " + repr(db_table_name) + " ("
    for key in keys:
        str_create_table = str_create_table + " " + key + ",\n"
    str_create_table = str_create_table[0:-2] + ");"
    print(str_create_table)
    vukl_cursor.execute(str_create_table)
    print("Die Metadaten der Fragen müssen allerdings manuell eingetragen werden.")
    print("Starten Sie VUKL anschließend erneut.")
    sys.exit(0)

# # # # # Überprüfung ob die Daten zu den Metainformationen des Fragebogens passen
# TODO SPALTENWEISE Konsistenzprüfung zwischen csv und Tabelle (Anzahl Fragen, Werte in Fragen usw...)

# # # # #
with vukl_db:
    vukl_cursor = vukl_db.cursor()
    vukl_cursor.execute("SELECT ID FROM meta WHERE Type='Auswahl'")
    id_auswahl_fragen_alle = vukl_cursor.fetchall()
    id_auswahl_fragen = []
    for row in id_auswahl_fragen_alle:
        if row[0].startswith(db_table_name):
            id_auswahl_fragen.append(int((row[0].replace(db_table_name, '')[1:])))

# # # # # Für jede Veranstaltung einzeln: Vervollständigung/Korrektur der Daten - ohne Fragen
print("Nun werden die Angaben zu den einzelnen Lehrveranstaltungen "
      "(identischer Name, Dozent und Semester) nacheinander vervollständigt:")
lv_list_raw = []
for row in dictlist:
    lv_quadrupel = (row['Lehrveranstaltung'], row['Vorname'], row['Nachname'], row['Periode'])
    lv_list_raw.append(lv_quadrupel)
lv_list = sorted(list(set(lv_list_raw)), key=lambda k: k[2])

for lv in lv_list:
    lv_dictlist = []
    csv_sheetnumbers_list = []
    db_sheetnumbers_list = []
    for row_nr in range(len(dictlist)):
        if dictlist[row_nr]['Lehrveranstaltung'] == lv[0] and dictlist[row_nr]['Vorname'] == lv[1] \
                and dictlist[row_nr]['Nachname'] == lv[2] and dictlist[row_nr]['Periode'] == lv[3]:
            lv_dictlist.append(dictlist[row_nr])
            csv_sheetnumbers_list.append(dictlist[row_nr]['Bogen'])

    print("\n" + lv[0] + " bei " + lv[1] + " " + lv[2] + " im " + lv[3])
    readline.add_history(lv[0])
    lv_namedeutsch = input("\tLV-Name (deutsch) umbenennen in (leer falls schon korrekt): ")
    if not lv_namedeutsch:
        lv_namedeutsch = lv[0]
    lv_nameenglisch = lv_namedeutsch

    csv_sheetnumbers = set(csv_sheetnumbers_list)
    #    if not len(csv_sheetnumbers) == len(csv_sheetnumbers_list):
    #        print("Die Veranstaltung enthält " + str(len(csv_sheetnumbers_list)-len(csv_sheetnumbers))
    #              + " Duplikate (gleiche Bogennummer)." )
    #        print("Der Import dieser LV wird ausgesetzt.")
    #        #TODO: hier passend aus der for iteration rausgehen, sonst müsste alles im else stattfinden ...
    with vukl_db:
        vukl_cursor = vukl_db.cursor()
        vukl_cursor.execute("SELECT Bogen FROM " + repr(db_table_name) + " WHERE Lehrveranstaltung='" + lv_namedeutsch
                            + "' AND Vorname='" + lv[1] + "' AND Nachname='" + lv[2] + "' AND Periode='" + lv[3] + "'")
        db_sheetnumbers_list_list = vukl_cursor.fetchall()
        for row in db_sheetnumbers_list_list:
            db_sheetnumbers_list.append(row[0])
    db_sheetnumbers = set(db_sheetnumbers_list)

    set_delete = set()
    set_import = set()
    if not db_sheetnumbers:  # means empty set
        print("\tEs liegen noch keine Daten zu dieser Veranstaltung vor, also werden alle Daten importiert")
        set_delete = db_sheetnumbers
        set_import = csv_sheetnumbers
    elif db_sheetnumbers == csv_sheetnumbers:
        print("\tEs liegen bereits exakt diese " + str(len(db_sheetnumbers)) + " Bögennummern zur Veranstaltung vor.")
        print("\ta) Importiere alles neu")
        print("\telse) Importiere nichts")
        input_importoption = input("\tWelche Option soll ausgeführt werden: ")
        if input_importoption == 'a':
            set_delete = db_sheetnumbers
            set_import = csv_sheetnumbers
        else:
            print("\tEs wird nichts importiert")
            set_delete = set()
            set_import = set()
    elif db_sheetnumbers.issubset(csv_sheetnumbers):
        print("Es sind bereits " + str(len(db_sheetnumbers)) + " Bögen zu dieser Veranstaltung vorhanden.")
        print("a) Importiere alles neu")
        print("b) Importiere nur die " + str(len(csv_sheetnumbers) - len(db_sheetnumbers)) + " neuen Bögen")
        print("else) Importiere nichts")
        input_importoption = input("\tWelche Datei soll eingelesen werden? ")
        if input_importoption == 'a':
            set_delete = db_sheetnumbers
            set_import = csv_sheetnumbers
        elif input_importoption == 'b':
            set_delete = set()
            set_import = csv_sheetnumbers - db_sheetnumbers
        else:
            print("Es wird nichts importiert")
    elif not db_sheetnumbers.intersection(csv_sheetnumbers):
        print("Es liegen bereits Daten zur Veranstaltung vor, aber es gibt keine Überschneidung, "
              "also werden die Daten importiert.")
        set_delete = db_sheetnumbers
        set_import = csv_sheetnumbers
    else:
        print("Es liegen bereits Fragebögen zu dieser Veranstaltung vor, die nicht in der 'csv' enthalten sind "
              "und der Schnitt ist auch nicht leer. Wie kann das denn passieren?")
        print("Es wird nichts importiert. Wahrscheinlich ist das die falsche Veranstaltung")

    # # # # # lv_dictlist anpassen
    lv_dictlist_short = [x for x in lv_dictlist if x['Bogen'] in set_import]
    lv_dictlist = lv_dictlist_short

    # # # # # Bögen aus DB rauslöschen
    for bogen_nummer in set_delete:
        str_exec_delete = "DELETE FROM " + repr(db_table_name) + " WHERE Lehrveranstaltung='" + lv_namedeutsch \
                          + "' AND Vorname='" + lv[1] + "' AND Nachname='" + lv[2] \
                          + "' AND Periode='" + lv[3] + "' AND Bogen IN ('"
        for item in set_delete:
            str_exec_delete = str_exec_delete + item + "','"
        str_exec_delete = str_exec_delete[:-2] + ")"
        vukl_cursor.execute(str_exec_delete)

    # print("\tLV-Name (englisch) umbenennen in (leer falls schon korrekt): ", end="")
    #    lv_nameenglisch = input()
    #    if not lv_nameenglisch:
    #        lv_nameenglisch = lv[0]
    # ZEIT#    print("\tTermine der Vorlesung (Format: Montag 8:15 48-210, Dienstag 10:00 46-268): ", end="")
    #  TODO Falls Übung sollten da eigentlich die anderen Details rein, kA wie die sinnvoll ausgelesen werden
    # ZEIT#    lv_raumtermin = input()
    lv_subdozent = input("\tLV hatte Subdozent: ")
    # ZEIT#    print("\tLV ist im Studiengang: ", end="") #*# mit Auswahl!
    # ZEIT#    lv_studgang = input()
    # ZEIT#    print("\tLV hat den Typ: ", end="") #*# mit Auswahl!
    # ZEIT#    lv_lvtyp = input()
    # ZEIT#    print("\tLV gehört zur Vertiefung: ", end="") #*# mit Auswahl!
    # ZEIT#    lv_vert = input()
    for row in lv_dictlist:
        row['Lehrveranstaltung'] = lv_namedeutsch
        row['Lehrveranstaltung_englisch'] = lv_nameenglisch
        row['Subdozent'] = lv_subdozent
    # ZEIT#        row['RaumTermin'] = lv_raumtermin
    # ZEIT#        row['Subdozent'] = lv_subdozent
    # ZEIT#        row['Studiengang'] = lv_studgang
    # ZEIT#        row['LVTyp'] = lv_lvtyp
    # ZEIT#        row['Vertiefungsgebiet'] = lv_vert

    for auswahl_frage in id_auswahl_fragen:
        auswahl_frage_intwerte_set = set()
        for row in lv_dictlist:
            auswahl_wert = row["Q_" + str(auswahl_frage)]
            if auswahl_wert.isdigit():
                auswahl_frage_intwerte_set.add(int(auswahl_wert))
        auswahl_frage_intwerte = sorted(list(auswahl_frage_intwerte_set))
        print("\tMit welchem Text sollen die Werte in Frage '" + str(auswahl_frage) + "' ersetzt werden?")
        for wert in auswahl_frage_intwerte:
            ersatz_text = input("\t\tWert " + str(wert) + ": ")
            if not ersatz_text:
                ersatz_text = wert
            for row in lv_dictlist:
                if row["Q_" + str(auswahl_frage)] == str(wert):
                    row["Q_" + str(auswahl_frage)] = ersatz_text
    str_import_dict = "INSERT INTO " + repr(db_table_name) + " ("
    # Get list of question IDs like (Q_1, Q_2, …, Q_17, Q_18-de, Q_19, …)
    vukl_cursor.execute("SELECT replace(ID,'" + db_table_name + "','Q') FROM meta " + \
                        # Find non-standard question IDs that look like 'Q_18-de' …
                        "WHERE ID GLOB '" + db_table_name + "_*-" + csv_language + \
                        # as well as standard question IDs like Q_18 but not Q_18-en.
                        "' OR ID GLOB '" + db_table_name + "_*' AND NOT ID GLOB '" + db_table_name + "_*-*'")
    question_names = vukl_cursor.fetchall()
    if len(question_names) != anzahl_fragen:
        print('Anzahl der Fragen stimmt nicht mit Angaben in meta-Tabelle überein')
        exit()
    for key in keys_list[0:-anzahl_fragen]:
        str_import_dict = str_import_dict + "`" + key + "`,"
    for key in question_names:
        str_import_dict = str_import_dict + "`" + key[0] + "`,"
    str_import_dict = str_import_dict[0:-1] + ") VALUES ("
    for key in keys:
        str_import_dict = str_import_dict + "?" + ","
    str_import_dict = str_import_dict[0:-1] + ")"

    list_list_from_dictrow = []
    for row in lv_dictlist:
        list_from_dictrow = []
        for key in keys:
            list_from_dictrow.append(row[key])
        # print(str_import_dict_intro + str_import_dict_row)
        if row['Bogen'] in set_import:
            list_list_from_dictrow.append(list_from_dictrow)
    vukl_cursor.executemany(str_import_dict, list_list_from_dictrow)
    vukl_db.commit()

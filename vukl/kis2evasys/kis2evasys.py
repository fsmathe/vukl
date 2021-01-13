#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
KIS2EvaSys - Umfragen aus KIS-Veranstaltungen anlegen
"""

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

__author__ = "Clemens Reibetanz, Christian De Schryver"

# Bitte die 3 Werte eintragen
SEMESTER = "[SS19]"
# 27=WS15/16, 28=SS16, 29=WS16/17, 30=SS17, 31=WS17/18, 32=SS18, 33=WS18/19, 34=SS19
PERIOD = 34
# URL von KIS -> Studiengänge und Veranstaltungen -> Elektrotechnik und Informationstechnik -> Elektrotechnik und Informationstechnik -> Dozent
URL = 'https://www.kis.uni-kl.de/campus/all/eventlist.asp?mode=field&gguid=0x090A152C497B43FE801EDB13F2F5CA60&tguid=0x20A24741AF3347FEB6943B4BA195534F'
# KIS Zeichensatz wie im HTML-Meta-Tag festgelegt
URLENCODING = "iso-8859-1"

# directory for generated output files
DATA_DIRECTORY = "data/"
# generated file for EvaSys import
EVASYS_IMPORT_FILENAME = DATA_DIRECTORY + "evasys-import-raw.csv"
# file encoding for generated EvaSys import file
EVASYS_IMPORT_FILE_ENCODING = "utf-8"
# generated list of all courses
COURSELIST_FILENAME = DATA_DIRECTORY + "vorlesungsliste.csv"
# file encoding for course list
COURSELIST_FILE_ENCODING = "utf-8"

"""
# einfach die 3 Werte oben für das aktuelle Semester aktualisieren
# dann dieses Script ausführen

# die herausfallende Datei dann wie folgend beschrieben bei befragung.uni-kl.de importieren

# in EvaSys
# Teilbereiche -> Gesamtübersicht -> Elektro- und Informationstechnik
# ganz unten "Nutzerliste aus CSV-Datei importieren: generierte auswählen und importieren

# Man muss normalerweise noch etwas nacharbeiten und Übungsleiter etc. eintragen, da die nie richtig im KIS stehen
# Mehr als 1 Dozent geht auch nicht, da das anscheinend vom EvaSys nicht wirklich unterstützt wird
# Am besten das geänderte einfach in die CSV-Datei einragen bevor es ins EvaSys geladen wird.
# Das EvaSys bietet nach dem Import auch noch die Möglichkeit Dinge zu ändern

# Desweiteren fällt auch noch eine Datei vorlesungen.csv raus, die eine Liste der Vorlesungen, der Zeiten und der Räume enthält

# Hier geht das Programm nun los, es zeigt den Fortschritt in der Konsole
# Es kann schon mal 5 Minuten dauern bis das durchgelaufen ist
# Alles wird mit regulären Ausdrücken gemacht, sicher nicht optimal, aber immerhin eine Lösung
"""

import re
import urllib.request
import os


# our datastructure
class Datum():
	def __init__(self, tag, beginn, ende, raum):
		self.tag = tag
		self.beginn = beginn
		self.ende = ende
		self.raum = raum


class Vorlesung():
	def __init__(self, name, dozent, mail, code, type, sprache, url, datum):
		self.name = name
		self.dozent = dozent
		self.mail = mail
		self.code = code
		self.type = type
		self.sprache = sprache
		self.url = url
		self.datum = datum


''' Skript '''

# create data directory if not existing
data_directory = os.path.dirname(EVASYS_IMPORT_FILENAME)
if not os.path.exists(data_directory):
	os.makedirs(data_directory)

# list of events for EIT
print("Reading KIS - URL: " + URL)
with urllib.request.urlopen(URL) as url:
	text = url.read().decode(URLENCODING)

# get everything inside the list of events for EIT
re_rows = re.findall(r"<tr class=\"blue[12]\">(.*?)</tr>", text, re.S)

# get all lectures and exercises that are EIT
re_excerciseOrLecture = []
for x in re_rows:
	if re.search(r"eventListTypeCol.*?>(.*?[VÜS])", x, re.S) and re.search(
			r"<td name=\"eventListLVNRCol\".*?>((?:EIT).*?)<", x, re.S):
		re_excerciseOrLecture.append(x)

# for all of these events do the following
lecture = []
i = 0
for x in re_excerciseOrLecture:
	# get the name of the lecture and the lecturer and if it contains an excercise
	nameOfLecture = re.search(r"eventlink.*?>(.*?)</a>", x, re.S)
	nameOfLecturer = re.search(r"eventListLecturerCol.*?>.*?>(.*?)</a>", x, re.S)
	codeOfLecture = re.search(r"<td name=\"eventListLVNRCol\".*?>(.*?)<img", x, re.S)
	typeOfLecture = re.search(r"eventListTypeCol.*?>(.*?)</td>", x, re.S)

	if nameOfLecturer:
		nameOfLecturer = nameOfLecturer.group(1)
	else:
		nameOfLecturer = ''
	if nameOfLecture:
		nameOfLecture = nameOfLecture.group(1)
	else:
		nameOfLecture = ''
	if codeOfLecture:
		codeOfLecture = codeOfLecture.group(1) + "-" + SEMESTER  # needs to be unique
	else:
		codeOfLecture = ''
	if typeOfLecture:
		typeOfLecture = typeOfLecture.group(1)
	else:
		typeOfLecture = ''

	# find out the email of the lecturer and therefore open the subpage
	urlofLecturer = re.search(r"<td name=\"eventListLecturerCol\".*?><.*?href=\"(.*?)\"", x, re.S)
	if urlofLecturer:
		with urllib.request.urlopen('http://www.kis.uni-kl.de/campus/all/' + urlofLecturer.group(1)) as url:
			textofLecturerSubpage = url.read().decode(URLENCODING)
		mailOfLecturer = re.search(r"E-Mail:<\/td>.*?>.*?>(.*?(?:\[at\]).*?)<\/a>", textofLecturerSubpage, re.S)
		if mailOfLecturer:
			mailOfLecturer = mailOfLecturer.group(1)
			mailOfLecturer = mailOfLecturer.replace("[at]", "@")
		else:
			mailOfLecturer = ''
	else:
		mailOfLecturer = ''

	# find out when and where the event is, therefore open the subpage
	urlofTimeAndDate = 'http://www.kis.uni-kl.de/campus/all/' + re.search(r"eventlink.*?href=\"(.*?)\">", x,
	                                                                      re.S).group(1)
	urlOfLecture = urlofTimeAndDate
	with urllib.request.urlopen(urlofTimeAndDate) as url:
		textOfTimeAndDateSubpage = url.read().decode(URLENCODING)
	# get the language
	languageOfLecture = re.search(r"Unterrichtssprache:.(.*?)</td>", textOfTimeAndDateSubpage, re.S)
	if languageOfLecture:
		languageOfLecture = languageOfLecture.group(1)
	else:
		languageOfLecture = ''
	# get out all dates
	re_dates = re.findall(r"<tr class=\"hierarchy4\">(.*?)</tr>", textOfTimeAndDateSubpage, re.S)
	# in these dates first of all find all important columns
	date = []
	for d in re_dates:
		re_times_room_columns = re.findall(r"<td class=\"default\">(.*?)</td>", d, re.S)
		if re_times_room_columns:
			day = re.search(r"((?:Mo|Di|Mi|Do|Fr|Sa|So))", re_times_room_columns[0], re.S)
			starttime = re.search(r"(\d\d:\d\d)", re_times_room_columns[1], re.S)
			endtime = re.search(r"(\d\d:\d\d)", re_times_room_columns[3], re.S)
			room = re.search(r"a href.*?>(.*?)<\/a>", re_times_room_columns[4], re.S)
			if day:
				day = day.group(1)
			else:
				day = ''
			if starttime:
				starttime = starttime.group(1)
			else:
				starttime = ''
			if endtime:
				endtime = endtime.group(1)
			else:
				endtime = ''
			if room:
				room = room.group(1)
			else:
				room = ''
			date.append(Datum(day, starttime, endtime, room))

			print("* " + nameOfLecture + " | " + nameOfLecturer + " | " + typeOfLecture)
	lecture.append(
		Vorlesung(nameOfLecture, nameOfLecturer, mailOfLecturer, codeOfLecture, typeOfLecture, languageOfLecture,
		          urlOfLecture, date))
	i = i + 1
	print
	i, '/', len(re_excerciseOrLecture)
print("Finished grabbing and reading KIS...")
print()

# write complete list of lectures
file = open(COURSELIST_FILENAME, "w", encoding=COURSELIST_FILE_ENCODING)
for x in lecture:
	line = "\"%s\";\"%s\";\"%s\";\"%s\";\"%s\"" % (x.url, x.name, x.dozent, x.type, x.sprache)
	for y in x.datum:
		line = "%s;\"%s\";\"%s\";\"%s\";\"%s\"\n" % (line, y.tag, y.beginn, y.ende, y.raum)
		file.write(line)
		line = "\"\";\"\";\"\";\"\";\"\""
file.close()
print("File " + COURSELIST_FILENAME + " written, Encoding: " + COURSELIST_FILE_ENCODING)

# write output file for EvaSys import
with open(EVASYS_IMPORT_FILENAME, "w", encoding=EVASYS_IMPORT_FILE_ENCODING) as file:
	file.write(
		"usertype|projectname|modulename|professional_title|title|firstname|surname|email|course_name|course_code|course_location|program_of_studies|course_type|course_participants|user_external_id|course_external_id|secondary_instructor_external_ids|module_course_position|module_course_main|course_period\n")
	for x in lecture:
		if x.dozent:
			# seminars
			if "S" in x.type:
				line = "\"dozent\"||||||\"%s\"|\"%s\"|\"%s [Seminar] %s\"|\"%s-S\"|\"\"|\"EIT\"|\"2\"|\"0\"|\"\"|\"\"|\"\"|||\"%s\"|\n" % (
					x.dozent, x.mail, x.name, SEMESTER, x.code, PERIOD)
				file.write(line)
			# not a seminar
			else:
				line = "\"dozent\"||||||\"%s\"|\"%s\"|\"%s %s\"|\"%s\"|\"\"|\"EIT\"|\"1\"|\"0\"|\"\"|\"\"|\"\"|||\"%s\"|\n" % (
					x.dozent, x.mail, x.name, SEMESTER, x.code, PERIOD)
				file.write(line)
				if "Ü" in x.type:
					line = "\"dozent\"||||||\"%s\"|\"%s\"|\"%s [Übung] %s\"|\"%s-Ü\"|\"\"|\"EIT\"|\"4\"|\"0\"|\"\"|\"\"|\"\"|||\"%s\"|\n" % (
						x.dozent, x.mail, x.name, SEMESTER, x.code, PERIOD)
					file.write(line)
print("File " + EVASYS_IMPORT_FILENAME + " written, Encoding: " + EVASYS_IMPORT_FILE_ENCODING)

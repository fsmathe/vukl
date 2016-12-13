#!/usr/bin/python3
'''
    sets correct values for full names and titles in EvaSys import file
'''

import csv

# generated output file from kis2evasys
INPUT_FILENAME = "data/evasys.csv"
# file encoding for input file
INPUT_FILE_ENCODING = "utf-8"

# target filename for updated names and titles
OUTPUT_FILENAME = "data/final.csv"
# desired file encoding for output file
OUTPUT_FILE_ENCODING = "latin-1"

# a fresh export of all users from EvaSys with required personal data
EXPORT_FILENAME = "data/evasys-export.csv"
# file encoding for EvaSys export file
EXPORT_FILE_ENCODING = "utf-8"

# determine CSV dialect of input file
with open(INPUT_FILENAME, "r", encoding=INPUT_FILE_ENCODING) as inputFile:
	dialect = csv.Sniffer().sniff(inputFile.read(1024))

# force quotes everywhere
dialect.quoting = csv.QUOTE_ALL

# add additional information for each person
with open(INPUT_FILENAME, "r", encoding=INPUT_FILE_ENCODING) as inputFile:
	inputReader = csv.reader(inputFile, dialect)
	with open(OUTPUT_FILENAME, "w", encoding=OUTPUT_FILE_ENCODING) as outputFile:
		outputWriter = csv.writer(outputFile, dialect)

		for row in inputReader:
			rowNew = row

			lastName = row[6]
			lastNameFound = False
			# search for last name in export file
			with open(EXPORT_FILENAME, "r", encoding=EXPORT_FILE_ENCODING) as exportFile:
				nameReader = csv.reader(exportFile, dialect)
				for nameRow in nameReader:
					if nameRow[6] == lastName:
						row[3] = nameRow[3]  # title
						row[4] = nameRow[4]  # Herr / Frau
						row[5] = nameRow[5]  # first name
						lastNameFound = True
						break

				if lastNameFound == False:
					print(lastName + " not found in EvaSys export --> needs to be updated manually")

			outputWriter.writerow(rowNew)

#!/usr/bin/python3
'''
    sets correct values for full names and titles in EvaSys import file
'''

import csv

# generated output file from kis2evasys
INPUT_FILENAME = "evasys.csv"
# a fresh export of all users from EvaSys
EXPORT_FILENAME = "export.csv"
# target filename for updated names and titles
OUTPUT_FILENAME = "final.csv"

# determine CSV dialect
with open(INPUT_FILENAME, "rb") as inputFile:
    dialect = csv.Sniffer().sniff(inputFile.read(1024))
# force quotes
dialect.quoting = csv.QUOTE_ALL


with open(INPUT_FILENAME, "rb") as inputFile:
    inputReader = csv.reader(inputFile, dialect)
    with open(OUTPUT_FILENAME, "rw") as ouputFile:
        outputWriter = csv.writer(open(OUTPUT_FILENAME, "wb"), dialect)

        for row in inputReader:
            rowNew = row
    
            lastName = row[6]
            lastNameFound = False
            # search for last name in export file
            with open(EXPORT_FILENAME, "rb") as exportFile:
                nameReader = csv.reader(open(EXPORT_FILENAME, "rb"), dialect)
                for nameRow in nameReader:
                    if nameRow[6] == lastName:
                        row[3] = nameRow[3] # title
                        row[4] = nameRow[4] # Herr / Frau
                        row[5] = nameRow[5] # first name
                        lastNameFound = True
                        break

                if lastNameFound == False:
                    print (lastName + " not found in EvaSys export --> needs to be updated manually")
            
            outputWriter.writerow(rowNew)

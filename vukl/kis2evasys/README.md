KIS2EvaSys - Umfragen aus KIS-Veranstaltungen anlegen
===

Dieses Skript parst die aktuelle Veranstaltungsliste aus dem KIS und erzeugt eine Importdatei für EvaSys, die die entsprechenden Umfragen anlegt.

## Benutzung
1. zuerst kis2evasys.py anpassen und die Werte oben richtig setzen
2. Skript ausführen mit `python3 kis2evasys` --> erzeugt Importdatei für EvaSys mit Rohdaten
3. diese Datei prüfen und ggfs. ergänzen (fehlende Veranstaltungen, Übungsleiter/innen, ...)
4. Liste aller Nutzer + Veranstaltungen aus EvaSys exportieren
5. replaceNames.py: anpassen und Werte richtig setzen
6. replaceNames.py ausführen mit `python3 replaceNames.py` --> ersetzt Nachnamen durch volle EvaSys-Details und erzeugt finale Tabelle für EvaSys-Import

## Contributors
* Christian De Schryver <schryver@eit.uni-kl.de>
* Clemens Reibetanz

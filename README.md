vukl
===
Project to pretty print evaluations.

Instructions
===
Generating the publishable pdf files using vukl needs two major steps:
* Export the raw evaluation data from EvaSys into csv files. Parse these files and save them in a lightSQL database with ``VUKLin.py``.
* Creating a tex file with graphics for the chosen evaluations using ``VUKLout.py``. Compile ``tex/aushang/aushang.tex`` or ``tex/auswertung/auswertung.tex`` to generate a pdf file.

* subproject kis2evays: creates an import file for EvaSys from the current courses listed in the KIS system

Documentation
===
For further information read https://github.com/fsmathe/vukl/wiki.

\ProvidesClass{vukl}[2015/06/21 v1.0.1]
\DeclareOption{gray}{\PassOptionsToPackage\CurrentOption{xcolor}%
	\graytrue % Für Auswirkung siehe Implementation von \badgoodcolor
}
\DeclareOption{oneside}{\PassOptionsToClass\CurrentOption{scrbook}%
}
\DeclareOption{aushang}{%
	\aushangtrue
}
\DeclareOption{kurz}{%
	\kurztrue
	\PassOptionsToClass{oneside}{scrbook}%
	%\PassOptionsToClass{oneside,headings=normal}{scrbook}% etwas kleinere Überschriften
}
\DeclareOption{*}{\PassOptionsToClass\CurrentOption{scrbook}}%
\newif\ifgray
\newif\ifkurz
\newif\ifaushang
\ProcessOptions
\LoadClass[fontsize=9pt,twocolumn,DIV=1]{scrbook}
\RequirePackage[T1]{fontenc}
\RequirePackage[utf8x]{inputenc}
\PreloadUnicodePage0
\RequirePackage[ngerman]{babel}
\RequirePackage{geometry}
\geometry{a4paper,tmargin=3.5cm,bmargin=2cm,lmargin=2cm,rmargin=2cm,headheight=1cm,headsep=1cm,footskip=1cm}
\setcounter{secnumdepth}{-1}
\setcounter{tocdepth}{1}
\makeatletter
% Use default title if none given
\def\default@title{\@latex@error{No \noexpand\title given}\@ehc}
\ifx\@title\default@title
\title{Vorlesungsumfrage Mathematik}
\fi
\RequirePackage[%
	pdftitle={\@title},%
	pdfauthor={Fachschaft Mathematik}%
]{hyperref}
\RequirePackage{ragged2e}
\RequirePackage{xcolor}
%\RequirePackage{ae,aecompl}
\RequirePackage{amsmath,amssymb}
%\RequirePackage{titlesec} %Nichtnummerierung der Kapitel --> zerschießt hyperref
\RequirePackage{scrpage2} %Seitennummerierung
\RequirePackage{tikz}
\usetikzlibrary{external}
\tikzexternalize[prefix=tikz/]
\usetikzlibrary{calc}
\RequirePackage[nohints]{minitoc}
\RequirePackage{xspace}

\hyphenation{Lern-er-folg Prä-senz-auf-ga-ben}


%%%% Gliederung und Seitenzahlen
% Statt die Seitenzahlen zu Beginn eines Kapitels herabzusetzen wird nur die Ausgabe der Seitenzahlen manipuliert, die PDF-Lesezeichen bleiben hiervon unberührt, insbesondere freut sich hyperref darüber
% tableofcontents- und minitoc-Einstellungen
\AtBeginDocument{%
	\renewcommand{\contentsname}{\@title}% setzt Name des Inhaltsverzeichnisses
	\markboth{\@title}{}
	\manualmark
	\markboth{\@title}{}
	\tableofcontents
	\automark[section]{chapter}
%
	\tikzset{external/mode={graphics if exists}}
}
\renewcommand\mtctitle{}%minitoc-Titel
\mtcsetrules{*}{off}
\renewcommand\mtcfont{\normalfont}
\renewcommand\mtcSfont{}
\dominitoc% notwendig für minitoc

\let\raggedsection\RaggedRight % bessere Silbentrennung in Überschriften, sinnvoll bei schmalen Spalten
\let\section@vu\section
\let\chapter@vu\chapter
\ifkurz % für Kurzfassung
	\@at@twocolumntrue % macht irgendwie, dass alles zweispaltig wird
	\renewcommand\chapterheadstartvskip{}% entfernt Abstand über Kapitelüberschriften
	\def\kurzchapter{\chapter}% Alias
\fi
\ifaushang % für Aushang
	% In der Aushangversion sollen insbesondere die Seitenzahlen zurückgesetzt werden,
	% um trotzdem noch hyperref nutzen zu können, wird aber nur die Anzeige der Seitenzahlen zurechtgebogen,
	% der eigentliche counter page bleibt bestehen.
	% \chapter, \section
	\renewcommand\chapter{%
		\setchapterpreamble{% nach Beginn des neuen Kapitels …
			\setchapterpage{\arabic{page}}% Seitenzahl speichern und …
			\minitoc % Inhaltsverzeichnis ausgeben
			\gdef\pagemark{\pagecalc{\arabic{page}}\thechapterpage}% berechnet Seitenzahl und gibt sie aus, wird in Kolumnentitel genutzt
		}%
		\chapter@vu
	}%
	\renewcommand\section{\cleardoublepage\section@vu}% Seitenumbruch vor \section
	% Rechnen mit Seitenzahlen
	\newcounter{pagecalc}%
	\newcommand\setchapterpage[1]{% wird zu Kapitelbeginn aufgerufen mit der Seitenzahl als Argument
		\setcounter{pagecalc}{#1}%
		\addtocounter{pagecalc}{1}%
		\xdef\chapterstartpage{\arabic{pagecalc}}% Seitennummer vor Kapitelbeginn
	}%
	\newcommand\pagecalc[1]{%{Seitenzahl von Abschnittbeginn} wird für den minitoc-Eintrag genutzt
		\setcounter{pagecalc}{-\chapterstartpage}% bestimmt Seitenzahl relativ zu Kapitelbeginn
		\addtocounter{pagecalc}{#1}%
	}%
	\newcommand\thechapterpage{\ifnum\value{pagecalc}>0 \arabic{pagecalc}\fi}
	\let\tableofcontents@vu\tableofcontents
	\def\tableofcontents{%
		\tableofcontents@vu
		% Folgende Zeilen bauen die Anzeige in den Inhaltsverzeichnissen korrekt
		\let\@dottedtocline@vu\@dottedtocline
		\renewcommand\@dottedtocline[5]{\pagecalc{\gobble@reset@font##5}\@dottedtocline@vu{##1}{##2}{##3}{##4}{\reset@font\arabic{pagecalc}}}% wird bei jedem Inhaltsverzeichniseintrag aufgerufen
		\let\l@chapter@vu\l@chapter
		\renewcommand\l@chapter[2]{\setchapterpage{\gobble@reset@font##2}\l@chapter@vu{##1}{}}% wird bei einem Kapiteleintrag im Inhaltsverzeichnis aufgerufen
	}%
	% Stupides Zeugs, je nachdem, ob danach \reset@font folgt, resultiert dies in …
	% \gobble@reset@font\reset@font#1 ->.
	% \gobble@reset@font ->.
	% hierdurch wird nur die Seitenzahl zur weiteren Berechnung von \pagecalc genutzt
	\newcommand\gobble@reset@font[1]{\gobble@reset@font@#1\@gobblethree\reset@font{#1}}
	\def\gobble@reset@font@#1\reset@font#2{#2}
\else
	\renewcommand\chapter{%
		\renewcommand\section{% erste \section nach \chapter wird ganz normal dargestellt …
			\renewcommand\section{% definiert aber alle folgenden \section so um, dass sie auf einer neuen Seite anfangen
				\clearpage\section@vu
			}\section@vu
		}% kein Seitenumbruch vor \section
		\chapter@vu
	}
\fi
\newcommand\fragestellung[1]{% zentriert, da textähnlich
	\let\raggedsection\relax
	\subsubsection{#1}%
	\let\raggedsection\RaggedRight
}

%%%% Kopfzeile
\clearscrheadfoot
\pagestyle{scrheadings}
\renewcommand\chapterpagestyle{scrheadings}
\setheadtopline{1pt}
\setheadsepline{.4pt}
% Da \leftmark mitunter breiter ist als eine halbe Seite wird dies etwas unkonventionell gelöst
\newlength\pagelabelwidth
\settowidth\pagelabelwidth{000}
\addtolength\pagelabelwidth{1em}
\newcommand\pagelabel{\makebox[\pagelabelwidth][r]{\pagemark}}
\chead{\leftmark\hfill\rightmark\pagelabel}% oder halt so, was auch immer gefällt

%%%% Stiländerungen
\newcommand\listenlaengen{%
	\setlength\itemsep{0pt}%
	\setlength\parsep{0pt}%
}

%%%% Makros zur Verwendung in Freitexten
\newcommand\quot[1]{\glqq#1\grqq}
\newcommand\zB{z.\,B.\xspace}

%%%% Hilfsmakros
%- \expandafter<token1><token2> resultiert in <token1><Expansion von token2>, entsprechend auch
% \expandafter\expandafter\expandafter<token1><token2> wird zu
% \expandafter<Expansion von \expandafter<token1><token2>> wird zu
% \expandafter<token1><Expansion von token2> wird zu
% <token1><Expansion der Expansion von token2>
% Beispiel: Für \newcommand\foo{FOO} resultiert \expandafter\example\expandafter{\foo} in \example{FOO}
%- \popelement speichert erstes Element aus \list in \result und entfernt es aus \list
\newcommand\popelement[2]{%{\result}{\list}
	% \list ist zuvor von der Form {arg1}{arg2}…{argn} und danach {{arg2}…{argn}}%
	% bzw. {argn} falls 2=n -- ja, das ist ein dokumentierter Bug, hier aber nich besser nötig
	% \result wird zu arg1
	\expandafter\popelement@#2\popelement@delim{#1}{#2}% expandiert \list zu {arg1}…{argn}
}
\def\popelement@#1#2\popelement@delim#3#4{\def#3{#1}\def#4{#2}}%{arg1}{arg2}…{argn}{\result}{\list}
%- \addtoken ergänzt #2 an das Ende von #1, ohne eins davon zu expandieren
\newcommand\addtoken[2]{%{\macro}{arg} setzt \macro auf <expansion>arg1, wenn \macro zu <expansion> expandiert
	\expandafter\def\expandafter#1\expandafter{#1#2}%
}

\newcommand\@swap[2]{#2#1}
% Ersetzt „\expandafterargument{foo}\stuff“ durch „foo<einmalige Expansion von \stuff>“
\newcommand\expandafterargument[2]{%
	\expandafter\@swap\expandafter{#2}{#1}}

%%% Makros für Nutzung von TikZ-Externalize
% Setzt den Dateinamen des nächsten Bilds auf den Hash von #1
\newtoks\hashtoks
\newcommand\setnextfilenametohash[1]{%
	\hashtoks{#1}%
	\tikzsetnextfilename{\expandafter\hextolower\pdfmdfivesum{\the\hashtoks}Z}}%
% Konvertiert A-F in a-f in einem durch Z beschränkten String, das Z wird entfernt
	\newcommand\hextolower[1]{%
	\if#1Z%
	\else\if#1Aa%
	\else\if#1Bb%
	\else\if#1Cc%
	\else\if#1Dd%
	\else\if#1Ee%
	\else\if#1Ff%
		\else#1%
	\fi\fi\fi\fi\fi\fi
	\expandafter\hextolower
	\fi
}

%%%% Ausgabe mittels \skala, \single, \offen
% Konstanten
\newcommand\histogramborderleftwithtext {     1-1.5}
\newcommand\histogramborderrightwithtext{\range+1.5}
\newcommand\histogramborderleft {     1-1}
\newcommand\histogramborderright{\range+1}
\newcommand\histogrambordercaptionoffset{.5} % Für Textabstand bei \semester
\newcommand\histogrambarwidth{0.45}
\newcommand\histogramheight{3.2}
\newcommand\histogramborderheight{4}
\newcommand\histograminnersep{3}
\pgfkeyssetvalue{/pgf/number format/precision}{2} % Runden auf 2 Stellen genau für arithmetisches Mittel
%% Variablen
\newcommand\histogram{}% Hier werden die dynamischen Inhalte des Histogramms eingespeichert
\newcounter{skalaposition}% Index des momentan bearbeiteten Eintrags
\newcounter{numberOfAll}% Summe aller Einträge
\newcounter{weightedSum}% gewichtete Summe -> Durchschnitt = weightedSum/numberOfAll
%color: histogramcolor
%% Farbe
%- \positiontocolor gibt {r,g,b} zurück mit r,g,b von 0 bis 1, wobei #1 zwischen -1 und 1 liegt und #2 angibt, welche Antwort positiv ist
\newcommand*\positive{}
\newcommand*\positivecenter{C}
\newcommand*\positiveneutral{N}
\ifgray
	\newcommand\badgoodcolor[1]{%{relative position from -1 to 1}
		\pgfmathparse{{0,0,(1-#1)/2}}%hsb
	}
\else
	\newcommand\badgoodcolor[1]{%{relative position from -1 to 1}
		\pgfmathparse{{%hsb
			(#1+1)/6,%
			(cos(360*#1)+3)/4,% 360=2*pi r
			1%
			%
			%%min(1,max(0,sqrt(2) * (sin(pi/2*(-#1+.5))-sin(pi*-#1)/2))), %red
			%min(1,1-4/5*#1),% red
			%%max(0,.08*(3*(#1-.5)^3-28*(#1-.5))), % red
			%%min(1,max(0,sqrt(2) * (sin(pi/2*(#1+.5)) - sin(pi*#1)/2))), %green
			%min(1,1+4/5*#1),% green
			%%max(0,.08*(3*(.5-#1)^3-28*(.5-#1))), % green
			%(-88*#1^2+94)*#1^2/30% blue % niemand hat vor, sinnlose Polynom-Interpolation zu verwenden
			%%2/3*sin(#1*2.56)^2% blue
		}}%
	}
\fi
\newcommand\positiontocolor[2]{%{relative position from -1 to 1}{macro expanding to positive}
	\ifx#2\positivecenter % Falls der beste Wert in der Mitte liegt
		\pgfmathparse{1-abs(2*#1)}%
		\badgoodcolor{\pgfmathresult}%
		\expandafter\positiontocolor@\pgfmathresult % speichert geklammerte Rückgabe von \pgfmathresult als Farbe, zu \expandafter siehe Erklärung im Abschnitt zu Hilfsmakros
	\else\ifx#2\positiveneutral % Falls keine Bewertung vorliegt
		\convertcolorspec{cmyk}{.4,.12,0,.16}{rgb}{\histogramcolor@color}% 60% von TU-blau -- pgf hat wohl Probleme mit cmyk, daher zuerst konvertieren in rgb
		\histogramcolor@save
		%\def\pgfmathresult{{.777}{1}{.56}}% TU-blau
	\else
		\badgoodcolor{#1}%
		\expandafter\positiontocolor@\pgfmathresult % speichert geklammerte Rückgabe von \pgfmathresult als Farbe
	\fi\fi
}
%\newcommand\positiontocolor@[3]{\definecolor{histogramcolor}{rgb}{#1,#2,#3}}%
\newcommand\positiontocolor@[3]{%
	\convertcolorspec{hsb}{#1,#2,#3}{rgb}{\histogramcolor@color}% pgf hat wohl Probleme mit hsb, daher zuerst konvertieren in rgb
	\histogramcolor@save
}%
\newcommand\histogramcolor@save{\definecolor{histogramcolor}{rgb}{\histogramcolor@color}}
\newcommand\histogramcolor[3]{%{range}{positive}{position}
	\pgfmathparse{2*(#3-1)/(#1-1)-1}%
	\positiontocolor{\pgfmathresult}{#2}%

}
%% Label
\newcommand\histogramlabel[1]{%{position}
	\pgfmathsetmacro\histogramlabeltext{#1-(\range+1)/2}% aus der Skala 1 bis \range wird -(\range-1)/2 bis (\range-1)/2
}
\newcommand\histogramlabelresult{\ensuremath{\pgfmathprintnumber\histogramlabeltext}}
%% einzelner Histogrammeintrag
%- \drawhistogramentry erzeugt für eine Ankreuzoption die gesamte Anzeige (label, caption, bar)
\newcommand\drawhistogramentry[4]{%{position}{number of <position>s}{code to be executed in the beginning}{label} % wird via \drawhistogramentry@relax verwendet
	#3%
	%\begin{scope}%
		\histogramcolor{\range}{\positive}{#1}% sets the color histogramcolor
		\draw (#1,0) node[below]{#4}; % label
		\draw ($(#1,0) + #2*(0,\relativeheight) $) node[above, fill=white, inner sep=3] {#2}; % caption
		\filldraw[fill=histogramcolor] % bar
			($(#1,0) - (\histogrambarwidth,0)$) rectangle % lower left corner
			($(#1,0) + (\histogrambarwidth,0) + #2*(0,\relativeheight)$); % upper right corner
	%\end{scope}%
}
%%% \histo
%- \histo malt ein Histogramm, übernimmt Code aus den verschiedenen Makors
\newcommand\histo[6]{%{Fragentext}{code after ini}{code before output}{left border width}{right border width}{code in picture}
	% Initialisierung
	\renewcommand\histogram{}%
	\let\drawhistogramentry@relax\relax % \drawhistogramentry@relax wird nun nicht expandiert bis es umdefiniert wird
	\setcounter{skalaposition}{0}%
	\setcounter{numberOfAll}{0}%
	% Iteriert üblicherweise über eine Liste von Zahlen
	#2%
	\edef\range{\arabic{skalaposition}}%
	\fragestellung{#1}%
	\ifnum0=\value{numberOfAll}%
		Keine Angaben%
	\else
		#3%
		% Histogrammausgabe aktivieren
		\let\drawhistogramentry@relax\drawhistogramentry % \drawhistogramentry@relax ist nun gleichbedeutend mit \drawhistogramentry
		% Längen bestimmen
		\pgfmathsetmacro\relativeheight{\histogramheight/\value{numberOfAll}}% Höhe pro Stimme
		\pgfmathsetmacro\borderleft@now{#4}%
		\pgfmathsetmacro\borderright@now{#5}%
		\pgfmathsetmacro\histogram@xscale{\linewidth/(\borderright@now cm-\borderleft@now cm)}% Skalierung auf Spaltenbreite
		\begin{tikzpicture}[xscale=\histogram@xscale]
			% Rahmen
			\draw (\borderleft@now,0) rectangle (\borderright@now,\histogramborderheight);
			#6%
			% Inhalt
			\histogram
		\end{tikzpicture}%
	\fi
}
%- \loopovernumbers führt für alle Elemente aus #1 den Code in #2 aus und erhöht Zähler
\newcommand\loopovernumbers[2]{%{list of numbers}{code in loop} % Aktualisiert Zähler und ergänzt Histogrammeinträge für alle Ankreuzoptionen/Positionen/somethings
	\@tfor\numberOfSth:=#1\do{% \numberOfSth nimmt nacheinander <number of 1s>, <number of 2s>, … an, siehe `texdoc source2e` Abschnitt f zu ltcntrl.dtx
		\addtocounter{skalaposition}{1}%
		\addtocounter{numberOfAll}{\numberOfSth}%
		#2%
	}%
}
%%% \skala: Numerische Werte als Histogramm
%- \addtoskalaout ergänzt einen Eintrag |\drawhistogramentry| zu |\histogram|
\newcommand\addtoskalaout[2]{%{position}{number of <position>s, e. g. number of 1s}
	\long\edef\histogram{% Durch Verwendung von \edef werden die fertigen Zahlen genutzt
		\histogram\drawhistogramentry@relax% Da \drawhistogramentry@relax unten auf \relax gesetzt wird, bleibt dies unverändert
		{#1}{#2}{\histogramlabel@relax{#1}}{\histogramlabelresult@relax}% Für \histogramlabel@relax und \histogramlabelresult@relax ebenso
	}%
}
%- \skala
\newcommand\skala[5]{%{positive}{Fragentext}{PolLeft}{PolRight}{{number of 1s}…{number of <range>s}}
	\setnextfilenametohash{\skala{#1}{#2}{#3}{#4}{#5}}% Grafik mit Hash des Aufrufs speichern
	% Initialisierung
	\let\histogramlabel@relax\relax % hier ebenso
	\let\histogramlabelresult@relax\relax % hier ebenso
	\setcounter{weightedSum}{0}%
	\renewcommand*\positive{#1}% Bestimmt positive Antwortmöglichkeit
	\histo{#2}{% code after ini:
		% Iteriert über #5
		\loopovernumbers{#5}{% führt folgenden Code für alle Elemente aus #5 aus und erhöht Zähler
			\pgfmathaddtocounter{weightedSum}{\value{skalaposition}*\numberOfSth}%
			\addtoskalaout{\arabic{skalaposition}}{\numberOfSth}% verwendet \arabic, um tatsächlich die Zahl zu speichern
		}%
	}{% code before output: 
		% Mittelwertbestimmung
		\pgfmathsetmacro\schnittgenau{\value{weightedSum}/\value{numberOfAll}}%
		\histogramlabel{0}%
		\pgfmathparse{\schnittgenau + \histogramlabeltext}%
		\pgfmathroundtozerofill{\pgfmathresult}%
		\let\schnitt\pgfmathresult
		% Histogrammausgabe aktivieren
		\let\histogramlabel@relax\histogramlabel % \histogramlabel@relax ist nun gleichbedeutend mit \histogramlabel@relax
		\let\histogramlabelresult@relax\histogramlabelresult % hier ebenso
	}{\histogramborderleftwithtext}{\histogramborderrightwithtext}{% code in picture:
		% Rahmen
		\histogramlabel{1}%
		\node[above left,rotate=270] at (\borderleft@now,0) {#3 (\histogramlabelresult)};
		\histogramlabel{\range}%
		\node[below left,rotate=270] at (\borderright@now,0) {#4 (\histogramlabelresult)};
		% Mittelwert
		\draw (\schnittgenau,\histogramborderheight) edge[loosely dashed] (\schnittgenau,0)
			node[fill=white,inner sep=\histograminnersep] {\(\varnothing=\schnitt\)};
	}%
}
%%% \singlegraph: Verschiedene Wahlmöglichkeiten als Histogramm
%- \addtosinglegraphout ergänzt einen Eintrag |\drawhistogramentry| zu |\histogram|
\newcommand\addtosinglegraphout[3]{%{position}{number of <position>s, e. g. number of 1s}{label of <position>}
	\long\edef\histogram{\histogram\drawhistogramentry@relax{#1}{#2}{}{#3}}% Durch Verwendung von \edef werden die fertigen Zahlen genutzt, da \drawhistogramentry@relax unten auf \relax gesetzt wird, bleibt dies unverändert
}
%- \singlegraph malt ein Histogramm mit gegebenen Labels, der Code ist partiell aus \skala und teils aus \single geklaut
\newcommand\singlegraph[3]{%{Fragentext}{{label of 1}…{label of <range>}}{{number of 1s}…{number of <range>s}}
	\setnextfilenametohash{\singlegraph{#1}{#2}{#3}}% Grafik mit Hash des Aufrufs speichern
	\histo{#1}{% code after ini:
		\singlegraph@read{#2}{#3}%
	}{}{\histogramborderleft}{\histogramborderright}{}%
}
\newcommand\singlegraph@read[2]{%{list of labels}{list of numbers} % erste Liste muss mindestens so lang sein, wie zweite
	% Initialisierung
	\renewcommand\listoftexts{#1{}}% Zur Verwendung in \popelement wird ein letztes Element angefügt, siehe dort genannten „Bug“
	\loopovernumbers{#2}{% ergänzt Einträge für jedes Element aus #2
		\popelement{\textOfSth}{\listoftexts}%
		\addtosinglegraphout{\arabic{skalaposition}}{\numberOfSth}{\textOfSth}% verwendet \arabic, um tatsächlich die Zahl zu speichern
	}%
	\renewcommand*\positive{N}%
}
%%% \semester: Semester mit Bachelor und Master als Histogramm
\newcommand*\middlerange{}
\newcommand\middlerangeposition{\middlerange}
\newcommand\semester[5]{%{Fragentext}{list of labels}{list of numbers}{list of labels}{list of numbers}
	\setnextfilenametohash{\semester{#1}{#2}{#3}{#4}{#5}}% Grafik mit Hash des Aufrufs speichern
	\histo{#1}{% code after ini:
		\singlegraph@read{#2}{#3}%
		\addtocounter{skalaposition}{1}%
		\edef\middlerange{\arabic{skalaposition}}%
		\singlegraph@read{#4}{#5}%
	}{}{\histogramborderleft}{\histogramborderright}{%
		\pgfmathsetmacro\middlerangepositionleft {\middlerange-1+\histogrambarwidth}
		\pgfmathsetmacro\middlerangepositionright{\middlerange+1-\histogrambarwidth}
		\draw (\middlerangeposition,\histogramborderheight) edge (\middlerangeposition,0);
		\node[fill=white,left ] at (\middlerangepositionleft ,\histogramborderheight) {Bachelor};
		\node[fill=white,right] at (\middlerangepositionright,\histogramborderheight) {Master};
	}%
}

%%% \single: Verschiedene Wahlmöglichkeiten als Aulistung
%% Konstanten
\newcommand\singleitemize{}% Speichert dynamische Inhalte der Auflistung
\newcommand\longempty{}% Zum Vergleich mittels \ifx
\newcommand\listoftexts{}% Speichert labels
%% Makros
\newcommand\addtosingleout[2]{%{macro expanding to text}{macro expanding to number} resultiert in \addtosingleout@{text}{number}, was einen Eintrag „\item[text] number“ ergänzt
	\expandafter\expandafter\expandafter\addtosingleout@ % zu \expandafter siehe Erklärung im Abschnitt zu Hilfsmakros
	\expandafter\expandafter\expandafter{% auf den Beginn der nächsten Zeile werden zwei Expansionen angewandt
	\expandafter#1\expandafter}\expandafter{% eine Expansion wird genutzt, um die nächste Zeile einmal zu expandieren, die andere expandiert #1
	#2}%
}
\newcommand\addtosingleout@[2]{%{text}{number}
	\long\addtoken\singleitemize{\item[#2$\times$]#1}% \item[#2]#1 wird besser nicht expandiert
}
%- \single
\newcommand\single[3]{%{Fragentext}{{text for option 1}…{text for option <range>}}{{number of option 1}…{number of option <range>}}
	% Initialisierung
	\renewcommand\singleitemize{}%
	% Liest Texte und Anzahlen für alle Ankreuzoptionen/Positionen/somethings ein
	\renewcommand\listoftexts{#2{}}% Zur Verwendung in \popelement wird ein letztes Element angefügt, siehe dort genannten „Bug“
	\@tfor\numberOfSth:=#3\do{% \numberOfSth nimmt nacheinander <number of option 1>, <number of option 1>, … an, siehe `texdoc source2e` Abschnitt f zu ltcntrl.dtx
		\popelement{\textOfSth}{\listoftexts}%
		\ifnum\numberOfSth=0 \else
			\addtosingleout{\textOfSth}{\numberOfSth}%
		\fi
	}%
	% Ausgabe
	\fragestellung{#1}%
	\ifx\longempty\singleitemize
		Keine Angaben% Falls \singleitemize leer sein sollte
	\else
		\begin{description}\listenlaengen
			\singleitemize
		\end{description}
	\fi
}

%%% \offen wird automatisch versteckt, wenn vorherige \yesnocomment-Frage kein ja enthielt
\newcommand\offen[2]{%{Fragentext}{Liste von \item}
	\fragestellung{#1}%
	\renewcommand\singleitemize{#2}%
	\ifx\longempty\singleitemize
		Es liegen keine Kommentare vor.\par
	\else
		\begin{itemize}\listenlaengen
			#2
		\end{itemize}
	\fi
}

\newcommand\yesnocomment[3]{%{Fragentext}{number of ja}{number of nein}
	\single{#1}{{ja}{nein}}{{#2}{#3}}%
	\ifnum#2>0 % mindestens ein ja -> Belasse nächtes \offen
		\expandafter\@gobble
	\fi
	\@gobble@offen
}
%%% Ignoriere folgendendes \offen{…}{…}
\newcommand\@gobble@offen[1]{%
	\ifx\offen#1
		\expandafter\@firstoftwo
	\else
		\expandafter\@secondoftwo
	\fi\@gobbletwo{#1}%
}

% Alias
\newcommand\janein[1]{\single{#1}{{ja}{nein}}}%

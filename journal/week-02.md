# Reflections

What material did I work with?

A csv file containing metadata of certain editions of early modern prints from the HRE and the Swiss CF. I had to turn that data into graphs using [RAWGraphs](https://app.rawgraphs.io/) 

What transformation did the tool perform?

The tool turned a spreadsheet into graphs, allowing diverse hist. quest. to be asked (see [instructions for week 2](https://github.com/drewbthomas/applied-digital-history-course/blob/main/tutorials/week-02-rawgraphs/README.md)).

Which decisions did I make?

To be honest, the only decisions I really had to make pertained to colour schemes (too many subcategories and RAWGraphs turns things grey any time you commit a change) and margins (when does the graph description not get cut off). For challenge two see my [notes](challenge-pie-notes.md).

What failed, remained unclear, or produced an unexpected result?

A major (MAJOR) annoyance with RAWGraphs is that one cannot reasonably space or place axis labels. They tend to overlap. What I did not expect was for RAWGraphs to be able to work with the uncleaned CSV with empty cells. I did not need to change the table until the second challenge.

I am not as of yet very convinced by the separation of data into "categories" and "quantities", maybe my understanding is flawed. Is a binary yes-no (HRE-Switzerland) a category or a quantity? Surely if categories get counted, only then they turn into quantities? And surely years are not quantities? And what distinguishes a quantity from an identifier? I do know what an identifier is or supposedly is (the ID, the author, the place, the title; proper metadata).

What does the output allow me to infer historically?

I do not believe in answering questions that have already been answered by themselves. Cf. the instructions to each graph except for challenge two.

What does the output not allow me to infer?

Anything not in the table is left out, and all graphs are derivative of the table. Anything left out is left out! E.g. Basel's high occurrence cannot let one infer that Basel was *the* printing center of the 16<sup>th</sup> century, only that in the sample it occurs extraordinarily more often than other cities, hence maybe inflating the numbers for editions out of the Swiss CF. Maybe there are more prints not included that even the numbers for certain cities, maybe not. n=500 is just too small to stake a claim.

Also, the data cannot, imo, show if production ever grew or diminished systematically (see graph [2](02-line-editions-by-year-and-country.svg)) as it is way to erratic.

Could this method contribute to my final project? Why or why not?

I am not a big fan of graphs. I like tables and descriptive text containing percentages. But who knows! Alas, I am not yet certain what my final project will be and cannot say if graphs will be a good representation.

**Below my notes to the overall process.**

## Step 2

*Check whether the data appears in separate columns.*
No, data does not appear in separate columns. All is in one column, and commas separate the values (at least visually). Probability that one can use the data presented this way w/o manually splitting it into colums = 0.

*Look at names and places containing accented characters, such as Köln. Are they displayed correctly?*
Accented characters work fine, but I have had to convert a csv to UTF-8 before because Chinese characters kept being displayed instead of *ö*.

Find a blank cell. Does it mean zero, unknown, not applicable, or simply missing?
Well, since there are no more than 1 (one) rows, there are no blank cells. But if a value is not present, the CSV contains ",," (presumably also if it can't convert Latin dates to numerical)

*Find one value in year that is more complicated than a four-digit number, if one is present. Compare it with year_numeric.*
As I cannot sort the data by "year" if everything is in one column, this would leave me to manually check at least 100 entries (checked the first 20), which I am too unenthusiastic to do. I assume that date ranges (or Latin numerals in the "year" field) may mess things up.

## Step 3

*everything looks normal*

## Step 4

*What does one row represent?*
One column represents the values for the fields of all corresponding items. One row represents one item and all its values that correspond to a field.

*Does a row describe a physical copy, an edition, or an aggregate?*
Probably a physical copy (format would not be as relevant a field as, say, editors in case of an edition). It could also point to all physical copies of said work (as prints are, ideally, identical).

*Which columns contain categories?*
author, printer, decade, format, language

*Which columns contain quantities?*
none? there is no actual counting being done? am I missing smth?

*Which columns are identifiers rather than quantities?*
all dates, edition_id, short_title, author, printer, printer, place(s)

*How are dates represented in year, year_numeric, and decade?*
year contains (except for normal years) date ranges (eg. "1553-54"), uncertainties (eg. "[1515]") or both (eg. "[1507-12]"). year_numeric loses this additional info, and decade itself derives from year_numeric, wherein the ending number is expunged.

*How are missing values represented?*
Missing values are empty cells.

*Are any categories uncertain, inconsistent, or historically constructed?*
The author category sometimes sorts by surname, sometimes not, and does not distinguish between "classical" and non-classical authors. Also, Saint Ursula is sometimes entered as "Ursula, S" or "Ursula, St" - maybe these two are different ppl. Not sure. Printers names seem to be normalized, albeit sorted by first name exclusively. The category "country" is itself at least questionable, esp. if the regional location/city is uncertain. At least uncertainties are marked by eckige Klammern. The category format is also sometimes inconsistent (eg. "Broadsheet" or added "oblong"). Titles range from sparse to very very long and sometimes contain metadata themselves (authors, Latin numerals, and places I think).

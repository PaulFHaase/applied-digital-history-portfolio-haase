# Step 2

*Check whether the data appears in separate columns.*
No, data does not appear in separate columns. All is in one column, and commas separate the values (at least visually). Probability that one can use the data presented this way w/o manually splitting it into colums = 0.

*Look at names and places containing accented characters, such as Köln. Are they displayed correctly?*
Accented characters work fine, but I have had to convert a csv to UTF-8 before because Chinese characters kept being displayed instead of *ö*.

Find a blank cell. Does it mean zero, unknown, not applicable, or simply missing?
Well, since there are no more than 1 (one) rows, there are no blank cells. But if a value is not present, the CSV contains ",," (presumably also if it can't convert Latin dates to numerical)

*Find one value in year that is more complicated than a four-digit number, if one is present. Compare it with year_numeric.*
As I cannot sort the data by "year" if everything is in one column, this would leave me to manually check at least 100 entries (checked the first 20), which I am too unenthusiastic to do. I assume that date ranges (or Latin numerals in the "year" field) may mess things up.

# Step 3

*everything looks normal*

# Step 4

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
The author category sometimes sorts by surname, sometimes not, and does not distinguish between "classical" and non-classical authors. Also, Saint Ursula is sometimes entered as "Ursula, S" or "Ursula, St" - maybe these two are different ppl. Not sure. Printers names seem to be normalized, albeit sorted by first name exclusively. The category "country" is itself at least questionable, esp. if the regional location/city is uncertain. At least uncertainties are marked by eckige Klammern. The category format is also sometimes inconsistent (eg. "Broadsheet" or added "oblong"). Titles in

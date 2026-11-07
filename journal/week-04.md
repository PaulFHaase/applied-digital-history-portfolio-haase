# Journal for week 4
I am using Jupyter Notebook because I would prefer not to use Google when I can, and I also prefer local environments.
Technical difficulties arose when I closed the cmd window, spent 40 Minutes trying to fix that by myself until I remembered that the crux with browser-UI programs is that the cmd window is the required backend.
## Part 5
The code works first try. This is the explanation Claude spat out:

What the code does

Each numbered block prints a header, so you can match the output to your list.

Loading. pd.read_csv reads the file into a table called df. It only reads, so your CSV on disk is never changed. I turned off pandas’ default habit of treating texts like “NA” or “None” as missing, so only truly empty cells (such as the blank author fields in your excerpt) count as missing. If the output shows one giant column, your file is probably tab-separated; change the loading line to pd.read_csv("book-sample.csv", sep="\t", keep_default_na=False, na_values=[""]).
Size. df.shape gives rows and columns.
Preview. df.head(5) shows the first five records.
Types. object means text, and int64 means whole numbers. If year_numeric shows as object, some entries are not clean numbers.
Missing values. df.isna().sum() counts empty cells per column, and the percentage is that count divided by the number of rows.
Year statistics. The minimum and maximum are the earliest and latest years. The median is the middle year when all are lined up in order, and the mean is the average. The code converts the column to numbers in a temporary copy, so df itself stays untouched, and it reports any entries it had to skip.
Category counts. value_counts(dropna=False) counts each value and includes empty cells, which are labelled “(missing)”. Decades are sorted in chronological order, and the other tables are sorted by size.
ID check. is_unique answers True or False. If it is False, the code lists the rows that share an ID.
What these statistics cannot establish historically
Representativeness. This is a teaching sample, so its proportions say nothing about early modern book production as a whole. A median year or a “most common decade” describes the sample, not the period.
Survival and cataloguing bias. Records reflect which editions survived, which libraries hold them, and which catalogues were digitised. A decade with few records may mean fewer books were printed, fewer survived, or fewer were catalogued.
Output and readership. One record is one recorded edition, not a print run. Counts say nothing about how many copies existed, who bought them, or who read them.
Missing values may not be random. Anonymous works, such as the blank author in your first row, are often systematically different from attributed ones. Percentages of missing data therefore cannot be treated as random noise.
Categories are catalogue labels. “Holy Roman Empire” is a broad, anachronism-prone label, and it sits beside modern city names like Nürnberg and Strasbourg. language and format (8o, 2o) are coarse. The format column indicates how the sheet was folded, not reliably the physical size or the cost of the book.
Derived columns. decade and year_numeric come from year, which may be a printed date, an estimate, or a cataloguer’s guess. The mean of years is rarely meaningful historically.
Unique IDs. A unique edition_id only shows that no ID is repeated. It does not prove that two records are not the same edition, or that each is a distinct work.

These outputs are a first look at data quality and shape. Historical claims need the bibliographic context behind the sample.

**I did not ask the LLM to explain every line of code to me. I'm currently learning Python by myself and can tell what most functions do, and if I don't, I look it up.**

## Part 7
Below the LLMs explanation for everything.

What each transformation does

Loading. Every column is read as text (dtype=str) and nothing is auto-converted to “missing”. This protects values such as box/folder numbers, QIDs, and the text “NA” from being altered. The raw columns are copied into out, and the new columns are added only to that copy.

year_start. A regular expression finds all runs of exactly four digits in date_raw. The first one becomes year_start. If none is found, the cell stays empty. The column uses Int64, pandas’ nullable integer type, so a blank does not force the column into decimals such as 1890.0.

year_end. This is the second four-digit year if there is one. If there is only one, it repeats year_start. If there is none, it is empty.

date_certainty. The rules run in the order you specified, and the first one that matches wins:

? anywhere gives “uncertain”.
Starting with c. (after trimming and lowercasing) gives “approximate”.
Starting with [ gives “supplied/inferred”.
Two or more four-digit years give “range”. I used “two or more”, so a text with three years also counts as a range.
Exactly one year gives “exact”.
Anything else gives “unparsed”.

Because of this order, [1890?] is “uncertain”, not “supplied/inferred”, and c. 1890-1895 is “approximate”, not “range”.

place_trimmed. str.strip() removes only leading and trailing whitespace. Spelling, language, and punctuation stay as they are.

Checks. The assertions confirm 100 rows, unique record_id, no missing original columns, and that the original values are identical to the input. A fifth check confirms that no unexpected label slipped in. If any check fails, the cell stops with a message instead of silently saving a bad file.

How aggregation changes the unit of observation

In the record-level file, one row is one photograph record, and you can still see its title, creator, place, and exact date. In the counts file, one row is one date-certainty category, and the number says how many records fall into it. The counts file therefore cannot tell you which photographs they are, who made them, or when. You cannot get back from the counts to the records. Use the record-level file when you want to chart individual photographs or years, and the counts file when you want to chart the quality of the dating itself (for example, a bar chart in RAWGraphs). Categories with zero records are kept as rows with record_count 0, so the table always has the same six rows. The percentage of a category is only meaningful in relation to the 100 records of this sample.

Cases the rules might handle incorrectly

Years and ranges

Abbreviated ranges such as 1890-95 or 1890/95 contain only one four-digit year. They are labelled “exact”, and year_end is 1890, not 1895.
Decades and centuries such as 1890s give 1890 and are labelled “exact”, even though they cover ten years. 18th century or 1890s with no further digits gives no year or the wrong span.
Wrong order or more than two years: 1895-1890 gives year_end smaller than year_start. With three years, year_end is the second, not the latest.
Two years that are not a range, such as “photographed 1890, printed 1925”. This is labelled “range”, but it describes two events, not a span of dates.
Four-digit numbers that are not years, such as “Box 1820” or “No. 2045”, would be read as years.
“before 1900” / “after 1900” are labelled “exact” although they only give a limit.

Certainty labels

Other markers of approximation such as circa 1900, ca. 1900, c1900, c 1900, or approx. do not start with c., so they fall into “exact” or “range” instead of “approximate”.
Brackets that are not at the start, such as 1890 [?], are caught only by the ? rule, and 1890 [supplied] is “exact”.
A question mark that is not about the date, for example in a quoted note, makes the whole value “uncertain”.
Square brackets with ranges such as [1890-1895] are labelled “supplied/inferred”, which hides that it is also a range, though year_end is still filled correctly.
Different calendars, Roman numerals, or OCR errors such as l890 are labelled “unparsed” or misread.
“Exact” only means “one four-digit year appears in the text”. It does not mean the date is verified.

Places

place_trimmed removes only edge whitespace. Variants such as “Wien” and “Vienna”, double spaces inside the name, trailing commas, or brackets remain as separate values and will appear as separate categories in RAWGraphs. If you want them merged, that is a separate, documented cleaning step.

A good habit is to scan the “unparsed” rows and a few “exact” rows in the output to see which of these patterns actually occur in your data.

**comments**

The Code returns "n.d." as unparsed. I asked the LLM to correct for this issue. The corrected code is beyond me, but I am too proud to ask an LLM. This will take much of my free time, but I am sacrificing it anyway.

## Part 8

The import of matplotlib (and pandas for that matter) fails if these libs are not installed. Luckily I used pip install for getting Jupyter, so I tried the same thing but with matplotlib and pandas and it worked.

### Step 3

I asked the LLM to make the axis' labels and the title of the graph more concise by removing parentheses and additional info.

## Part 9

Up until now, Claude has been exceedingly careful to not skew the data in any way. I can't find anything I would not do myself, which is scary in a way.

## Part 12

I let the LLM create a python script that displays some information about the street names in Salzburg. It even made an acceptable lookup table for titles of honoured persons without much instruction. My prompt was this:

I have a file named "StrVerz_Salzburg.csv". Write one self-contained Python code cell to calculate certain percentages. Import only the most necessary packages, e.g. Pandas or re if you need it.

The first five rows look like this:
Straßenkennziffer	Straßenname	Straßenname kurz	Ortschaftsname	Postleizahl
030915	Abfalterhofweg	Abfalterhofweg	Salzburg	5026
030916	Abtsdorferstraße	Abtsdorferstr.	Salzburg	5020
040347	Adalbert-Stifter-Straße	Adalbert-Stifter-Str.	Salzburg	5020
030917	Adam-Müller-Guttenbrunn-Str.	A.M.Guttenbrunn-Str.	Salzburg	5020
030918	Adolf-Bekk-Straße	Adolf-Bekk-Str.	Salzburg	5020

The file is 1112 rows long (header included).

Requirements:
if a street name is mentioned in multiple rows, count it for the Postleizahl evaluation, but do not count it for other percentages.
print the count for total unique street names.
print how many streets are located in which PLZ in a table.
print how often street names are NOT abbreviated in the "Straßenname kurz" category. Give absolute and relative numbers in a table.
print how often the several endings for street names appear (weg, -Straße/straße, gasse, platz, kai), and print how many names do not fall into these categories. Again give percentages.
inspect naming patterns to count only titles.

**Afterwards**, the LLM suggested to link everything to wikidata or overlay it on a map - things already done in part by the city of Salzburg.

## Part 13/2 (reflection)

*Report one result you independently validated and explain how you validated it.*

I manually checked titles in street names by searching the csv. The LLM's code did not catch all nobles (the lookup table does not include dropping particles; nor does the Python code check for noble's names - but how could it?), but it did catch all academic titles.

Identify one missing-data pattern in the book dataset.

Inferred place names are not included in the analyses.

Describe one way you improved a prompt after seeing code or output.

This question has already been answered.

Describe one error or questionable assumption and how you diagnosed it.

There were no errors. The LLM did exactly what it was told to do.

What does it mean to supervise generated code rather than merely accept it?

It means to look at what each line does and inspect how the code changes/agglomerates data.

What parts of this workflow should remain the historian's responsibility even if the code executes correctly?

The prompting, the general procurement of data (Quellenkritik) and the inspection of the results should be done by a human.

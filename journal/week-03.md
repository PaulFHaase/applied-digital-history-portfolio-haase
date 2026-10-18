# Journal for Week 3

## Part 3

What does one row represent?

One row equals one object.

Which columns describe the historical object?

subject_raw, object_type_raw, caption_language_raw, notes_raw (by extension also title_raw, creator_raw, date_raw, place_raw, country_raw and rights_raw)

Which columns describe its archival or digital representation?

record_id, holding_institute_raw, box_folder_raw, filename_raw, place_wikidata_qid?, creator_authority_uri?, lcsh_subjects????

Which columns appear suitable for a controlled vocabulary?

creator_raw, place_raw, country_raw, subject_raw, caption_language_raw, rights_raw

Which columns contain uncertainty that should not simply be deleted?

foremost date_raw. I would not count an entry with "unknown" as an uncertainty in a strict sense.

## Part 4

Record two examples for each category:

+ a difference that is probably typographical;

CCBY4 and CC BY 4.0; public domain and Public Domain (both in rights_raw)

+ a difference that probably represents two labels for the same concept;

eng and English; HU and Hungary and all other variants

+ a difference that should not be resolved without more evidence.

no known restrictions and Public Domain; and if a place is known but a country is not

## Part 6, Step 3

I merged "photo;print", "photograph/print" and "photo print" into "photo print". I also merged "photograph" and "photo" into "photo", the strings are shorter this way, aesthetic choice. I did not touch the different types of prints - if recorded, that can be a nice source for photo art history or material history.

## Part 7, Step 2

All of the suggested strings were justifiable, initialized names were only clustered among themselves (which is justifiable even if they refer to different persons, so long as they do not get clustered with uninitialized names).
I retained/reformed every name that had an identifiable surname (in case of Spanisch language names the first surname as is custom) like this: lastName, firstName secondName secondFamilyName. This is done for alphabetical sortability.
For the name "Brassaï" i chose the form with the punctuated i as it is very hard to have a typo with extra vowel punctuation. I also radically decided for diacritica as utf-8 can handle diacritica well (not like the late Habsburg Empire).

### Step 3 & 4

The nearest neighbour clustering method put out only one match for the name "henri cartier-bresson"/"Henri Cartier Bresson". Justifiable because no other Cartiers or Bressons are in the sample.
I did not cluster any names whose first names were initialized with non-initialized names. Only if the second name was initialized did I take this risk.
E.g.: I did not cluster "Cartier-Bresson, Henri" with "H. Cartier-Bresson" because the H. could stand for any family member or person who happens to share initial and last name. I would need to see if this person can be verified - records of children and spouse; also photo places (country) could serve to fingerprint it to one person.

## Part 8, Step 3

Normalized "Lisboa" and "Lisbon" into the latter. Also felt confident in approving all of the suggested clusters. Next-neighbour yielded no clusters.
Also normalized "NYC" and "New York City" into the latter.

## Part 9, Step 3

added "if(value.contains("n.d."), "uncertain", [...])" to the expression so that "n.d." would not be referred to as "exact".

## Part 10, Step 2

The expression leaves blank spaces before and after each replaced seperator. This is annoying, but sometimes, the spacing before/after seperators is inconsistent, so no expression is an easy fix.
As the next step requires splitting multi-valued cells, excess spaces can now be trimmed by using value.trim(), then adding a space after each semicolon after remerging the cells using value.replace(";", "; "). Sorry, deviated from my program.

### Step 4

Using multiple cells may be of interest if you want to easily count subjects and if there is no need to keep subject-photograph-count in accord.

## Part 11, Step 4

I am choosing all six of them. All of them are duplicates because their file names match but have different extensions. This heavily suggests duplication. They are the photos w the IDs (PHO-0)25, 49, 73, 94, 96, 98.
If it were not for the matching filenames, I would not be so sure at all. It could be that someone took two photos of the same scene, even with the exact same settings. For 25 and 98, one could compare the scene and be sure, and also for 49 and 96 - they show (probably) moving people. A match would mean that it is a duplicate. The duplicate_keys match; and everything else matches also that identifies the photos.

## Part 14, Step 3

OpenRefine allows for expor of the op hist via a button and saves it as a .json with one click, no need to paste it.

## Part 17. Reflection

Inconsistencies that were visible were mainly naming conventions and spellings, and also initializations. Dates should not be treated the same if they are uncertain with a ? - but it is appropriate to label entirely undated photos as uncertain so long as its undatedness is preserved elsewhere (in our case, year_raw).
I inferred that people were the same if the spelling matched except for diacritica if the dates/places matched roughly. I did not merge initialized names with non-initialized first names. Evidence that they were the same person was sometimes strong (place, date), but it could have been a family member (reasonably) or anybody (unreasonably).
If places are normalized w/o preserving the original spelling, linguists will be mad. Linguistics is a branch of history, or at least depends on it very much. Normalization, for me, changes the interpretation only if you aks questions about naming practices or ethnicities etc., so about the words that have been normalized themselves. Else, the question will probably be largely unaffected. Normalizing "subject" however may lose some distinguishability between terms that are similar, but not the same. A count of normalized place names may differ (for this dataset) because non-english names are spelt in different languages/spellings - not counting the outlier NYC.
If date_raw were replaced by only a single year, we would lose ranges and uncertainty and also exact dates that are sometimes recorded.
Proof requires a visual match. Metadata does not equal the content of a picture, or the physicality thereof. Metadata alone generally allows for *conjecture*, but not *proof*.

# Challenges  

no challenges this week, as I do not want to fiddle around with turning strings into numbers; also, the data is still not cleaned enough after openrefining it. The sugg. clusters for places do not catch all variations - "Vienna" and "Vienne" still coexist. More cleaning would be necessary to make a graph that works, and I don't have the time this week.
The book.csv-challenge would be too tedious, sorry. The same concepts would need to be applied, names should be normalized carefully; but I'm not re-doing the entire week's task with another dataset.
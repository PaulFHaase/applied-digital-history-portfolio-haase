# Journal week 6

## Checkpoint 1

I will use false_imprint_attributed_to to encode places with (= place_name); place_norm are different from place because the values are normalized, and place_interpreted finalizes how uncertainties are mapped.

## Checkpoint 2

all normal.

## Normalization

one normalization you accepted: All inferred places were normalized, additionaly, "Basel (Genéve" was normalized
one proposed normalization you rejected: I did not reject any normalization, as there were no spelling variants.
one value requiring historical interpretation rather than string cleaning: all names with brackets need interpretation; for inferred places, I chose to trust the sample. I did not normalize (= place) because I would like to retain the 'fake' name.

## 11 interpretation

The complete unabridged dataset containing all books printed in the HRE and Switzerland shows that most books come from Basel. There appear to be secondary centres (Leipzig, Cologne, Strasbourg, Nuremberg), but they are regional and cannot supercede the hegemony of Basel. No books are printed in northernmost Germany - books are probably imported, or not one person there can read; printing centers are clustered toward southwest Germany with some small exceptions.

## Optional extension

I instructed the LLM (Claude) to make the circles into pie charts showing the place_relations. It should also add a dashboard with controls. Additionally, the functionality of a "time machine" was edited (editions/decade, viewable accumulative or not on the map); and a "printer trail" search function with predictive search, where one can find printers that moved places easily. There are also analytical graphs to the right of the map showing the absolute number of editions and the place relations, the languages and the places. At the top, a slider helps narrowing down the timeframe, and the entire csv is searchable. The LLM added the functionality to ungarble uploaded csv files, but was not prompted to do so.
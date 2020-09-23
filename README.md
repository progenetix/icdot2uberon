## icdot2uberon
### Mapping from ICDO-T to UBERON

In the cancer genome database [Progenetix](http://progenetix.org), the site of tumor origin is annotated with International Classification of Diseases for Oncology (ICD-O) Topograhy (T), together with the ICD-O Morphology (M) code which indicates histological type and degree of maligancy.

The ICD-O classification system focuses on the clinical and diagnostic aspects of tumor entities, with the combined code providing an accurate representation of a diagnostic entity. In contrast, UBERON is a cross-species anatomical structural ontology system. Its relationship structure allows intergrative queries linking multiple databases (e.g. Gene Ontology, Protein ontology), description logic query within the same organism (linking related organs) and between model animals and humans.

In order to exploit the features of the Uberon ontology, we performed a mapping exercise of ICD-O-T codes to Uberon entities, based on [~270 existing ICD-O T terms](https://progenetix.org/services/collations/?filters=icdot) used to annotate the current >110'000 cancer samples in the [Progenetix cancer genomics resource](https://progenetix.org) to UBERON. We applied a scoring system which rates all Uberon terms to match a queried ICD-O T term with weights from inverse document frequency and yield the match with the highest score. If the score does not pass threshold, it repeats the procedure for synonyms of both ontology systems. Due to the different focus of the two ontology systems - ICD-O on clinical location clusters, UBERON on anatomy and developmental origin - in this first attempt of mapping existing ICD-O-T terms ~10% of the indirect matches needed to be manually adjusted to a more precise level. 

#### Input file
* `icdotmap.txt` in 3 columns: id, label, cleaned label (removing hyphen, nos)
* `uberon_export.owl` Uberon ontology file in OBO format (2019-11-22 release).
* `ICD-O-3_WHO/Topoenglish.txt` ICD-O Topography synonym extension text file from WTO. (open access to registered users after filling out the research questionaire.
[Link](https://www.who.int/classifications/icd/adaptations/oncology/en/))

#### Output file after curation
* `UBERON_icdot_mapping_curated.ods`. 5(7) columns: ICDOT id, label, UBERON id, label, tfidf score, (original UBERON id before correction by curation, original UBERON label)
* Score of 1000 is perfect match of all terms, without text mining.
* Curation was focused on mapping relation with low scores.

#### To-do
* incorporate hierarchical ontology structure into weight function to replace manually selected "specWords".

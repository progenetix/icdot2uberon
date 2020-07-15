## icdot2uberon
### Mapping from ICDO-T to UBERON

In the cancer genome database Progenetix, the site of tumor origin is annotated with International Classification of Diseases for Oncology (ICD-O) Topograhy (T) together with ICD-O Morphology (M) to indicate the cell type and biological activity. The ICD-O ontology system focuses on the clinical and diagnostic aspects of tumor entity so that the combined code gives an accurate representation of tumor. On the other hand, UBERON is a cross-species anatomical structural ontology system. Its relationship structure allows intergrative queries linking multiple databases (e.g. Gene Ontology, Protein ontology), description logic query within the same organism (linking related organs) and between model animals and human. In order to exploit these features and advantages of Uberon ontology, we are taking the initiative to map ICD-O-T codes to Uberon entities, from ~200 existing ICD-O-T terms in [Progenetix cancer genomics resource](https://progenetix.org/do/pgx_subsets/biosubsets.biocharacteristics.type.id=icdot) to UBERON. We use a scoring system which rates all Uberon terms to match a queried ICD-O-T term with weights from inverse document frequency and yield the match with the highest score. If the score does not pass threshold, it repeats the procedure for synonyms of both ontology systems. Due to the different focus of the two ontology systems - ICD-O on clinical location cluster, UBERON on anatomical, developmental origin - in this first attempt of mapping existing ICD-O-T terms, ~10% of the indirect matches need to be manually adjusted to a more precise level. 

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

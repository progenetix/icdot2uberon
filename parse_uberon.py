from pymongo import MongoClient
import nltk, re
from math import log
from nltk.corpus import stopwords
import json

stopword = set(stopwords.words('english'))
meaningLessSingleWord = ['gland','upper','lower','area', 'wall',
                     'joint', 'middle','lower', 'tissu', 'lobe',
                     'third', 'anteri', 'posterior', 'primary',
                    'digit', ' layer', 'region', 'left', 'right', 
                    'proxim', 'element', 'lymph', 'tract', 'system',
                    'ventral', 'dorsal', 'later', 'nucleu','digit',
                    'vein', 'process', 'manual', 'fin', 'epithelium']

specWord = ['left','right','proxim', 'distal', 'dorsal', 'later', 
            'upper', 'lower', 'middle', 'anteri', 'posterior','ventral', 'arteri',
            'vein', 'muscle', 'first', 'second', 'third']

icdot2map = []
icdot2map_label = []
with open('icdotmap_20200924.txt') as f:
    for l in f:
        col = l.strip().split('\t')
        col[-1] = col[-1].replace('overlapping lesion of ','')
        icdot2map.append(col)
        icdot2map_label.append(col[-1])

icdot_synonym = {}
with open('ICD-O-3_WHO/Topoenglish.txt') as f:
    for l in f:
        col = l.strip().split('\t')
        if col[1] == 'incl':

            s = col[2].lower().replace(', nos','').replace('"','').replace('-',' ')
            k = 'icdot-'+col[0] 

            if k in icdot_synonym:
                icdot_synonym[k].append(s)

            else:
                icdot_synonym[k] = [s]

ont_name = 'UBERON'
with open(ont_name.lower() +'_export.owl') as f:
    content = f.read()

split_terms = content.split('\n\n')
easy_match = 0
matched = set()
uberon_term = []
uberon_id = []
uberon_synonym = {}
icdot2uberon = []
for t in split_terms:
    try:
        term_name = t.split('\n')[2].replace('name: ', '')
        term_id = t.split('\n')[1].replace('id: ', '')

        if not re.match(r'UBERON', term_id):
            continue
        if term_name.startswith('obsolete'):
            continue
        
        synonyms = re.findall(r'synonym: "(.+)"', t)
        if synonyms:
            uberon_synonym[term_id] = synonyms
        uberon_term.append(term_name)
        uberon_id.append(term_id)
        if term_name.lower() in icdot2map_label:
            easy_match += 1
            matched.add(term_name.lower())
            idx = icdot2map_label.index(term_name)
            icdot2uberon.append([icdot2map[idx][0], icdot2map[idx][1], term_id, term_name, '1000'])

    except IndexError:
        continue


print('full match: ', easy_match)
print('out of: ', len(icdot2map_label))

### porter stemmer
porter = nltk.PorterStemmer()
def stem(term, porter):
    tokens = nltk.word_tokenize(term.replace('-',' ').replace('/',' '))
    stemmed_term = [porter.stem(t) for t in tokens if t.isalpha()]
    stemmed_term = [t for t in stemmed_term if t not in stopword]
    return stemmed_term

## remove terms which have no stems to have final index
all_uberon_stems = [stem(i, porter) for i in uberon_term]
rm_idx = [i for i,j in enumerate(all_uberon_stems) if not j]
# print('remove id: ',len(rm_idx), uberon_term[rm_idx[0]])
all_uberon_stems = [j for i,j in enumerate(all_uberon_stems) if i not in rm_idx]
uberon_term = [j for i,j in enumerate(uberon_term) if i not in rm_idx]
uberon_id = [j for i,j in enumerate(uberon_id) if i not in rm_idx]

## construct synonym list
uberon_synonym_idx = []
all_uberon_synonyms = []
for u_id, synonyms in uberon_synonym.items():
    idx = uberon_id.index(u_id)
    syns = [stem(i, porter) for i in synonyms]
    uberon_synonym_idx += [idx] * len(syns)
    all_uberon_synonyms += syns

all_icdot_synonyms = []
for i_id, synonyms in icdot_synonym.items():
    syns = [stem(i, porter) for i in synonyms]
    all_icdot_synonyms += syns

all_icdot_terms = [stem(i, porter) for i in icdot2map_label]

## calculate idf (each token's occurrence in all terms) ##
all_tokens = set([j for i in all_uberon_stems for j in i])
all_tokens.update(set([j for i in all_icdot_terms for j in i]))
all_tokens.update(set([j for i in all_uberon_synonyms for j in i]))
all_tokens.update(set([j for i in all_icdot_synonyms for j in i]))
stem_N = len(all_uberon_stems + all_icdot_terms + all_uberon_synonyms + all_icdot_synonyms)
token_idf = {}
for token in all_tokens:
    token_idf[token] = stem_N/(1+sum([1 for term in all_uberon_stems + all_icdot_terms + \
                    all_uberon_synonyms + all_icdot_synonyms if token in term]))

def search_uberon(stemmed_term, term):
    '''
    Searches the list of uberon terms for the best match with an icdo-t term in its stems.
    stemmed_term: list of string
    term: list of list of string
    '''
    tfidf_max = None
    current_match = None
    for idx,u in enumerate(term):
        total_stems = len(u)
        
        match_words = [i for i in stemmed_term if i in u]
        surplus_source = [i for i in stemmed_term if i not in u]
        surplus_target = [i for i in u if i not in stemmed_term]
        spec_punish = [i for i in surplus_target if i in specWord]

        if not match_words:
            continue
        tfidf_u = sum([token_idf[i] for i in match_words]) - \
                    sum([token_idf[i] for i in surplus_source]) - \
                    sum([token_idf[i] for i in surplus_target]) * 5 - \
                    sum([token_idf[i] for i in spec_punish]) * 50 

        if not tfidf_max:
            tfidf_max = tfidf_u - 1
        if len(match_words) == 1 and match_words[0] in meaningLessSingleWord:
            continue

        if tfidf_u > tfidf_max:
            tfidf_max = tfidf_u
            current_match = idx
            
    if not tfidf_max:
        tfidf_max = -1000
    
    return(current_match, tfidf_max)

def find_match(icdot_lab):
    '''
    Find the match index in uberon termsfor an icdo-t term.
    If direct search doesn't pass threshold, search the synonym terms in uberon
    returns matched index and tfidf score
    icdot_lab: string
    '''
    stemmed_term = stem(icdot_lab, porter)
    current_match, tfidf_u = search_uberon(stemmed_term, all_uberon_stems)

    if current_match and tfidf_u > -100:
        return(current_match, tfidf_u)
    else:
        ## try uberon synonym 
        current_match, tfidf_u = search_uberon(stemmed_term, all_uberon_synonyms)
        if current_match:

            current_match = uberon_synonym_idx[current_match]
            
        return(current_match, tfidf_u)

still_unmatch = 0
still_unmatch_term = []

for icdot_id, icdot_label, lab in icdot2map:
    if lab not in matched:

        current_match, tfidf_u = find_match(lab)

        if current_match and tfidf_u > -1000:
            icdot2uberon.append([icdot_id, icdot_label, uberon_id[current_match], uberon_term[current_match], str(tfidf_u)])
        else:
            ## If direct search doesn't pass threshold, search the synonym of the icdo-t term
            try:
                synonyms = icdot_synonym[icdot_id]
                if synonyms:

                    tfidf_max = -1000
                    best_match = None
                    for s in synonyms:
                        current_match, tfidf_u = find_match(s)

                        if tfidf_u > tfidf_max:
                            best_match = current_match
                            tfidf_max = tfidf_u

                    if best_match:
                        icdot2uberon.append([icdot_id, icdot_label, uberon_id[current_match], uberon_term[current_match], str(tfidf_u)])
                    
                    else:
                        still_unmatch += 1
                        still_unmatch_term.append(lab)
                        icdot2uberon.append([icdot_id, icdot_label, '', '', 'unmatched'])

                else: # no synonyms

                    if current_match:
                        icdot2uberon.append([icdot_id, icdot_label, uberon_id[current_match], uberon_term[current_match], str(tfidf_u)])

                    else:
                        raise KeyError

            except KeyError:
                still_unmatch += 1
                still_unmatch_term.append(lab)
                icdot2uberon.append([icdot_id, icdot_label, '', '', 'unmatched'])
            

print('No match!')
print('\n'.join(still_unmatch_term))
print('Number of unmatched terms (doesn\'t pass threshold): ', still_unmatch)

with open('mapping.tsv', 'w') as f:
    print('\t'.join(['ICDOT_id', 'ICDOT_label','UBERON_id', 'UBERON_label', 'score']), file = f)
    for i in icdot2uberon:
        print('\t'.join(i), file = f)




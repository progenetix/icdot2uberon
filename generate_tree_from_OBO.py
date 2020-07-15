## generate tree from owl file (OBO format)
import re

# Clean terms list
def clean_ont_terms(terms, ont_name):
    l = []
    for term in terms:
        keep = ''
        obs = False
        term_split = term.split('\n')
        try:
            term_id = term_split[1]
            if not term_id.startswith('id: '+ ont_name):
                continue
            else:
                keep = term_id
        except IndexError:
            print(term)
            continue
        for line in term_split:
            if line.startswith('is_a:'):
                keep += line
            if line.startswith('is_obsolete: true'):
                obs = True
                break
        if not obs:            
            l.append(keep)
        
    return l

def get_top_nodes(terms, ont_name):
    l = []
    for term in terms: 
        if len(re.findall('is_a: '+ ont_name + ':\d+', term)) == 0:
            l.append(term)
    return l

# Find every term that has the top node as a parent; apply recursively to entire list of terms
# * Keys with empty lists will be leaves
def generate_ont_tree(parent_nodes, all_ont_terms, ont_name, switch=True):
    ont_dict = {}
    search_id = 'id: ('+ ont_name + ':\d+)'
    search_parent = 'is_a: ('+ ont_name + ':\d+)'
    
    for node in parent_nodes:
        parent_ont_id = re.findall(search_id, node)[0]
        ont_dict[parent_ont_id] = {}
        for ont_term in all_ont_terms:
            ont_id = re.findall(search_id, ont_term)[0]
            parent_list = re.findall(search_parent, ont_term)
            if (parent_ont_id in parent_list):
                ont_dict[parent_ont_id][ont_id] = generate_ont_tree([ont_term], all_ont_terms, ont_name, True)
    return ont_dict

ont_name = 'UBERON'
with open('/Users/pgweb/Downloads/' + ont_name.lower() +'_export.owl') as f:
    content = f.read()

split_terms = content.split('\n\n')
split_terms_clean = clean_ont_terms(split_terms, ont_name)
top_nodes = get_top_nodes(split_terms_clean, ont_name)
len(top_nodes)
print('\n'.join(top_nodes))


ont_tree = generate_ont_tree(top_nodes, split_terms_clean, ont_name)
print(ont_tree)
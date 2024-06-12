from SPARQLWrapper import SPARQLWrapper, JSON, RDF


def fetch_all_tags():
    query = '''
    PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
    SELECT DISTINCT ?tag {
        ?r recipe-kb:tagged ?tag .
    }
    LIMIT 10
    '''

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    tags = [x['tag']['value'] for x in results['results']['bindings']]
    return tags

# Here, we extract all the dishes from KG (tagged or without tag)
def fetch_all_dishes ():
    query = '''
        PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
        SELECT DISTINCT ?r ?name {{
        ?r rdfs:label ?name .
        }}
        LIMIT 10
        '''
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    #dish_uris = [r['r']['value'] for r in results['results']['bindings']]
    dish_names = [r['name']['value'] for r in results['results']['bindings']]

    return dish_names

# This function fetches all the dishes that have the given tag
def get_dishes_for_tag(tag):
    #tag = '<{}>'.format(tag)
    query = '''
        PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
        SELECT DISTINCT ?name {{
            ?r recipe-kb:tagged {} .
            ?r rdfs:label ?name .
        }}'''.format(tag)

    query = f'''
        PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
        SELECT DISTINCT ?name
        WHERE {{
            ?r recipe-kb:tagged ?tag .
            ?r rdfs:label ?name .
            FILTER (CONTAINS(LCASE(str(?name)), LCASE("{tag}")))
        }}
    '''

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    dishes = [(x['name']['value']) for x in results['results']['bindings']]
    
    return dishes


sparql = SPARQLWrapper("http://128.213.11.13:9999/blazegraph/namespace/kb")

uri = 'http://idea.rpi.edu/heals/kb/tag/'
tag = "beijing"

#tags_names = fetch_all_tags()
#print (tags_names)

dishes = get_dishes_for_tag (  tag)
print (dishes)
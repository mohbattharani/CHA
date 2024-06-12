"""
Affect - Physical activity analysis
"""
import json
from typing import Any
from typing import Dict
from typing import List

from pydantic import model_validator

from tasks.affect.base import Affect

from SPARQLWrapper import SPARQLWrapper, JSON, RDF

class FoodKGAnalysis(Affect):
    """
    **Description:**

        This tasks performs analysis of FoodKG.
    """

    name: str = "foodkg_analysis"
    chat_name: str = "FoodKGAnalysis"
        
    description: str = (
        "This tool help to get data from FoodKG using SPARQL queries"
        "ADD DETAILS HERE: "
    )
    dependencies: List[str] = []
    inputs: List[str] = [
        "A dish/recipe tag extracted from natural language question. For example: veal, swiss",
    ]
    outputs: List[str] = [
         "RDF graph, Triplets or list of recipe names. This can be JSON. ADD EXAMPLE"
    ]
    # False if the output should directly passed back to the planner.
    # True if it should be stored in datapipe
    output_type: bool = True
    
    def get_dishes_for_tag(self, sparql, tag):
        uri = 'http://idea.rpi.edu/heals/kb/tag/'
        #tag = uri + tag
        query = f'''
            PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
            SELECT DISTINCT ?name
            WHERE {{
                ?r recipe-kb:tagged ?tag .
                ?r rdfs:label ?name .
                FILTER (CONTAINS(LCASE(str(?name)), LCASE("{tag}")))
            }}
            '''
        try:
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            dishes = [(x['name']['value']) for x in results['results']['bindings']]
        except:
            dishes = []

        return dishes

    def generate_recipe_ingredient_query(self, ingredients, limit=10):
        # Construct the FILTER clauses for each ingredient
        filter_clauses = f"regex(str(?ing_name), \"{ingredients[0]}\")"
        for ingredient in ingredients[1:]:
            filter_clauses += f"&&\n regex(str(?ing_name), \"{ingredient}\") "
        
        # Construct the complete SPARQL query
        query = f"""
            PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>

            SELECT DISTINCT ?name
            WHERE {{
            ?recipe rdfs:label ?name .
            ?recipe recipe-kb:uses ?ing .
            ?ing recipe-kb:ing_name ?ing_name .
            FILTER ({filter_clauses})
            }}
            LIMIT {limit}
            """

        return query

    def select_recipes_contain_ingredients (self, sparql, query, return_type = JSON, sub_graph = None):
        #query = self.generate_recipe_ingredient_query (ingredients)
        try:
            sparql.setQuery(query)
            sparql.setReturnFormat(return_type)
            results = sparql.query().convert()
            
            results = [x['name']['value'] for x in results['results']['bindings']]
        except:
            results = []

        return results
        

    def generate_n_hop_query(self, node_uri, num_hops):
        if num_hops < 1:
            raise ValueError("Number of hops should be 1 or greater.")

        # Construct the initial part of the query
        query = f'''PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
        CONSTRUCT {{
        {node_uri} ?predicate1 ?neighbor1 .
        '''
        
        # Add lines for additional hops
        for hop in range(2, num_hops + 1):
            query += f'      ?neighbor{hop - 1} ?predicate{hop} ?neighbor{hop} .\n'

        # Complete the WHERE clause
        query += '    }\n'
        query += 'WHERE {{' + f'''
        {node_uri} ?predicate1 ?neighbor1 .
        '''
        
        # Add lines for additional hops in WHERE clause
        for hop in range(2, num_hops + 1):
            query += "OPTIONAL {" + f"?neighbor{hop - 1} ?predicate{hop} ?neighbor{hop}" +"}" +".\n" 
            #query += "" + f"?neighbor{hop - 1} ?predicate{hop} ?neighbor{hop}" +".\n" 

        query += '    }\n'

        # Complete the UNION clause
        
        query += f'''UNION {{
        ?neighbor1 ?predicate1 {node_uri} .
        '''
        
        # Add lines for additional hops in WHERE clause
        for hop in range(2, num_hops + 1):
            query += "" + f"?neighbor{hop - 1} ?predicate{hop} ?neighbor{hop}" +".\n" 

        query += '    }\n'
        query += '    }\n'
    
        return query
    

    def construct_NHOP_graph (self, dish, N = 1, debug = False):
        dish = '<{}>'.format(dish)
        query = self.generate_n_hop_query(dish, N)
        
        if (debug):
            print (query)
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(RDF)
        graph = self.sparql.query().convert()

        return graph


    def get_tag_graph (self, tag):
        uri = 'http://idea.rpi.edu/heals/kb/tag/' + tag
        graph= self.construct_NHOP_graph (uri, N = 1, debug=False)

        return graph
    
    def get_ing_graph (self, ing):
        uri = 'http://idea.rpi.edu/heals/kb/ingredientname/' + "%20".join (ing.split(" "))

        graph= self.construct_NHOP_graph (uri, N = 1, debug=False)

        return graph

    def graph_triplets (self, graph):
        triplets = []
        for s, p, o in graph:
            triplets.append ([s,p,o])
        
        return triplets

    def _execute(
        self,
        inputs: List[Any] = None,
    ) -> str:
        
        # Connect with RDF Graph Database which is located at this URL
        sparql = SPARQLWrapper("http://128.213.11.13:9999/blazegraph/namespace/kb")
        
        #### 
        # Text query to TAG OR ING NAME
        #  What dishes contain salt and sugar?
        ####
        # Given Tag/Ingredient name, fetch a 1-Hop graph
        #graph = self.get_tag_graph (inputs)
        #graph = self.get_ing_graph (inputs)
        #triplet = self.graph_triplets (graph)
        print ("+"*40)
        print (inputs)
        print ("+"*40)

        if isinstance(inputs, list):
            inputs = inputs[0]

        #query = self.generate_recipe_ingredient_query (inputs)
        #graph = self.select_recipes_contain_ingredients (sparql, query)
        #print ("+query"+"+"*40)
        #print (query)
        #print ("+"*40)
        graph = self.get_dishes_for_tag (sparql, inputs)
        #graph = "\n".join (graph)
        print ("+graph"+"+"*40)
        print (graph)
        print ("+"*40)
        
        return graph

from CHA import CHA
import json 

def save_as_json(results, filename):
    with open(filename, 'w') as f:
        json.dump(results, f, indent=4)


available_tasks = ["foodkg_analysis", "ask_user"]
available_tasks = ["ask_user"]

save_results = 'results/results_v1.json'

user_query1 = "What veal dishes don't have lean beef and are medium fat, and have peppercorns, and do not have short - grain rice, 15%25 cream, and contain sugar with desired range 5.0 g to 30.0 g?"

user_queries = [user_query1]

kwargs = {
    'meta': ['Identify the food tags and ingredients from user query. Use food tags as input to foodkg_analysis task to get relevant recipe names.']
}

for user_query in user_queries:
    #input("Ask your question: ")
    cha = CHA()
    chat_history = []
    response = cha.run(
        user_query,
        chat_history=chat_history,
        available_tasks=available_tasks,
        use_history=True,
        max_retries=1,
    )

    print("CHA: ", response)

    chat_history.append((user_query, response))

    save_as_json ({'q': user_query, 'pred': response}, save_results)
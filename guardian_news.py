
import pandas as pd
import requests
import json
api_key = '0c8d16dd-6deb-461c-b0c3-4c42ab95407a'
query_list = ['ukraine']#['war AND ukraine']
section_text = 'commentisfree|world'
from_date="2022-02-24"

def query_api(query_text, section_text, page, from_date, api_key):
    """
    Function to query the API for a particular query
    returns: a response from API
    """

    # + "&show-fields=bodyText" \
    req = "https://content.guardianapis.com/search?order-by=newest&q=" + query_text \
        + "&section=" + section_text \
        + "&from-date=" + from_date \
        + "&page=" + str(page) \
        + "&page-size=200&api-key=" + api_key
    response = requests.get(req)
    return response

def get_results_for_q(q, section_text, from_date, api_key):
    """
    Function to run a for loop for results greater than 200. 
    Calls the query_api function accordingly
    returns: a list of JSON results
    """
    # json_responses = []
    response = query_api(q, section_text, 1, from_date, api_key).json()
    records = collect_results(response)
    # json_responses.append(response)
    number_of_results = response['response']['total']
    pages = response['response']['pages']
    print(number_of_results, pages)
    for page in range(2, pages+1):
            print(str(page) + "/" + str((round(number_of_results/200))+1))
            response = query_api(q, section_text, page, from_date, api_key).json()
            add_records = collect_results(response)
            records +=add_records
    return records

def collect_results(response):
    filtered_results = []
    if 'results' in response['response']:
        for result in response['response']['results']:
            record = {}
            title  = result['webTitle']
            #remove similar frequent headers
            if 'Russia-Ukraine war: what we know on day' in title or 'Corrections and clarifications' in title or "Russia-Ukraine war: catch up on this week’s must-read news and analysis" in title:
                continue
            if "Russia-Ukraine war latest:" in title :
                title = title.replace("Russia-Ukraine war latest:", "")
            if "Russia-Ukraine war:" in title:
                title = title.replace("Russia-Ukraine war:", "")
            if "Russia’s war in Ukraine:" in title:
                title = title.replace("Russia’s war in Ukraine:", "")

            # record['body'] = result['fields']['bodyText']
            record['title'] = title
            record['date'] = result['webPublicationDate'] 
            filtered_results.append(record)
    return filtered_results



def convert_json_responses_to_df(json_responses):
    """
    Function to convert the list of json responses to a dataframe
    """
    df_results = []
    for json in json_responses:
        df = pd.json_normalize(json['response']['results'])
        df_results.append(df)
    all_df = pd.concat(df_results)
    return all_df
        
def get_results_for_all_queries(q_list, section_text, from_date,  api_key):
    tag_df_list = []
    for q in q_list:
        json_responses = get_results_for_q(q,section_text, from_date, api_key)
        tag_df_list.append(json_responses)
    return tag_df_list

results = get_results_for_all_queries(query_list,section_text, from_date, api_key)

for i,res in enumerate(results):
    # print(results)
    with open(query_list[i] + '_data.json', 'w') as f:
        json.dump({'articles': res}, f)



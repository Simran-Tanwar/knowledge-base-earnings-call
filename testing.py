import time
import numpy as np
from functions import knowledge_base
from get_transcript import get_transcript
from constant import common_path,openAI_API
from llama_index import StorageContext, load_index_from_storage
import openai
import os
import requests

getTranscript = get_transcript()
knowledge_base = knowledge_base()

openai.api_key = openAI_API
os.environ["OPENAI_API_KEY"] = openAI_API
storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)
def index_func():
	file_path = common_path + 'transcript/Apple_transcript.txt'  # Replace with the actual path to your text file
	with open(file_path, 'r',encoding="utf-8") as file:
		content = file.read()
	doc = knowledge_base.read_docs(content,"AAPL")
	doc_list = [doc]
	index = knowledge_base.create_index(doc_list)
	index.storage_context.persist("./storage")
	return index

def rapid_API_func():
	name = "Apple"
	url = "https://seeking-alpha.p.rapidapi.com/v2/auto-complete"

	querystring = {"query": name, "type": "symbols", "size": "5"}

	headers = {
		"X-RapidAPI-Key": "a6839f9a09mshf020b19a9270c8ap16dae2jsn0713d4ff74df",
		"X-RapidAPI-Host": "seeking-alpha.p.rapidapi.com"
	}

	response = requests.get(url, headers=headers, params=querystring)
	response.json()

def query_function():
	query_engine = index.as_query_engine()
	response = query_engine.query("what was the total revenue for Apple?")
	return response

all_times = []
for i in range(2):
	s_time = time.time()
	index_func()
	all_times.append(time.time()-s_time)
print(np.quantile(all_times, q=[0.5, 0.75,0.95, 0.99]))





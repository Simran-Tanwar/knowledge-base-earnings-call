import openai
import os
from llama_index import SimpleDirectoryReader, VectorStoreIndex, load_index_from_storage, StorageContext, Document
import pandas as pd
from get_transcript import get_transcript


class knowledge_base:
    # to get transcript of a company
    # folder_path should be path to the folder where transcript is saved
    def get_transcript(self, company_name, folder_path):
        getTranscript = get_transcript()
        transcript = getTranscript.fetch_and_preprocess_transcript(company_name)
        file_path = folder_path + "/" + company_name + '_transcript.txt'
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(transcript)
        return transcript

    # to load docs from a directory
    def load_docs(self, folder_path):
        docs = SimpleDirectoryReader(folder_path).load_data()
        return docs

    # to read data manually from code
    def read_docs(self, transcript):
        doc = Document(text=transcript)
        doc_list = [doc]
        return doc_list

    # to create index
    def create_index(self, docs):
        index = VectorStoreIndex.from_documents(docs)
        return index

    #to get response
    def get_response(self,query_engine, qs ):
        responses = []
        for i in range(len(qs)):
            response = query_engine.query(qs[i])
            responses.append(response)

        response_arr = []
        for i, response in enumerate(responses):
            response_dict = {
                "Query": qs[i],
                "Response": response
            }
            response_arr.append(response_dict)
        return response_arr

    def get_company_names(self,folder_path):
        company_names = []
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                company = filename.split("_transcript.txt")[0]
                company_names.append(company)
        return company_names

    #to create a data dictionary
    #company_names is list of companies and ticker_sym is list of ticker symbols of companies
    def data(self,company_names,docs,ticker_sym):
        data = {}
        doc_id_dict = {}
        ticker_symbols = {}
        for i, company in enumerate(company_names):
            ticker_symbols[company] = ticker_sym[i]
            docs[i].metadata = {"Ticker_symbol": ticker_symbols[company]}
            docs[i].doc_id = "EC_" + ticker_symbols[company] + "_" + company
            doc_id_dict[company] = docs[i].doc_id

            data[company] = {
                "doc_id": doc_id_dict[company],
                "ticker_symbol": ticker_symbols[company]
            }
        return data
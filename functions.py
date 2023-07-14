import openai
import os
from llama_index import SimpleDirectoryReader, VectorStoreIndex, load_index_from_storage, StorageContext, Document
import pandas as pd
from get_transcript import get_transcript
from constant import openAI_API, common_path

class knowledge_base:
    # to load docs from a directory
    def load_docs(self, folder_path):
        docs = SimpleDirectoryReader(folder_path).load_data()
        return docs

    # to create index
    def create_index(self, docs):
        openai.api_key = openAI_API
        os.environ["OPENAI_API_KEY"] = openAI_API
        index = VectorStoreIndex.from_documents(docs)
        return index

    #to get the master list, from an excel sheet names "Companies.xlsx"- sheet have 2 columns - Ticker Symbol and Company Name
    def list_companies(self,file_path =common_path+"Companies.xlsx" , sheet_name="Sheet1"):
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        ticker_symbols = df["Ticker Symbol"].tolist()
        company_name = df["Company Name"].tolist()
        list_companies = {}
        for i,ticker_symbol in enumerate(ticker_symbols):
            list_companies[ticker_symbol] = company_name[i]
        return list_companies

    # to get transcript of a company
    # folder_path should be path to the folder where transcript is saved
    def save_transcript(self, company_ticker, folder_path):
        getTranscript = get_transcript()
        transcript = getTranscript.fetch_and_preprocess_transcript(company_ticker)
        master_list = self.list_companies()
        company_name = master_list[company_ticker]
        #file is saved as company_name_transcript.txt
        file_path = folder_path + "/" + company_name + '_transcript.txt'
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(transcript)
        return transcript

    # to read data manually from code
    def read_docs(self, transcript, company_ticker):
        doc = Document(text=transcript)
        master_list = self.list_companies()
        company_name = master_list[company_ticker]
        doc.metadata = {"Ticker_symbol":company_ticker, "Company_name":company_name}
        doc.doc_id = "EC_"+company_ticker+"_"+company_name
        return doc

    #to query for a company given its ticker symbol and query
    #response is stored in form of dictionary like {company_name:{query:response}}
    def query_ticker(self,company_ticker, query):
        master_list = self.list_companies()
        company_name = master_list[company_ticker]

        openai.api_key = openAI_API
        os.environ["OPENAI_API_KEY"] = openAI_API

        storage_context = StorageContext.from_defaults(persist_dir="./storage")
        index = load_index_from_storage(storage_context)

        Query = "For " + company_name + ", " + query
        query_engine = index.as_query_engine()
        response = query_engine.query(Query)

        response_dict = {query: str(response)}
        return response_dict

    #to insert new companies in master list and in index
    def edit_index(self,new_list):
        folder_path = common_path+"transcript"
        file_path = common_path+"Companies.xlsx"

        master_list = self.list_companies()
        company_tickers = list(master_list)

        storage_context = StorageContext.from_defaults(persist_dir="./storage")
        index = load_index_from_storage(storage_context)
        for company_ticker in new_list:
            if company_ticker not in company_tickers:
                transcript = self.save_transcript(company_ticker, folder_path)
                doc= self.read_docs(transcript, company_ticker)
                index.insert(doc)
                company_tickers.append(company_ticker)
                company_name = new_list[company_ticker]
                master_list[company_ticker] = company_name
                new_company = pd.DataFrame({'Ticker Symbol': [company_ticker],'Company Name':[company_name]})
                df = pd.read_excel(file_path, sheet_name="Sheet1")
                df = pd.concat([df, new_company], ignore_index=True)
                df.to_excel(file_path, index=False)

        index.storage_context.persist("./storage")
        return index

    #to delete a transcript from index and update master list accordingly
    def del_doc(self,company_ticker):
        master_list = self.list_companies()
        company_name = master_list[company_ticker]

        doc_id = "EC_" + company_ticker + "_" + company_name

        storage_context = StorageContext.from_defaults(persist_dir="./storage")
        index = load_index_from_storage(storage_context)

        index.delete_ref_doc(ref_doc_id=doc_id, delete_from_docstore=True)
        index.storage_context.persist("./storage")

        master_list.pop(company_ticker)
        df = pd.read_excel(common_path + 'Companies.xlsx')
        condition = df['Ticker Symbol'] == company_ticker
        df = df[~condition]
        df.to_excel(common_path + 'Companies.xlsx', index=False)

        return index

    #to update index with the new transcript
    def update_index(self,company_ticker):
        self.del_doc(company_ticker)
        list = [company_ticker]
        index = self.edit_index(list)
        return index
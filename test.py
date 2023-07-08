from flask import Flask, redirect, url_for, request, jsonify
import openai
import os
from llama_index import SimpleDirectoryReader, VectorStoreIndex, load_index_from_storage, StorageContext
import pandas as pd
from functions import knowledge_base

app = Flask(__name__)

openai.api_key = "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"
os.environ["OPENAI_API_KEY"] = "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"

folder_path = "D:/college stuff/Intern_Aviso/Knowlegde_base_earnings_call/transcript"

knowledge_base = knowledge_base()

# Get list of companies and ticker symbols
file_path = 'D:/college stuff/Intern_Aviso/Knowlegde_base_earnings_call/Companies.xlsx'
df = pd.read_excel(file_path, sheet_name="Sheet1")
company_names = df["Company"].tolist()
ticker_sym = df["Ticker Symbol"].tolist()

# Get transcript of companies
transcript_dict = {}
for company in company_names:
    transcript = knowledge_base.get_transcript(company, folder_path)
    transcript_dict[company] = transcript

# Get Index (vector data base)
docs = knowledge_base.load_docs(folder_path)
doc_id_dict = {}
ticker_symbols = {}
for i, company in enumerate(company_names):
    ticker_symbols[company] = ticker_sym[i]
    docs[i].metadata = {"Ticker_symbol": ticker_symbols[company]}
    docs[i].doc_id = "EC_" + ticker_symbols[company] + "_" + company
    doc_id_dict[company] = docs[i].doc_id

index = knowledge_base.create_index(docs)
index.storage_context.persist("./storage")

# Get response
storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)


@app.route('/query/<company_name>')
def query(company_name):
    qs = [
        'What was the total revenue of {} for this quarter?',
        'How has the revenue growth rate changed compared to the previous period of the {}?',
        'Which product or market segments contributed the most to the overall revenue of the {}?'
    ]

    company_qs = [q.format(company_name) for q in qs]

    query_engine = index.as_query_engine()
    responses = []
    for i in range(len(company_qs)):
        response = query_engine.query(company_qs[i])
        responses.append(response)
    response_dict = {qs[i]: responses[i] for i in range(len(qs))}
    return jsonify(response_dict)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        name = request.form['nm']
        return redirect(url_for('query', company_name=name))
    else:
        name = request.args.get('nm')
        return redirect(url_for('query', company_name=name))


if __name__ == '__main__':
    app.run(debug=True)

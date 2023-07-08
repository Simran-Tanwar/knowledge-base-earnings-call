import requests
import regex as re

class get_transcript:
    #def __init__(self, company_name):
    #    self.company_name = company_name

    def get_raw_transcript(self, company_name): #To get the transcript from Rapid API
        API = "7871a3e878msh29d22269f291f38p1169b5jsn1401131f5511" #You rapidAPI API key
        url_0 = "https://seeking-alpha.p.rapidapi.com/v2/auto-complete"
        querystring_0 = {"query": company_name, "type": "people,symbols,pages", "size": "5"}
        headers_0 = {
            "X-RapidAPI-Key": API,
            "X-RapidAPI-Host": "seeking-alpha.p.rapidapi.com"
        }
        response_0 = requests.get(url_0, headers=headers_0, params=querystring_0)
        symbol_c = response_0.json()
        ticker_symbol = symbol_c["symbols"][0]["name"]

        url_1 = "https://seeking-alpha.p.rapidapi.com/transcripts/v2/list"
        querystring_1 = {"id": ticker_symbol,"size": "20", "number": "1"}
        headers_1 = {
            "X-RapidAPI-Key": API,
            "X-RapidAPI-Host": "seeking-alpha.p.rapidapi.com"
        }
        response_1 = requests.get(url_1, headers=headers_1, params=querystring_1)
        lists = response_1.json()
        id_company = lists["data"][0]["id"]

        url_2 = "https://seeking-alpha.p.rapidapi.com/transcripts/v2/get-details"
        querystring_2 = {"id": id_company}
        headers_2 = {
            "X-RapidAPI-Key": API,
            "X-RapidAPI-Host": "seeking-alpha.p.rapidapi.com"
        }
        response_2 = requests.get(url_2, headers=headers_2, params=querystring_2)
        details = response_2.json()
        raw_transcript = details["data"]["attributes"]["content"]
        return raw_transcript

    def preprocess_transcript(self, raw_transcript): # to pre-process the transcript
        modified_text = re.sub(r'</p>', '\n', raw_transcript)
        modified_text = re.sub(r'&amp;', ' and ', modified_text)
        modified_text = re.sub(r'<p>|<strong>|</strong>', '', modified_text)
        modified_text = re.sub(r'<[^>]+>', '', modified_text)
        modified_text = re.sub(r"(Company Participants|Conference Call Participants)\s+[\w\s,-\.']+\n", '', modified_text)

        pattern = r'(?<=\n|Q -)[A-Za-z ]+(?=\n)'
        modified_transcript = re.sub(pattern, lambda match: match.group() + ':', modified_text)

        def remove_url(text_data):
            text = re.sub(r"http\S+", "", text_data)
            text = re.sub(r'^[\w\.-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', '', text)
            return text

        modified_transcript = re.sub(r'Q - ', '', modified_transcript)
        modified_transcript = re.sub(r'\[\w*\W*\w*]\n', '', modified_transcript)
        modified_transcript = re.sub(r"^.*PM\sET$|^.*AM\sET",'Operator:', modified_transcript)
        modified_transcript = re.sub(r"([A-Za-z\s.,]+)\((\w+:\w+)\)[\s\w',:].*ET", 'Operator:', modified_transcript)
        modified_transcript = re.sub(r'\n\s*', ' ', modified_transcript)

        pattern_2 = '([A-Za-z ]+)\s*:|Question-and-Answer Session'
        modified_transcript = re.sub(pattern_2, lambda match: '\n' + match.group(), modified_transcript)
        transcript = remove_url(modified_transcript)
        return transcript
    def fetch_and_preprocess_transcript(self, company_name): #to get the pre-processed transcript
        raw_transcript = self.get_raw_transcript(company_name)
        processed_transcript = self.preprocess_transcript(raw_transcript)
        return processed_transcript

#company_name = input("Give Company name:")
#getTranscript = get_transcript(company_name)
#transcript = getTranscript.fetch_and_preprocess_transcript(company_name)
#file_path = company_name + 'Q1_transcript.txt'
#Saving the transcript as company_name_transcript.txt
#with open(file_path, 'w', encoding="utf-8") as file:
#    file.write(transcript)
#print("File saved successfully as:", file_path)
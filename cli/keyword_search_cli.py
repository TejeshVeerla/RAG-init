import string
import argparse
import json
import io
from nltk.stem import PorterStemmer
import sys
import pickle

def remove_punctuations(current):

    punctuations = string.punctuation
    translatetable = str.maketrans("","",punctuations)
    target = current.translate(translatetable)

    return target

f = open("data/stopwords.txt","r")
#stop words 
stopwords = f.read().splitlines()
for i in range(len(stopwords)):
    stopwords[i] = remove_punctuations(stopwords[i])
stopwords = set(stopwords)


class InvertedIndex():
    
    def __init__(self):
        self.index = {}
        self.docmap = {}

    def  __add_document(self, doc_id, text):
        tokens = tokenizeText(text)
        for token in tokens:
            if token not in self.index:
                self.index[token] = set()
            self.index[token].add(doc_id)

    def get_documents(self,term):
        if term not in self.index:
            return []
        res = list(self.index[term])
        res.sort()
        return res
    
    def Build(self):
        with open("data/movies.json","r") as file:
            data = json.load(file)

        for movie in data["movies"]:
            
            self.docmap[movie["id"]] = movie
            text = f"{movie['title']} {movie['description']}"
            self.__add_document(movie["id"],text)

    def save(self):
        
        with open("cache/index.pkl","wb") as index_file:
            pickle.dump(self.index,index_file)
        
        with open("cache/docmap.pkl","wb") as docmap_file:
            pickle.dump(self.docmap,docmap_file)


    def load(self):
        with open("cache/index.pkl", "rb") as index_file:
            self.index = pickle.load(index_file)
            
        with open("cache/docmap.pkl", "rb") as docmap_file:
            self.docmap = pickle.load(docmap_file)


stemmer = PorterStemmer()
def tokenizeText(text:str,stop_words = stopwords):
    nopunc = remove_punctuations(text)
    split_text = nopunc.lower().split()
    valid_token = []
    for i in split_text:
        if i not in stop_words:
            valid_token.append(i)

    filtered_tokens = []
    for token in valid_token:
        filtered_tokens.append(stemmer.stem(token))
    return filtered_tokens



def build_command():
    inverted_index = InvertedIndex()
    inverted_index.Build()
    inverted_index.save()
    # print(f"First document for token 'merida' = {inverted_index.get_documents('merida')[0]}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Keyword Search CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    search_parser = subparsers.add_parser("search", help="Search movies using keywords")
    search_parser.add_argument("query", type=str, help="Search query")
    subparsers.add_parser("build", help="Build the inverted index and save it to disk")
    args = parser.parse_args()
    


    match args.command:
        case "build":
            build_command()
        case "search":
            InvIndex = InvertedIndex()
            try: 
                InvIndex.load()
            except FileNotFoundError:
                print("Error: File not Found, Try using build command first ")
            
            filtered_query = tokenizeText(args.query,stop_words=stopwords)
            
            matched_ids = set()
            for token in filtered_query:
                doc_ids = InvIndex.get_documents(token)
                
                for doc_id in doc_ids:
                    matched_ids.add(doc_id)
                    if len(matched_ids) == 5:
                        break
                
                if len(matched_ids) == 5:
                    break
            
            print(matched_ids)

            # for i in range(len(res)):
            #     print(f"{i+1}. {res[i]}")            
            sorted_doc_ids = sorted(list(matched_ids))
            
            # Print the final resulting document details cleanly
            for i, doc_id in enumerate(sorted_doc_ids):
                print(f"{i+1}. [ID: {doc_id}] {InvIndex.docmap[doc_id]['title']}")

        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
    
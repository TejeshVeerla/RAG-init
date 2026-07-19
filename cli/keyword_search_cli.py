import string
import argparse
import json
import io
from nltk.stem import PorterStemmer

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
        self.docmap[doc_id] = text
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
            text = f"{movie['title']} {movie['description']}"
            self.__add_document(movie["id"],text)
    def save(self):
        
        with open("cache/index.pkl","wb") as index_file:
            pickle.dump(self.index,index_file)
        
        with open("cache/docmap.pkl","wb") as docmap_file:
            pickle.dump(self.docmap,docmap_file)


def build_command():
    inverted_index = InvertedIndex()
    inverted_index.Build()
    inverted_index.save()
    print(f"First document for token 'merida' = {inverted_index.get_documents('merida')[0]}")

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

            with open("data/movies.json","r") as file:
                d = json.load(file)
            res = []
            
            filtered_query = tokenizeText(args.query,stop_words=stopwords)


            print(f"Searching for: {filtered_query}")

            for movie in d["movies"]:
                movie_title = movie["title"]
                filtered_title = tokenizeText(movie_title,stop_words=stopwords) 
                for query in filtered_query:
                   
                    if query in filtered_title:
                        res.append(movie_title)
                        break
                        
            for i in range(len(res)):
                print(f"{i+1}. {res[i]}")


        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
    
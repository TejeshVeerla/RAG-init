import os
import math
import string
import argparse
import json
import io
from nltk.stem import PorterStemmer
import sys
import pickle
from collections import Counter

#HELPER FUNCTIONS AND VARIABLES

BM25_K1 = 1.5
BM25_B = 0.75

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

def tokenize_single_term(text:str):
    token = tokenizeText(text)
    if len(token) != 1:
        raise ValueError("Expected only one token")
    return "".join(token)

def bm25_idf_command(term):
    invIndex = InvertedIndex()
    try:
        invIndex.load()
    except FileNotFoundError:
        print("Error: File not Found, Try using build command first ")
    term = tokenize_single_term(term)
    bm25_value = invIndex.get_bm25_idf(term=term) 
    return float(bm25_value)


def bm25_tf_command(doc_id, term, k1=BM25_K1,b= BM25_B):
    invIndex = InvertedIndex()
    try:
        invIndex.load()
    except FileNotFoundError:
        print("Error: File not Found, Try using build command first ")
    term = tokenize_single_term(term)
    return invIndex.get_bm25_tf(doc_id=doc_id,term=term,k1=k1,b=b)


class InvertedIndex():
    
    def __init__(self):
        self.index = {}
        self.docmap = {}
        self.term_frequencies = {}
        self.doc_lengths = {}
        self.doc_lengths_path = os.path.join("cache/", "doc_lengths.pkl")

    def  __add_document(self, doc_id, text):
        tokens = tokenizeText(text)
        self.doc_lengths[doc_id] = len(tokens)
        self.term_frequencies[doc_id] = Counter(tokens)
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
        with open("cache/term_frequencies.pkl","wb") as term_frequencies_file:
            pickle.dump(self.term_frequencies,term_frequencies_file)
        with open("cache/doc_lengths.pkl","wb") as doc_lengths_file:
            pickle.dump(self.doc_lengths,doc_lengths_file)

    def load(self):
        with open("cache/index.pkl", "rb") as index_file:
            self.index = pickle.load(index_file)
        with open("cache/docmap.pkl", "rb") as docmap_file:
            self.docmap = pickle.load(docmap_file)
        with open("cache/term_frequencies.pkl", "rb") as term_frequencies_file:
            self.term_frequencies = pickle.load(term_frequencies_file)
        with open("cache/doc_lengths.pkl", "rb") as doc_lengths_file:
            self.doc_lengths = pickle.load(doc_lengths_file)
    
    def get_tf(self,doc_id,term):
        if doc_id not in self.term_frequencies:
            return 0
        if term not in self.term_frequencies[doc_id]:
            return 0
        return (self.term_frequencies[doc_id][term])

    def get_bm25_idf(self,term:str) -> float :
        df = len(self.index[term]) if term in self.index else 0
        N = len(self.docmap)
        bm25_idf = math.log((N-df+0.5) / (df+0.5)+1)
        return bm25_idf

    def get_bm25_tf(self, doc_id, term, k1=BM25_K1, b=BM25_B):
        raw_tf = self.get_tf(doc_id, term)
        doc_length = self.doc_lengths.get(doc_id, 0)
        avg_len = self.__get_avg_doc_length()
        if avg_len == 0:
            length_norm = 1.0
        else:
            length_norm = 1 - b + b * (doc_length / avg_len)
        bm25_tf = (raw_tf * (k1 + 1)) / (raw_tf + k1 * length_norm)
        return bm25_tf
        
    def __get_avg_doc_length(self) -> float:
        if not self.doc_lengths:
            return 0.0
        total = sum(self.doc_lengths.values())
        return total/len(self.doc_lengths)

    def bm25(self, doc_id, term):
        return self.get_bm25_idf(term)*self.get_bm25_tf(doc_id,term)
    
    def bm25_search(self, query, limit=5):
        tokens = tokenizeText(query)
        scores = {}
        for doc_id in self.docmap:
            score = 0.0
            for token in tokens:
                score+= self.bm25(doc_id,token)
            scores[doc_id] = score
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        final = []
        for ind,score in sorted_docs[:limit]:
            final.append(
                    {
                        "title":self.docmap[ind]['title'],
                        "id" : ind,
                        "score":score
                    }
                )

        

        return final



def build_command():
    inverted_index = InvertedIndex()
    inverted_index.Build()
    inverted_index.save()
    # print(inverted_index.term_frequencies[1])
    # print(f"First document for token 'merida' = {inverted_index.get_tf(1,'maya')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Keyword Search CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    search_parser = subparsers.add_parser("search", help="Search movies using keywords")
    search_parser.add_argument("query", type=str, help="Search query")
    subparsers.add_parser("build", help="Build the inverted index and save it to disk")
    
    tf_parser = subparsers.add_parser("tf",help="add doc id and term to get term frequency")
    tf_parser.add_argument("doc_id",type=int, help = "Enter the document id you want to check the frequency from:")
    tf_parser.add_argument("term",type=str,help="add the term to check the frequency")
    
    idf_parser = subparsers.add_parser("idf",help="To retrieve information about Inverse document frequency of a term")
    idf_parser.add_argument("term",type=str,help="add the term to check idf")

    tfidf_parser = subparsers.add_parser("tfidf",help="Retrieve tfidf value to given term")
    tfidf_parser.add_argument("doc_id",type=int, help = "Enter the document id you want to check the frequency from:")
    tfidf_parser.add_argument("term",type=str,help="add the term to check tf-idf")

    bm25_idf_parser = subparsers.add_parser("bm25idf", help="Get BM25 IDF score for a given term")
    bm25_idf_parser.add_argument("term", type=str, help="Term to get BM25 IDF score for")
    
    bm25_tf_parser = subparsers.add_parser(
        "bm25tf", help="Get BM25 TF score for a given document ID and term"
    )
    bm25_tf_parser.add_argument("doc_id", type=int, help="Document ID")
    bm25_tf_parser.add_argument("term", type=str, help="Term to get BM25 TF score for")
    bm25_tf_parser.add_argument("k1", type=float, nargs='?', default=BM25_K1, help="Tunable BM25 K1 parameter")
    bm25_tf_parser.add_argument("b", type=float, nargs='?', default=BM25_B, help="Tunable BM25 b parameter")
    
    bm25search_parser = subparsers.add_parser("bm25search", help="Search movies using full BM25 scoring")
    bm25search_parser.add_argument("query", type=str, help="Search query")

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
        case "tf":
            doc_id = args.doc_id
            term = args.term
            term = tokenize_single_term(term)
            invIndex = InvertedIndex()
            
            try: 
                invIndex.load()
            except FileNotFoundError:
                print("Error: File not Found, Try using build command first ")

            print(invIndex.get_tf(doc_id,term))

        case "idf":
            invIndex = InvertedIndex()
            try: 
                invIndex.load()
            except FileNotFoundError:
                print("Error: File not Found, Try using build command first ")

            term = args.term
            term = tokenize_single_term(term)
            idf_value = math.log((len(invIndex.docmap)+1)/(len(invIndex.index[term])+1)) 
            print(f"Inverse document frequency of '{args.term}': {idf_value:.2f}")

        case "tfidf":
            invIndex = InvertedIndex()
            try:
                invIndex.load()
            except FileNotFoundError:
                print("Error: File not Found, Try using build command first ")

            term = tokenize_single_term(args.term)
            idf_value = math.log((len(invIndex.docmap)+1)/(len(invIndex.index[term])+1)) 
            tf_idf = invIndex.get_tf(args.doc_id,term)*idf_value 
            print(f"TF-IDF score of '{args.term}' in document '{args.doc_id}': {tf_idf:.2f}")
        
        case "bm25idf":
            bm25idf = bm25_idf_command(args.term)
            print(f"BM25 IDF score of '{args.term}': {bm25idf:.2f}")

        case "bm25tf":
            bm25tf = bm25_tf_command(args.doc_id,args.term)
            print(f"BM25 TF score of '{args.term}' in document '{args.doc_id}': {bm25tf:.2f}")
        
        case "bm25search":

            invIndex = InvertedIndex()
            try:
                invIndex.load()
            except FileNotFoundError:
                print("Error: File not Found, Try using build command first ")

            results = invIndex.bm25_search(args.query)
            for i, res in enumerate(results, 1):
                print(f"{i}. ({res['id']}) {res['title']} - Score: {res['score']:.2f}")
        case _:
            parser.print_help()



if __name__ == "__main__":
    main()

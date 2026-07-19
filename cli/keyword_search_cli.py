import string
import argparse
import json
import io
from nltk.stem import PorterStemmer

def remove_punctuations(current):

    punctuations = string.punctuation
    translatetable = str.maketrans("","",punctuations)
    target = current.translate(translatetable)

    return target

def main() -> None:
    parser = argparse.ArgumentParser(description="Keyword Search CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    search_parser = subparsers.add_parser("search", help="Search movies using keywords")
    search_parser.add_argument("query", type=str, help="Search query")

    args = parser.parse_args()


    with open("data/movies.json","r") as file:
        d = json.load(file)

    match args.command:
        case "search":

            stemmer = PorterStemmer()

            res = []
            query = args.query.lower().split(" ")

            f = open("data/stopwords.txt","r")
            #stop words 
            stopwords = f.read().splitlines()
            for i in range(len(stopwords)):
                stopwords[i] = remove_punctuations(stopwords[i])
            
            filtered_query = []
            for i in query:
                if i.lower() not in stopwords:
                    filtered_query.append(stemmer.stem(i.lower()))



            print(f"Searching for: {filtered_query}")

            for i in d["movies"]:
                current = i["title"]
                target = remove_punctuations(current)
                
                for q in filtered_query:
                   
                    if q in target.lower():
                        res.append(i["title"])
                        break
                        
            for i in range(len(res)):
                print(f"{i+1}. {res[i]}")


        case _:
            parser.print_help()

if __name__ == "__main__":
    main()
    
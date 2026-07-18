import argparse
import json

def test():
   print(d)

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
            res = []
            query = args.query
            print(f"Searching for: {query}")
            for i in d["movies"]:
                if query in i["title"]:
                    res.append(i["title"])
            for i in range(len(res)):
                print(f"{i+1}. {res[i]}")
        case _:
            parser.print_help()

if __name__ == "__main__":
    main()
    
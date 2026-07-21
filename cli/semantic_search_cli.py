import argparse
from lib.semantic_search import verify_model,embed_text,verify_embeddings,embed_query_text,SemanticSearch
import json
def main() -> None:
    parser = argparse.ArgumentParser(description="Semantic Search CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    embed_text_parser = subparsers.add_parser("embed_text")
    embed_text_parser.add_argument("text",type=str)
    
    verify_embeddings_parser = subparsers.add_parser("verify_embeddings")
    
    embed_query_parser = subparsers.add_parser("embed_query")
    embed_query_parser.add_argument("query",type=str)

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query",type=str)
    search_parser.add_argument("--limit",type=int, default=5)

    subparsers.add_parser("verify")

    args = parser.parse_args()

    match args.command:
        case "verify":
            verify_model()
        case "embed_text":
            embed_text(args.text)
        case "verify_embeddings":
            verify_embeddings()
        case "embed_query":
            embed_query_text(args.query)
        case "search":
            ss_instance = SemanticSearch()
            with open("data/movies.json", "r") as movies_file:
                movies = json.load(movies_file)
                documents = movies["movies"]
            ss_instance.load_or_create_embeddings(documents)

            results = ss_instance.search(args.query, args.limit)

            for i, res in enumerate(results, start=1):
                print(f"\n{i}. {res['title']} (Score: {res['score']:.4f})")
                print(f"   {res['description']}")
        case _:
            parser.print_help()

if __name__ == "__main__":
    main()
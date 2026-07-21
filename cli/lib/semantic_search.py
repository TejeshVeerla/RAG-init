from sentence_transformers import SentenceTransformer

#helpful functions and variables declared below
def verify_model():
    ss_instance = SemanticSearch()
    model = ss_instance.model
    print(f"Model loaded: {model}")
    print(f"Max sequence length: {model.max_seq_length}")


#class 
class SemanticSearch():
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')


verify_model()
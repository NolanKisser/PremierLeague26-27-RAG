import torch
from transformers import AutoTokenizer, AutoModel

class Embedder:
    """
    Generates text embeddings using a Hugging Face Transformer model in PyTorch.
    """
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        # Force CPU execution as the RTX 5080 (sm_120) is not fully supported by this PyTorch build yet
        self.device = torch.device("cpu")
        print(f"Loading embedding model '{model_name}' on {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()

    def mean_pooling(self, model_output, attention_mask):
        """
        Performs mean pooling on token embeddings to get sentence embeddings.
        """
        token_embeddings = model_output[0] # First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        return sum_embeddings / sum_mask

    def embed_texts(self, texts):
        """
        Takes a list of strings and returns a PyTorch tensor of embeddings.
        """
        # Tokenize sentences
        encoded_input = self.tokenizer(texts, padding=True, truncation=True, max_length=256, return_tensors='pt').to(self.device)
        
        # Compute token embeddings
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        
        # Perform pooling
        sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
        
        # Normalize embeddings for cosine similarity
        sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
        
        return sentence_embeddings.cpu()

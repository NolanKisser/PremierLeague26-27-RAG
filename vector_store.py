import torch

class VectorStore:
    """
    A simple PyTorch-based vector database.
    Stores embeddings as a continuous 2D tensor and executes fast exact-K-NN via cosine similarity.
    """
    def __init__(self):
        self.embeddings = None
        self.metadata = []

    def add_embeddings(self, new_embeddings, new_metadata):
        """
        Appends new document chunks to the database.
        new_embeddings: torch.Tensor of shape (N, D)
        new_metadata: list of dicts of length N
        """
        if self.embeddings is None:
            self.embeddings = new_embeddings
        else:
            self.embeddings = torch.cat([self.embeddings, new_embeddings], dim=0)
        
        self.metadata.extend(new_metadata)

    def search(self, query_embedding, top_k=3):
        """
        Finds the top_k most similar chunks for a given query_embedding.
        query_embedding: torch.Tensor of shape (1, D)
        """
        if self.embeddings is None or self.embeddings.size(0) == 0:
            return []

        # query_embedding and self.embeddings should already be L2 normalized by the embedder.
        # Cosine similarity between normalized vectors is simply the dot product.
        # shape: (N,)
        similarities = torch.mm(self.embeddings, query_embedding.T).squeeze()
        
        # Handle case where there are fewer documents than top_k
        k = min(top_k, similarities.size(0))
        
        if k == 1:
            # If only 1 document exists, topk might behave differently, so we just return the max
            scores, indices = torch.max(similarities, dim=0, keepdim=True)
            if scores.dim() == 0:
                scores, indices = scores.unsqueeze(0), indices.unsqueeze(0)
        else:
            scores, indices = torch.topk(similarities, k)

        results = []
        for score, idx in zip(scores, indices):
            results.append({
                "score": score.item(),
                "metadata": self.metadata[idx.item()]
            })
            
        return results

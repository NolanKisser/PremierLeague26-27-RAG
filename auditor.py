import torch

class ComplianceAuditor:
    """
    Simulates the LLM auditing logic. Uses the Embedder and VectorStore to check draft text against regulations.
    """
    def __init__(self, embedder, vector_store):
        self.embedder = embedder
        self.vector_store = vector_store

    def audit_draft(self, draft_text):
        """
        Takes a draft document, embeds it, queries the vector store, and formulates a compliance report.
        """
        print("\n--- Compliance Audit Initiated ---")
        print(f"Draft Length: {len(draft_text)} characters")
        
        # 1. Embed the draft to find the most relevant regulations
        query_embedding = self.embedder.embed_texts([draft_text])
        
        # 2. Retrieve top matching clauses
        matches = self.vector_store.search(query_embedding, top_k=2)
        
        if not matches:
            return "No relevant regulations found in the database. Audit cannot be completed."

        # 3. Simulate generation of the compliance report
        # In a full deployment, this retrieved context would be appended to an LLM prompt.
        report = []
        report.append("### Compliance Audit Report\n")
        
        # We simulate the LLM flagging an issue based on the retrieved context.
        # If GDPR or HIPAA is retrieved, we flag a violation if the text seems to contradict it.
        # For prototype simplicity, we assume the draft needs revision based on the top match.
        
        top_match = matches[0]
        source = top_match["metadata"]["metadata"].get("source", "Unknown Regulation")
        retrieved_text = top_match["metadata"].get("text", "")
        
        report.append(f"**Potential Violation Detected**")
        report.append(f"The drafted clause may violate **{source}**.")
        report.append(f"\n**Relevant Legislation Cited:**")
        report.append(f"> \"{retrieved_text.strip()}\"")
        report.append(f"*(Relevance Score: {top_match['score']:.4f})*")
        
        report.append("\n**Suggested Revision:**")
        
        # Very simple mock logic for the prototype
        if "GDPR" in source:
            report.append("Ensure explicit, opt-in consent is obtained for data collection. Remove language implying pre-checked boxes or assumed consent.")
        elif "HIPAA" in source:
            report.append("Data must be heavily encrypted and access restricted. Explicitly mention HIPAA compliance protocols in the text.")
        else:
            report.append(f"Align the draft terms directly with the requirements outlined in {source}.")
            
        return "\n".join(report)

import os
from data_loader import DataLoader
from embedder import Embedder
from vector_store import VectorStore
from auditor import ComplianceAuditor

def setup_mock_data():
    """
    Creates mock public and private regulation documents.
    """
    os.makedirs("data/public", exist_ok=True)
    os.makedirs("data/private", exist_ok=True)
    
    gdpr_text = (
        "GDPR Article 7: Conditions for consent.\n"
        "1. Where processing is based on consent, the controller shall be able to demonstrate that the data subject has consented to processing of his or her personal data.\n"
        "2. If the data subject's consent is given in the context of a written declaration which also concerns other matters, the request for consent shall be presented in a manner which is clearly distinguishable from the other matters, in an intelligible and easily accessible form, using clear and plain language.\n"
    )
    with open("data/public/GDPR_Article_7.txt", "w", encoding='utf-8') as f:
        f.write(gdpr_text)
        
    hipaa_text = (
        "HIPAA Security Rule 45 CFR 164.312(a)(2)(iv): Encryption and Decryption.\n"
        "Implement a mechanism to encrypt and decrypt electronic protected health information.\n"
        "Covered entities must implement transmission security measures to guard against unauthorized access to electronic protected health information that is being transmitted over an electronic communications network."
    )
    with open("data/public/HIPAA_Security_Rule.txt", "w", encoding='utf-8') as f:
        f.write(hipaa_text)

    sop_text = (
        "Internal Data Handling Policy v2.1\n"
        "All customer data must be stored on localized European servers if the customer resides in the EU. "
        "Any cross-border transfer must be explicitly authorized by the Data Protection Officer."
    )
    with open("data/private/Internal_SOP.txt", "w", encoding='utf-8') as f:
        f.write(sop_text)

def main():
    print("Initializing Compliance & Audit Co-Pilot (RegTech) Prototype...")
    
    # Setup mock regulatory files
    setup_mock_data()
    print("Mock data generated in 'data/public' and 'data/private'.")

    # Load and Chunk Documents
    loader = DataLoader(chunk_size=300, overlap=50)
    public_chunks = loader.load_directory("data/public")
    private_chunks = loader.load_directory("data/private")
    all_chunks = public_chunks + private_chunks
    
    print(f"Loaded {len(all_chunks)} document chunks.")

    # Initialize PyTorch Embedder
    # Uses sentence-transformers, requires downloading ~90MB weights if not cached
    embedder = Embedder(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Generate Embeddings for all chunks
    print("Generating embeddings for regulatory documents...")
    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = embedder.embed_texts(texts)
    
    # Populate PyTorch Vector Store
    v_store = VectorStore()
    v_store.add_embeddings(embeddings, all_chunks)
    print("Documents successfully indexed into PyTorch Vector Store.")

    # Initialize Auditor
    auditor = ComplianceAuditor(embedder, v_store)

    # Run an Audit on a Draft Contract
    draft_contract = (
        "Marketing Data Collection Agreement:\n"
        "By signing up for our service, the user agrees to receive promotional emails. "
        "Consent is assumed by default unless the user emails support to opt-out manually. "
        "We also reserve the right to share basic telemetry with our US-based partners for analytics."
    )
    
    print("\nDraft Contract submitted for review:")
    print("--------------------------------------------------")
    print(draft_contract)
    print("--------------------------------------------------")
    
    report = auditor.audit_draft(draft_contract)
    print(report)

if __name__ == "__main__":
    main()

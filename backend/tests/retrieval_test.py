from services.retrieval import RetrievalService

results = RetrievalService.retrieve_similar_chunks("What does the document say about diabetes?")
print(len(results), "results retrieved")
print(results[0].chunk_text[:300])

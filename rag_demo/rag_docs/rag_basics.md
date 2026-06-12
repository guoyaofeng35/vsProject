# RAG Basics

RAG means Retrieval-Augmented Generation.

RAG solves a common problem: a language model may not know your private documents or latest project knowledge. Instead of asking the model from memory, RAG first retrieves relevant text from a document collection, then gives that text to the model as context.

A simple RAG pipeline has five steps:

1. Load documents.
2. Split documents into small chunks.
3. Search for chunks related to the question.
4. Put the top chunks into the prompt.
5. Ask the model to answer using only the provided context.

RAG is useful for knowledge bases, customer support, project documentation, policy search, and codebase Q&A.

Good RAG answers should cite the retrieved source files so users can check where the answer came from.

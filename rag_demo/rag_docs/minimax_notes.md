# MiniMax Notes

MiniMax can be used as the generation model in an agent or RAG application.

In this demo, MiniMax is optional. If the MINIMAX_API_KEY environment variable exists, the RAG program sends retrieved context and the user question to MiniMax. If the key is missing, the program still runs in local fallback mode.

The recommended project pattern is to keep API configuration outside code:

- MINIMAX_API_KEY stores the API key.
- MINIMAX_BASE_URL stores the API endpoint.
- MINIMAX_MODEL stores the model name.

Keeping these values in environment variables avoids leaking secrets into source code and makes it easy to change models.

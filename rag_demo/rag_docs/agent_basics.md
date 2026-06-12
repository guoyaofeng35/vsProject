# Agent Basics

Agent is a program that can receive a user goal, decide what to do next, call tools, observe tool results, and continue until it can answer.

The simplest agent loop has four steps:

1. Think: understand the user goal.
2. Act: choose a tool or answer directly.
3. Observe: read the tool result.
4. Answer: explain the result to the user.

Tools make an agent useful. Common tools include calculator, file search, web search, database query, code runner, calendar, and memory.

Memory helps an agent remember user preferences, past facts, and project context. Short-term memory usually lives in the current conversation. Long-term memory can be saved in a file or database.

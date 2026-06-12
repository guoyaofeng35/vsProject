# RAG Demo

这个目录是独立可运行的 RAG 示例。

流程：

1. 从 `rag_demo/rag_docs` 读取 Markdown 文档
2. 把文档切成小片段
3. 根据问题检索最相关片段
4. 有 `MINIMAX_API_KEY` 时调用 MiniMax 生成答案
5. 没有 API Key 时输出本地检索结果

## 运行

```powershell
python rag_demo/rag_demo.py
```

或双击：

```text
rag_demo/run_rag.bat
```

## 可问的问题

```text
什么是 RAG？
Agent 的基本循环是什么？
MiniMax API Key 应该放在哪里？
RAG 适合什么场景？
```

## 接入 MiniMax

```powershell
$env:MINIMAX_API_KEY="你的 MiniMax API Key"
$env:MINIMAX_BASE_URL="https://api.minimax.chat/v1"
$env:MINIMAX_MODEL="MiniMax-M1"
python rag_demo/rag_demo.py
```

## 添加自己的资料

把 `.md` 文件放进：

```text
rag_demo/rag_docs
```

重新运行即可检索新资料。

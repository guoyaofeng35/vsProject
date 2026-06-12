# MiniMax Agent 学习项目

这是一个可执行的 Agent 小项目，核心思路是：

1. 用户输入任务
2. 大模型决定是否调用工具
3. 程序执行本地工具
4. Agent 汇总工具结果并回答

没有 `MINIMAX_API_KEY` 时，项目会自动使用本地规则模式，方便你先学习 Agent 的运行流程。

## 运行

```powershell
python agent_demo/main.py
```

## 配置 MiniMax

在 PowerShell 中设置环境变量：

```powershell
$env:MINIMAX_API_KEY="你的 MiniMax API Key"
$env:MINIMAX_BASE_URL="https://api.minimax.chat/v1"
$env:MINIMAX_MODEL="MiniMax-M1"
python agent_demo/main.py
```

如果你的 MiniMax 控制台显示了不同的 Base URL 或模型名，只需要改环境变量，不用改代码。

## 可用命令

```text
时间
计算 12 * (8 + 3)
记住 学习目标: 掌握 agent 工具调用
查看记忆
搜索 README
计划 做一个天气查询 agent
退出
```

也支持英文别名：

```text
time
calc 12 * (8 + 3)
remember goal: learn agent tool use
memory
search README
plan build a weather agent
exit
```

## 文件说明

```text
agent_demo/
  main.py           # 程序入口
  agent.py          # Agent 决策、工具调用、回答组织
  minimax_client.py # MiniMax Chat Completions 请求封装
  tools.py          # 本地工具：计算、时间、文件搜索、计划
  memory.json       # 记忆文件
```

## 学习重点

- `MiniMaxAgent._decide()`：让模型输出结构化 JSON 决策
- `MiniMaxAgent._run_tool()`：把模型选择映射到真实工具
- `MiniMaxAgent._format_answer()`：把思考、工具、结果展示出来
- `RuleAgent`：没有 API Key 或接口失败时的本地兜底

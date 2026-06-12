import json
import os
import re
from pathlib import Path

from minimax_client import MiniMaxClient
from tools import ToolResult, calculate, current_time, make_plan, search_files


SYSTEM_PROMPT = """You are a learning-oriented MiniMax agent.
Choose exactly one tool, then return JSON only.

Tools:
- calculator: arithmetic expression only
- clock: current local time
- memory_save: save one key/value memory
- memory_read: read all memory
- file_search: search files by name in this project
- planner: create a short step-by-step plan
- none: answer directly

Required JSON shape:
{
  "thought": "brief reason",
  "tool": "calculator | clock | memory_save | memory_read | file_search | planner | none",
  "args": {
    "expression": "",
    "key": "",
    "value": "",
    "query": "",
    "goal": ""
  },
  "final": ""
}

Never return markdown. Never wrap the JSON in code fences.
"""


class RuleAgent:
    def decide(self, text: str) -> dict:
        lowered = text.lower().strip()

        if text.startswith("计算"):
            return self._decision("user needs calculation", "calculator", expression=text[2:].strip())
        if lowered.startswith(("calc ", "calculate ")):
            return self._decision("user needs calculation", "calculator", expression=text.split(" ", 1)[1].strip())
        if text in {"时间", "现在几点", "当前时间"} or lowered in {"time", "now"}:
            return self._decision("user needs current time", "clock")
        if text.startswith("记住"):
            key, value = self._split_memory(text[2:].strip())
            return self._decision("user wants to save memory", "memory_save", key=key, value=value)
        if lowered.startswith("remember "):
            key, value = self._split_memory(text[9:].strip())
            return self._decision("user wants to save memory", "memory_save", key=key, value=value)
        if text in {"查看记忆", "记忆"} or lowered in {"memory", "show memory", "mem"}:
            return self._decision("user wants to read memory", "memory_read")
        if text.startswith("搜索"):
            return self._decision("user wants to search files", "file_search", query=text[2:].strip())
        if lowered.startswith("search "):
            return self._decision("user wants to search files", "file_search", query=text[7:].strip())
        if text.startswith("计划"):
            return self._decision("user wants a plan", "planner", goal=text[2:].strip())
        if lowered.startswith("plan "):
            return self._decision("user wants a plan", "planner", goal=text[5:].strip())

        return self._decision("no local tool matched", "none", final=f"I received: {text}")

    def _decision(self, thought: str, tool: str, **kwargs) -> dict:
        args = {"expression": "", "key": "", "value": "", "query": "", "goal": ""}
        args.update(kwargs)
        return {"thought": thought, "tool": tool, "args": args, "final": kwargs.get("final", "")}

    def _split_memory(self, detail: str) -> tuple[str, str]:
        for sep in (":", "：", "="):
            if sep in detail:
                key, value = detail.split(sep, 1)
                return key.strip(), value.strip()
        return "note", detail


class MiniMaxAgent:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.memory_path = project_root / "agent_demo" / "memory.json"
        self.memory = self._load_memory()
        self.client = MiniMaxClient()
        self.rule_agent = RuleAgent()
        self.debug = os.getenv("AGENT_DEBUG", "").lower() in {"1", "true", "yes"}

    def run(self, user_input: str) -> str:
        text = user_input.strip()
        if not text:
            return "请输入一个任务。"

        decision = self._decide(text)
        tool_result = self._run_tool(decision)
        return self._format_answer(decision, tool_result)

    def _decide(self, text: str) -> dict:
        if not self.client.enabled:
            return self.rule_agent.decide(text)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Memory: {json.dumps(self.memory, ensure_ascii=False)}\nUser: {text}"},
        ]

        try:
            raw = self.client.chat(messages)
            if self.debug:
                print(f"\n[MiniMax raw response]\n{raw}\n")
            return self._parse_decision(raw, text)
        except Exception as exc:
            fallback = self.rule_agent.decide(text)
            fallback["thought"] = f"MiniMax call failed, using local rules: {exc}"
            return fallback

    def _parse_decision(self, raw: str, original_text: str) -> dict:
        raw = (raw or "").strip()
        if not raw:
            raise ValueError("MiniMax returned empty content.")

        json_text = self._extract_json(raw)
        try:
            decision = json.loads(json_text)
        except json.JSONDecodeError as exc:
            if self._looks_like_tool_answer(raw):
                return self.rule_agent.decide(original_text)
            raise ValueError(f"MiniMax did not return valid JSON. Raw content: {raw[:300]}") from exc

        return self._normalize_decision(decision)

    def _extract_json(self, raw: str) -> str:
        text = raw.strip()
        fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fence:
            return fence.group(1).strip()

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]

        return text

    def _looks_like_tool_answer(self, raw: str) -> bool:
        lowered = raw.lower()
        keywords = ["time", "clock", "calculate", "calculator", "memory", "search", "plan"]
        return any(word in lowered for word in keywords)

    def _normalize_decision(self, decision: dict) -> dict:
        allowed = {"calculator", "clock", "memory_save", "memory_read", "file_search", "planner", "none"}
        tool = str(decision.get("tool", "none")).strip()
        if tool not in allowed:
            tool = "none"

        args = decision.get("args")
        if not isinstance(args, dict):
            args = {}

        normalized_args = {"expression": "", "key": "", "value": "", "query": "", "goal": ""}
        normalized_args.update({key: str(value) for key, value in args.items() if value is not None})

        return {
            "thought": str(decision.get("thought", "")),
            "tool": tool,
            "args": normalized_args,
            "final": str(decision.get("final", "")),
        }

    def _run_tool(self, decision: dict) -> ToolResult:
        tool = decision.get("tool", "none")
        args = decision.get("args") or {}

        if tool == "calculator":
            return calculate(args.get("expression", ""))
        if tool == "clock":
            return current_time()
        if tool == "memory_save":
            return self._save_memory_item(args.get("key", "note"), args.get("value", ""))
        if tool == "memory_read":
            return self._read_memory()
        if tool == "file_search":
            return search_files(args.get("query", ""), self.project_root)
        if tool == "planner":
            return make_plan(args.get("goal", ""))
        if tool == "none":
            return ToolResult("none", decision.get("final", "我可以继续帮你分析这个问题。"))

        return ToolResult("error", f"Unknown tool: {tool}")

    def _format_answer(self, decision: dict, result: ToolResult) -> str:
        return (
            f"Agent 思考: {decision.get('thought', '无')}\n"
            f"选择工具: {result.name}\n"
            f"执行结果:\n{result.output}"
        )

    def _save_memory_item(self, key: str, value: str) -> ToolResult:
        key = (key or "note").strip()
        value = (value or "").strip()
        self.memory[key] = value
        self.memory_path.write_text(json.dumps(self.memory, ensure_ascii=False, indent=2), encoding="utf-8")
        return ToolResult("memory_save", f"已记住: {key} = {value}")

    def _read_memory(self) -> ToolResult:
        if not self.memory:
            return ToolResult("memory_read", "当前没有记忆。")
        lines = [f"- {key}: {value}" for key, value in self.memory.items()]
        return ToolResult("memory_read", "\n".join(lines))

    def _load_memory(self) -> dict:
        if not self.memory_path.exists():
            return {}
        try:
            return json.loads(self.memory_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

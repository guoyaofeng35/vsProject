#!/usr/bin/env python3
"""从会议 JSON 或非标准文本生成中文 Markdown 会议纪要。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def text(value: Any, fallback: str = "未提供") -> str:
    if value is None or value == "":
        return fallback
    return str(value)


def list_section(items: Any) -> str:
    if not items:
        return "- 未提供"
    if not isinstance(items, list):
        return f"- {items}"
    return "\n".join(f"- {text(item)}" for item in items)


def attendees_line(attendees: Any) -> str:
    if isinstance(attendees, list) and attendees:
        return "、".join(str(item) for item in attendees)
    return text(attendees)


def action_table(items: Any) -> str:
    header = "| 事项 | 负责人 | 截止日期 | 状态 |\n| --- | --- | --- | --- |"
    if not items:
        return f"{header}\n| 未提供 | 未提供 | 未提供 | 未提供 |"

    rows: list[str] = []
    for item in items:
        if isinstance(item, dict):
            rows.append(
                "| {task} | {owner} | {due} | {status} |".format(
                    task=text(item.get("task")),
                    owner=text(item.get("owner")),
                    due=text(item.get("due")),
                    status=text(item.get("status")),
                )
            )
        else:
            rows.append(f"| {text(item)} | 未提供 | 未提供 | 未提供 |")
    return "\n".join([header, *rows])


def clean_line(line: str) -> str:
    return re.sub(r"^[\s#>*\-•·\d.、）)]+", "", line).strip()


def split_people(value: str) -> list[str]:
    value = re.sub(r"^(参会人|参会|与会人|与会|参加人员|人员)\s*[:：]?", "", value).strip()
    return [item.strip() for item in re.split(r"[、,，;；\s]+", value) if item.strip()]


def parse_value_after_label(line: str, labels: tuple[str, ...]) -> str | None:
    pattern = r"^(?:" + "|".join(re.escape(label) for label in labels) + r")\s*[:：]\s*(.+)$"
    match = re.search(pattern, clean_line(line), flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def parse_action_item(line: str) -> dict[str, str]:
    item = clean_line(line)
    owner = "未提供"
    due = "未提供"
    status = "未提供"

    owner_match = re.search(r"(?:负责人|责任人|owner|@)\s*[:：]?\s*([\u4e00-\u9fa5A-Za-z0-9_]+)", item, re.IGNORECASE)
    if owner_match:
        owner = owner_match.group(1)

    due_match = re.search(
        r"(?:截止|到期|DDL|due)\s*[:：]?\s*([0-9]{4}[-/年][0-9]{1,2}[-/月][0-9]{1,2}日?|周[一二三四五六日天]|今天|明天|后天)",
        item,
        re.IGNORECASE,
    )
    if not due_match:
        due_match = re.search(r"([0-9]{4}[-/年][0-9]{1,2}[-/月][0-9]{1,2}日?)", item)
    if due_match:
        due = due_match.group(1)

    status_match = re.search(r"(?:状态|进度)\s*[:：]\s*([\u4e00-\u9fa5A-Za-z0-9_]+)", item)
    if status_match:
        status = status_match.group(1)

    task = re.sub(r"(负责人|责任人|owner|@)\s*[:：]?\s*[\u4e00-\u9fa5A-Za-z0-9_]+", "", item, flags=re.IGNORECASE)
    task = re.sub(
        r"(截止|到期|DDL|due)\s*[:：]?\s*([0-9]{4}[-/年][0-9]{1,2}[-/月][0-9]{1,2}日?|周[一二三四五六日天]|今天|明天|后天)",
        "",
        task,
        flags=re.IGNORECASE,
    )
    task = re.sub(r"(状态|进度)\s*[:：]\s*[\u4e00-\u9fa5A-Za-z0-9_]+", "", task)
    task = re.sub(r"[，,；;]+$", "", task).strip()

    return {"task": task or item, "owner": owner, "due": due, "status": status}


def parse_text_minutes(raw_text: str) -> dict[str, Any]:
    data: dict[str, Any] = {
        "title": "",
        "time": "",
        "location": "",
        "host": "",
        "attendees": [],
        "summary": "",
        "discussion_points": [],
        "decisions": [],
        "action_items": [],
        "risks": [],
        "next_steps": [],
    }
    section = "discussion_points"
    summary_lines: list[str] = []

    section_map = {
        "summary": ("摘要", "背景", "概述"),
        "discussion_points": ("讨论", "议题", "问题", "要点"),
        "decisions": ("决议", "决定", "结论"),
        "action_items": ("行动项", "待办", "任务", "todo", "action"),
        "risks": ("风险", "阻塞", "问题风险"),
        "next_steps": ("后续", "下一步", "跟进"),
    }

    for raw_line in raw_text.splitlines():
        line = clean_line(raw_line)
        if not line:
            continue

        title = parse_value_after_label(line, ("标题", "主题", "会议主题", "会议名称"))
        if title:
            data["title"] = title
            continue

        time = parse_value_after_label(line, ("时间", "日期", "会议时间"))
        if time:
            data["time"] = time
            continue

        location = parse_value_after_label(line, ("地点", "会议地点", "位置"))
        if location:
            data["location"] = location
            continue

        host = parse_value_after_label(line, ("主持人", "主持"))
        if host:
            data["host"] = host
            continue

        attendees = parse_value_after_label(line, ("参会人", "参会", "与会人", "与会", "参加人员"))
        if attendees:
            data["attendees"] = split_people(attendees)
            continue

        changed_section = False
        for key, labels in section_map.items():
            if any(label.lower() in line.lower() for label in labels) and len(line) <= 16:
                section = key
                changed_section = True
                break
        if changed_section:
            continue

        if section == "summary":
            summary_lines.append(line)
        elif section == "action_items":
            data["action_items"].append(parse_action_item(line))
        else:
            data[section].append(line)

    if not data["summary"]:
        data["summary"] = " ".join(summary_lines) if summary_lines else "未提供"
    if not data["title"]:
        data["title"] = "未命名会议"
    return data


def load_minutes_data(input_path: Path) -> dict[str, Any]:
    raw_text = input_path.read_text(encoding="utf-8")
    if input_path.suffix.lower() == ".json":
        return json.loads(raw_text)
    return parse_text_minutes(raw_text)


def make_minutes(data: dict[str, Any]) -> str:
    title = text(data.get("title"), "未命名会议")
    lines = [
        f"# 会议纪要：{title}",
        "",
        "## 会议信息",
        "",
        f"- 时间：{text(data.get('time'))}",
        f"- 地点：{text(data.get('location'))}",
        f"- 主持人：{text(data.get('host'))}",
        f"- 参会人：{attendees_line(data.get('attendees'))}",
        "",
        "## 摘要",
        "",
        text(data.get("summary")),
        "",
        "## 讨论要点",
        "",
        list_section(data.get("discussion_points")),
        "",
        "## 决议",
        "",
        list_section(data.get("decisions")),
        "",
        "## 行动项",
        "",
        action_table(data.get("action_items")),
        "",
        "## 风险与后续",
        "",
        "### 风险",
        "",
        list_section(data.get("risks")),
        "",
        "### 后续",
        "",
        list_section(data.get("next_steps")),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="会议 JSON、TXT 或 Markdown 文件路径")
    parser.add_argument("--output", type=Path, help="可选的 Markdown 输出路径")
    args = parser.parse_args()

    data = load_minutes_data(args.input)
    minutes = make_minutes(data)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(minutes, encoding="utf-8")
    else:
        print(minutes, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

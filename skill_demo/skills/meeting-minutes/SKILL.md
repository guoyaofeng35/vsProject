---
name: meeting-minutes
description: 生成、整理和结构化中文会议纪要。用于 Codex 需要把会议记录、会议转写、要点列表或结构化会议 JSON 转成清晰的中文 Markdown 纪要，包含会议摘要、讨论要点、决议、行动项、风险和后续跟进。
---

# 会议纪要

## 工作流

1. 先判断输入类型：会议转写文本、零散要点，或结构化 JSON。
2. 如果输入是长文本，先提取主题、参会人、讨论点、决议、行动项和风险；不要编造缺失信息。
3. 如果输入是 JSON、TXT 或 Markdown 文件，优先运行 `scripts/make_minutes.py` 生成稳定格式的 Markdown 纪要。
4. 需要调整措辞、粒度或行动项格式时，读取 `references/minutes-style.md`。

## 脚本

运行示例：

```bash
python scripts/make_minutes.py examples/sample_meeting.json
```

非标准文本示例：

```bash
python scripts/make_minutes.py examples/rough_meeting.txt
```

输出到文件：

```bash
python scripts/make_minutes.py examples/rough_meeting.txt --output output/minutes.md
```

## 输出要求

- 使用中文 Markdown。
- 保留明确的负责人、截止日期和状态。
- 行动项必须写成可执行动作，不要只写抽象目标。
- 不确定的信息标注为“未提供”，不要自行补全。
- 默认包含这些部分：会议信息、摘要、讨论要点、决议、行动项、风险与后续。

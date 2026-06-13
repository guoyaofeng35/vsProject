# Codex Skill Demo：会议纪要

这个目录包含一个可运行的中文 skill 示例：

```text
skill_demo/
  run_example.ps1
  skills/
    meeting-minutes/
      SKILL.md
      agents/openai.yaml
      scripts/make_minutes.py
      references/minutes-style.md
      examples/sample_meeting.json
```

在 PowerShell 中运行示例：

```powershell
.\skill_demo\run_example.ps1
```

校验 skill：

```powershell
python C:\Users\guoyaofeng\.codex\skills\.system\skill-creator\scripts\quick_validate.py D:\vsProject\skill_demo\skills\meeting-minutes
```

建议重点看：

- `SKILL.md`：skill 被触发后 Codex 会读取的中文说明。
- `agents/openai.yaml`：UI 元数据和默认 prompt。
- `scripts/make_minutes.py`：把会议 JSON 稳定转换成 Markdown 纪要的脚本。
- `references/minutes-style.md`：需要调整纪要风格时才读取的参考文件。

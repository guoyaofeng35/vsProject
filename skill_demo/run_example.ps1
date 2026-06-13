$SkillDir = Join-Path $PSScriptRoot "skills\meeting-minutes"
$Script = Join-Path $SkillDir "scripts\make_minutes.py"
$InputJson = Join-Path $SkillDir "examples\sample_meeting.json"

python $Script $InputJson

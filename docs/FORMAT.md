# 文件格式与字段映射

所有 JSONL 均为 UTF-8，一行一条 JSON 对象。时间统一整数毫秒，片段时间从 0 开始，区间为左闭右开 `[start_ms,end_ms)`。把秒乘以 1000 是单位转换；先导标注仍为秒级。原视频申报时钟单独保留，未核对前不可用它推算绝对证据坐标。

| 文件 | 主键 / 关系 | 内容 |
| --- | --- | --- |
| `data/clips.jsonl` | `clip_id`；多个片段可共享 `source_id` | 视频来源和申报窗口、实测音频时长、类别、主题、人数、状态 |
| `data/turns.jsonl` | `clip_id + turn_id` | 说话人、片段内轮次边界、时钟状态。仅评测侧使用 |
| `data/inputs.jsonl` | `id`，外键 `clip_id` | 问题、语言、时长。模型侧拿这一条和音频 |
| `data/references.jsonl` | `id`，外键 `clip_id` 与 `turn_ids` | 片段内说话人、身份、可听特征、语气、语义要点、证据区间与审核状态 |
| `data/migration_audit.jsonl` | `id` | 旧 ID、时间和轮次，聚合差异、修复和审计标记 |
| `data/summary.json` | 数据版本 | 样本数、来源数、类别和状态等 |
| `data/local/legacy_rounds.jsonl` | `id` | 转档时生成：原两轮结构（仅修复 JSON 引号）、合并版本，含旧转录、旧问题和双答文 |
| `data/local/media_manifest.jsonl` | `clip_id` | 转档时生成：本地相对路径、大小和 SHA-256 |

`identity_ref` 当前来自原标注，包含姓名和节目角色；`voice_ref` 为可听描述，保留音色、韵律、相对音量、节奏和可选口音听感。原 `voice_answer` 与 `identity_answer` 保留在本地归档；评分将两者共享的 What 和 When 统一成 `key_points` 与 `evidence_ms`。`tone_ref` 是编辑归一后的候选标签，`tone_source` 是旧标签文本，两者都未进入自动主分。

| 原字段 | 新字段与处理 |
| --- | --- |
| `video_id` / `media_id` | 目录中的真实片段名作为 `clip_id`；从链接取原视频 ID 形成 `source_id`。旧值进入审计 |
| `browser_start_timestamp`, `browser_end_timestamp` | `source_window_reported_ms`；保留报告值，无法确认的另标记 |
| `speakers[].turns` / `speaker` | `turn_id` / 片段内 `speaker_id`；身份和可听描述只放评测侧 |
| `start_time`, `end_time` | 轮次用 `start_ms`, `end_ms`；题目用区间列表 `evidence_ms` |
| `question` / `transcription` | 重写题目以减少泄漏；完整原转录留本地，迁移时做证据对照 |
| 第二轮 `turn_id` | `turn_ids` 数组，支持多轮；参考证据为对应轮次区间的并集 |

下例来自 `wsw_0018`。它有两个证据区间，中间 1 秒为另一位说话人的插话。可先查看对应文件的完整行：

```json
{
  "id": "wsw_0018",
  "speaker_id": "spk_02",
  "evidence_ms": [[10000, 26000], [27000, 59000]],
  "answer": "A situation cannot be changed and must be accepted. A problem has a solution, even if it is uncomfortable."
}
```

预测 JSONL 中 `id` 必填。缺少 `speaker_id` 或 `evidence_ms` 对应分数为 0；`identity_name` 和 `answer` 可选。若评测内容答案，可另建人工判断 JSONL：

```json
{"id":"wsw_0018","point_scores":[1,1],"material_contradiction":false}
```

```bash
python3 -m wsw.score predictions.jsonl --judgments judgments.jsonl --out results.json
```

机器可读 Schema 位于 `schemas/`；跨文件的 ID、证据对应、媒体时长、状态和组别关系由 `python3 -m wsw.validate` 核查。正式版改用精确到证据句子的时间时，应另记录子区间与对应轮次关系，并更新验证规则。

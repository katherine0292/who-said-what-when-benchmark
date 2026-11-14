# Who Said What When｜多人对话音频理解 Benchmark

给模型一段访谈音频和一道自然语言问题，要求模型指出**哪位说话人、表达了什么、哪些时间段能支持答案**。同一个问题可以有多个不连续的证据段。项目包含中文标注手册、数据说明、可复现的转换和评分工具，以及由现有标注整理而成的先导数据。

> **版本 `0.1.0-pilot`**：25 道英文题、25 个音频片段、5 个原始视频、178 条原始发言轮次，音频合计约 94 分 47 秒。18 道已做文本对齐，7 道标记为优先回听。所有样本仍属于先导集；当前没有双人听审后的金标，也没有独立测试集。

## 这是什么标注？

这是**以声音和对话内容为证据的说话人归因、内容理解和时间定位标注**。第一轮为完整片段建立说话人、轮次、转录、时间和语气信息；第二轮从片段设计有唯一答案的问答，关联能证明答案的轮次。现有主题包括美食与餐馆文化、身份认同与心理适应、青少年发展、访谈中的影响与决策观点，以及个人行动和职业角色。数据记录的是说话人的表述和观点；对话中的研究、心理和行为主张不会因为被收录而得到证实。

核心问题是：模型能不能把一条有意义的回答**归给对的人，并定位到真正说出它的地方**？一份流畅的摘要可能混淆主持人与嘉宾、忽略反问或否定、把两段不同发言拼成一句，或者给出无法复核的时间。将三项能力拆开评分，可以区分归因、理解和检索错误。适合会议纪要溯源、访谈检索和音频助手的早期诊断。

## 从这里开始

| 入口 | 适用场景 |
| --- | --- |
| [项目说明与数据卡](docs/DATA_CARD.md) | 回答标注对象、主题、背景、业务价值、数据构成与局限 |
| [标注手册](docs/ANNOTATION_GUIDE.md) | 从选素材到双人复核、仲裁和验收；含边界例子 |
| [Benchmark 协议](docs/BENCHMARK_PROTOCOL.md) | 输入条件、切分、评分口径、基线、扩展和发布条件 |
| [字段与样例](docs/FORMAT.md) | 核对模型输入、参考答案、预测格式和转档审计 |
| [迁移审计与回听清单](docs/MIGRATION_AUDIT.md) | 查阅已修复项、7 道优先回听题和具体操作 |
| [输入](data/inputs.jsonl) · [参考答案](data/references.jsonl) · [汇总](data/summary.json) | 查看 25 条实际转换结果 |
| [机器可读 Schema](schemas/) | 校验接口和提交数据 |

## 快速复现

Python 3.10+；评分和验证只用标准库。以下命令在仓库根目录运行，不要求联网或读取音频。

```bash
python3 -m wsw.validate
python3 -m unittest discover -s tests -v
python3 -m wsw.score examples/whole_clip.jsonl
python3 -m wsw.score examples/middle_20pct.jsonl --out /tmp/wsw-report.json
```

已有本地原始材料时，可重新生成迁移产物和媒体清单；macOS 使用 `afinfo`，其他系统可用 `ffprobe`。探测器对 MP3 时长的估计可能略有差异。

```bash
python3 -m wsw.convert "/path/to/标注benchmark" --out /tmp/wsw-rebuilt
python3 -m wsw.validate --data /tmp/wsw-rebuilt
```

`data/inputs.jsonl` 是模型侧输入；`references.jsonl`、`turns.jsonl`、来源链接和审计日志只在评测方使用。真实音频跑分时，按本地媒体清单提供与题目匹配的 MP3。仓库未随附音视频、完整第三方转录或原始答文；本地迁移会将它们的索引和原始文字另存至忽略目录 `data/local/`。当前数据与素材未声明开放再分发许可。

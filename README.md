# Academic Writing Humanizer · v2

面向 research proposal、research statement 和导师联系材料的写作与编辑 skill，可供 Claude Code、Codex 等支持本地技能文件的 agent 使用。

A portable skill for drafting and editing academic prose with verified facts, clear reasoning, natural expression, and contextual style review. It preserves substantive meaning and distinguishes editorial judgments from actual detector results.

## 能做什么

- **内容与逻辑**：核对背景、研究问题、数据方法、导师匹配和文献支持。
- **结构与表达**：重写模板化段落，调整信息顺序、句式、措辞和阅读节奏。
- **个人声音**：根据使用者提供的真实写作样本进行校准；没有样本时明确说明尚未校准。
- **核验与记录**：分别检查研究含义和阅读流畅度，保存实际修改与待确认事项。

v2 保留 A–I 九个模块，并增加 Wikipedia 主页面及 Style、Markup 扩展页的完整情境映射：101 个编号标题、82 个末级条目。父子标题重叠，不代表 101 种独立特征。历史观察、维基专属格式和无效判断不会被当作通用禁令。

这个 skill 不保证避开 Turnitin 或其他检测器，也不会估计不存在的检测百分比。脚本输出是编辑候选提示，不是 AI 检测结果。

## 下载与安装

在本仓库页面选择 **Code → Download ZIP**，解压后复制整个 `academic-writing-humanizer` 文件夹。也可以克隆仓库，在本地跟踪后续修改：

```bash
git clone https://github.com/HunkBB/ai-humanizer.git
cd ai-humanizer
```

| 工具 | 个人技能位置 | 项目技能位置 |
|---|---|---|
| Claude Code | `~/.claude/skills/academic-writing-humanizer/` | `<项目>/.claude/skills/academic-writing-humanizer/` |
| Codex | `~/.agents/skills/academic-writing-humanizer/` | `<项目>/.agents/skills/academic-writing-humanizer/` |

不要只复制 `SKILL.md`：它引用 `references/`、`assets/` 和 `scripts/` 内的配套文件。首次安装后，通常无需每次使用都重新导入；更新时备份旧副本，再替换整个技能文件夹。

Claude Code 可用 `/academic-writing-humanizer`；Codex 可用 `$academic-writing-humanizer` 或可用的技能选择器。实际发现方式取决于客户端版本和设置。也可直接要求 agent 读取本地 `SKILL.md` 并执行。

本地技能文件的存在不等于已经安装到 ChatGPT 账号的技能目录。该安装方式应按当前客户端要求单独处理。

格式资料：[Claude Code skills](https://code.claude.com/docs/en/skills) · [OpenAI build skills](https://learn.chatgpt.com/docs/build-skills)。相关路径在本项目原始使用说明中于 2026-11-06 核查；后续客户端变更应查阅官方资料。

## 使用示例

提供初稿、目标读者、长度要求、可引用资料，以及自己的真实写作样本。把个人材料放在自己的项目中，不必提交到本仓库。

```text
读取 academic-writing-humanizer/SKILL.md。
按 A–I 全部模块及 Wikipedia 覆盖表审阅这篇 proposal。
先锁定事实与研究方法，再重写模板化段落；分别验证含义保真与阅读流畅度。
保留原稿，输出修订稿、代表性前后对照、来源记录及待我确认的问题。
```

轻度编辑可明确说“只做 light copyedit，保持内容和结构”。对完整重写，可要求保留逐项处理记录。稿件中的数据、背景、研究选择和使用声明仍需作者确认。

## 文件结构

| 路径 | 作用 |
|---|---|
| `academic-writing-humanizer/SKILL.md` | 入口与三轮工作流程 |
| `academic-writing-humanizer/references/` | 编辑细则、示例、来源、Wikipedia 覆盖和验收方法 |
| `academic-writing-humanizer/assets/` | 输入与审阅模板 |
| `academic-writing-humanizer/scripts/` | 本地检查及 HTML 差异工具 |
| `academic-writing-humanizer/agents/openai.yaml` | 可选界面信息 |
| `tests/` | 通用辅助脚本回归测试，不含个人稿件 |

## 本地工具与测试

辅助脚本仅使用 Python 标准库，不调用网络或检测服务，不需要 API key。本次发布准备在 Python 3.13 下运行测试；没有在 Claude Code 会话中做新的执行验证。

从仓库根目录运行：

```bash
python3 academic-writing-humanizer/scripts/review_text.py audit draft.md --output audit.json
python3 academic-writing-humanizer/scripts/review_text.py diff before.md after.md --output changes.html
python3 academic-writing-humanizer/scripts/style_audit.py draft.md --output style-audit.json
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

22 项测试检查脚本行为、输入保护、引用/占位符识别及误报控制。它们不验证检测规避效果、个人声音匹配或研究设计本身。`style_audit.py` 只做局部候选扫描，不能代替完整的语义审阅。

## 迭代与来源

修改工作流程时同步相关引用文件，保留真实测试记录。贡献说明见 [CONTRIBUTING.md](CONTRIBUTING.md)。

Wikipedia 来源采用 2026-11-07 检索的固定版本；它是社区观察性建议，不是通用检测算法。固定链接和完整署名见 [覆盖表](academic-writing-humanizer/references/wikipedia-coverage.md) 与 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

项目尚未为原创部分指定统一许可证；Wikipedia 改编映射文件按其明确标注的 CC BY-SA 4.0 提供。下载和使用时保留适用的署名及许可说明。

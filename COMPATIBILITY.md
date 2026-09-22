# 兼容性说明

VaultForge 课程版面向**支持 Markdown 文件读写与 Agent Skill 加载**的客户端。`SKILL.md` 是唯一契约来源，本文件只说明不同客户端的能力差异与降级路径，不新增或修改任何流程。

课程版**不依赖联网搜索**，也不需要 Firecrawl、Exa 或任何 MCP 研究后端。

---

## 客户端能力矩阵

| 能力 | 是否必需 | 支持时 | 不支持时 |
|---|---|---|---|
| 子 Agent 调度 | 可选 | `agents/*.md` 映射为子 Agent，课次之间可并行 | 主 Agent 按同一输入输出协议顺序执行 |
| 并行执行 | 可选 | 每个 Agent 同时处理 ≤10 篇课次 | 顺序执行，每批 ≤10 篇，协议不变 |
| PDF 精确抽取 | 可选 | 用 `context-extractor.py` 按 `source_range` 预取原文 | 回退到原始课件全文，禁止用摘要或笔记替代 |
| 文件访问 | **必需** | 直接读写课程目录；子 Agent 通过上下文包与 `allowed_writes` 访问 | 不满足则该客户端无法运行本 Skill |
| 中文 Markdown 读写 | **必需** | 生成 `00. 课程索引.md`、课次笔记、知识卡片 | 同上 |
| Web 研究 | 不需要 | —— | —— |

课程版不需要网络研究能力；阶段 0–5 全部依赖本地课件与本地文件操作。

---

## 逐客户端说明

### Claude Code

- 把整个仓库放入 Skills 目录（如 `~/.agents/skills/VaultForge`），可直接加载 `SKILL.md`。
- `agents/` 下的文件是平台无关的任务规格，交给客户端的子 Agent / Task 机制执行。
- 推荐为 `/VaultForge` 配置一个斜杠命令，或直接用自然语言触发（例如“用 VaultForge 处理 `~/vault/深度学习`”）。
- 并行时每个子 Agent 最多 10 篇课次；概念卡片必须在候选去重后才允许并行创建。

### Codex

- 同样把仓库整体放入 Skills 目录，或将 `SKILL.md` 显式加入上下文。
- 若客户端不支持并行，主 Agent 按阶段 0–5 顺序执行；**覆盖清单、`source_range` 和逐页账本不能省略**。
- 运行脚本时使用绝对路径，例如 `python3 ~/.agents/skills/VaultForge/scripts/course-manifest.py <课程目录> --output manifest.json`。

### Cursor

- 将仓库放到 Agent Skills 位置，或在对话中显式引用 `SKILL.md`。
- Cursor 可能不把 `agents/` 当作可执行子 Agent：此时把每个 `agents/*.md` 当作提示词规格，由主 Agent 依次执行。
- 保留默认的对话式目录选择流程，不要跳过阶段 0 的扫描汇报。

### 其他客户端

- 任何支持加载 Skill 目录的客户端都可以使用；自动识别失败时在对话中显式指明 `SKILL.md`。核心流程不依赖浏览器，四个脚本都是 CLI 工具。
- 若客户端不支持子 Agent，只使用“降级”一列的行为即可，输出契约与文件格式完全一致。

---

## 能力降级表

| 缺失能力 | 降级行为 | 禁止事项 |
|---|---|---|
| 无并行 / 无子 Agent | 主 Agent 按同一协议顺序执行，每批 ≤10 篇课次 | 不得省略覆盖清单、`source_range` 或逐页账本 |
| 无子 Agent 文件访问 | 由主 Agent 代读原文，再把上下文包交给后续步骤 | 不得凭标题或记忆补写未读内容 |
| 无 `pypdf` | 回退到原始课件全文（PDF 全文或宿主读取结果） | **禁止**用摘要、路线图或既有笔记替代原文 |
| 无精确页码 | 按 slide / 段落范围记录来源 | 不得伪造页码或引用 |
| 页面内容无法确认 | 保留账本记录并标记 `needs_review` | 不得假装已覆盖 |
| 子 Agent 超时或返回格式错误 | 只重试该任务，最多 2 次，超限标 `needs_review` | 不得重跑整门课程或伪造成功统计 |

---

## 脚本依赖

| 依赖 | 版本要求 | 用途 | 缺失后果 |
|---|---|---|---|
| Python 3 | 3.x | 运行全部脚本 | 无法生成清单、任务信封或上下文包 |
| `pypdf` | 建议安装 | PDF 按页精确抽取 | `context-extractor.py` 输出 stderr 警告、跳过该文件并把 `excerpt` 置空，需回退原始全文 |

安装：`pip install pypdf`。

---

## 四个脚本的用途与命令

### 1. course-manifest.py — 增量清单

```bash
python3 scripts/course-manifest.py <course_dir> --output manifest.json
```

扫描 `.pdf/.ppt/.pptx/.md/.txt/.doc/.docx/.html/.htm`，跳过 `01. 课程笔记`、`02. 知识卡片`、`00. 课程索引.md` 与隐藏文件；读取 `.course-progress.json` 中的 `sources[].hash` 判定 `NEW/UPDATED/DONE/REMOVED`，并汇总 `lessons`、`concepts`、`states`。**不修改课程目录。**

### 2. course-orchestrator.py — 任务信封

```bash
python3 scripts/course-orchestrator.py <course_dir> [--output .course-runtime.json]
```

为每个非 `DONE` 课件生成 `lesson-organizer` 任务信封，用 `course_contracts.validate_task` 校验必填字段、`schema_version`（`course-cn-v2`）与写入边界，输出含 `tasks`、`invalid_tasks` 的 `.course-runtime.json`。**不执行 Agent、不并发、不重试。**

### 3. context-extractor.py — 原文上下文包

```bash
python3 scripts/context-extractor.py <vault_path> <extract_manifest> -o context_packets.json [--buffer 1] [--note-filter note1.md,note2.md]
```

第二个参数是**临时抽取清单**：课程版不生成路线图，因此由阶段 1 账本生成一个只含 `**知识点标题**  \`source_range: ...\`` 行的临时 markdown（放 `/tmp`，不写入课程目录），格式见 [references/templates.md](./references/templates.md) 第 11.1 节。

解析 `source_range: {文件名}:{页码段}, ...`，支持单页 `102`、连续 `12-15`、混合 `12-15, 45-48, 102`、多文件 `A.pdf:12-15, B.md`。PDF 用 `pypdf` 按页抽取（`--buffer` 默认 ±1 页），Markdown/TXT 抽取全文。缺少 `pypdf` 或文件不可读时输出 stderr 警告、跳过该文件并将对应 `excerpt` 置空，Agent 需回退到原始全文。仅用于 PDF / Markdown / TXT 的精确抽取；PPT / DOCX / HTML 由 Agent 直接读取全文。

### 4. double-link-builder.py — 双链候选（可选）

```bash
python3 scripts/double-link-builder.py <course_dir> --output candidates.json
```

课程版默认不生成 MOC 与路线图，因此该脚本仅作为批量候选工具：产出 `pairs` 候选对，由主 Agent 按阶段 4 的六种关系白名单确认后写入。**脚本产出的结构亲和候选不得直接当作已确认关系。** 可选参数：`--mode full|strict|incremental`、`--new-notes`、`--output-suggestions`、`--tfidf-threshold`、`--structural-threshold`，以及可选的主题名位置参数。

---

## 测试

```bash
cd VaultForge
python3 -m unittest discover -s tests
```

预期全部通过（69 个测试），覆盖上下文抽取、双链候选、课程运行时契约与 Skill 完整性检查。

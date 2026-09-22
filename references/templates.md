# 课程版格式契约

本文件是 VaultForge 课程版所有产物的**唯一格式契约**，主 Agent 与子 Agent 共同遵守。流程控制、质量门槛与运行边界见 [SKILL.md](../SKILL.md)。

目录：

1. [命名与编号规则](#1-命名与编号规则)
2. [frontmatter 完整字段契约](#2-frontmatter-完整字段契约)
3. [课程索引模板](#3-课程索引模板)
4. [课次笔记模板](#4-课次笔记模板)
5. [知识卡片模板](#5-知识卡片模板)
6. [逐页知识点账本模板](#6-逐页知识点账本模板)
7. [覆盖清单（coverage）模板](#7-覆盖清单coverage模板)
8. [子 Agent 任务信封](#8-子-agent-任务信封)
9. [子 Agent 返回契约](#9-子-agent-返回契约)
10. [进度文件格式](#10-进度文件格式)
11. [关系标注格式](#11-关系标注格式)
12. [写入协议与自检](#12-写入协议与自检)
13. [禁止写法清单](#13-禁止写法清单)

---

## 1. 命名与编号规则

| 对象 | 规则 | 示例 |
|---|---|---|
| 课程目录 | 用户指定，`course_id` 取目录名 | `AIAA4220/` |
| **知识区** | 用户指定，默认 `50 Knowledge`，按领域分子目录 | `50 Knowledge/AI/` |
| 课次编号 | `L` + 两位序号，由课件在课程中的教学顺序决定 | `L01`、`L02` |
| 课次笔记文件 | `01. 课程笔记/{lesson_id} - {English Title}.md` | `01. 课程笔记/L02 - Embodied AI System Overview.md` |
| 知识卡片文件 | `{知识区}/{领域}/{English Concept Name}.md` | `50 Knowledge/AI/World Model.md` |
| 课程索引 | 固定 `00. 课程索引.md`（课程根目录唯一） | — |
| 知识库索引 | 固定 `_index.md`（知识区根目录唯一） | — |
| 临时文件 | `{目标文件名}.tmp`，rename 前不得视为产物 | `World Model.md.tmp` |
| `lesson_order` | 正整数，连续递增；**不使用文件名排序** | `1`、`2`、`3` |
| `concept_id` | 稳定 ID，kebab-case，不随标题变化 | `world-model`、`kalman-filter` |

`concept_id` 生成规则（与 `scripts/course_contracts.py` 的 `concept_id()` 一致）：

1. 对 `canonical_name` 做 NFKC 规范化、去首尾空白、`casefold`；
2. 删除所有空白、`_`、`-`、`–`、`—`；
3. 非 `[a-z0-9\u4e00-\u9fff]` 字符替换为 `-`，去首尾 `-`，截断到 48 字符；
4. 结果为空时回退为 `concept`。

因此 `CNN`、`cnn`、` C N N ` 得到同一个 `concept_id: cnn`。同名异义必须显式加语境后缀：`attention-nlp`、`attention-vision`。

---

## 2. frontmatter 完整字段契约

> ⚠️ `scripts/course-manifest.py` 只用 `^([A-Za-z_][\w-]*):\s*(.+)$` 解析**单行** `key: value`。`type`、`lesson_id`、`concept_id`、`canonical_name`、`status`、`vf_status`、`source_hash` 等关键字段必须写成单行标量，不要写成多行 YAML 列表或块。

### 2.1 课次笔记（`type: lesson`）

```yaml
---
type: lesson
course_id: AIAA4220
lesson_id: L02
lesson_order: 2
title: Embodied AI System Overview
aliases: [L02 具身 AI 系统概览]
source_file: Resource/AIAA 4220 L2.pdf
source_hash: sha256:3f1c...
source_range: "Resource/AIAA 4220 L2.pdf:1-63"
tags: [course/AIAA4220]
status: reviewed
vf: true
vf_version: course-cn-v2
vf_status: pristine
---
```

| 字段 | 必填 | 取值 | 说明 |
|---|---|---|---|
| `type` | ✅ | `lesson` | 固定值，清单脚本据此识别课次 |
| `course_id` | ✅ | 字符串 | 与课程目录名一致 |
| `lesson_id` | ✅ | `L\d{2}` | 课次编号 |
| `lesson_order` | ✅ | 正整数 | 排序依据，必须唯一 |
| `source_file` | ✅ | 相对路径 | 对应课件 |
| `source_hash` | ✅ | `sha256:...` | 用于增量判定与追溯 |
| `source_range` | ✅ | `文件:页码段` | 见第 11 节格式 |
| `status` | ✅ | 五态 | 见 2.3 |
| `vf` | ✅ | `true` | 标记 VaultForge 产物 |
| `vf_version` | ✅ | `course-cn-v2` | 产物格式版本（v2 = 学习笔记优先架构） |
| `vf_status` | ✅ | 三态 | 见 2.4 |

### 2.2 知识卡片（`type: concept`）

```yaml
---
type: concept
concept_id: world-model
canonical_name: World Model
aliases: [世界模型, WAM]
level: 核心                     # 核心 | 一般
courses: [AIAA4220]            # 归属课程，供课程索引反查
source_lessons: [L02]
source_files: [Resource/AIAA 4220 L2.pdf]
source_range: "Resource/AIAA 4220 L2.pdf:7-8"
tags: [concept/embodied-ai]
status: reviewed
vf: true
vf_version: course-cn-v2
vf_status: pristine
---
```

| 字段 | 必填 | 取值 | 说明 |
|---|---|---|---|
| `type` | ✅ | `concept` | 固定值 |
| `course_id` | ✅ | 字符串 | 与课程目录名一致 |
| `concept_id` | ✅ | 稳定 slug | 见第 1 节；禁止随标题变化 |
| `canonical_name` | ✅ | 字符串 | 标准名，用于卡片文件名与索引 |
| `aliases` | 推荐 | 单行数组 | 同义名，用于去重匹配 |
| `source_lessons` | ✅ | 单行数组 | 至少一个课次 |
| `source_files` | 推荐 | 单行数组 | 全部来源课件 |
| `source_range` | ✅ | `文件:页码段` | 可多段、多文件 |
| `status` / `vf` / `vf_version` / `vf_status` | ✅ | 同 2.1 | — |

### 2.3 `status` 五态

| 值 | 含义 | 由谁写入 |
|---|---|---|
| `draft` | 已建空壳，正文待写 | 主 Agent 建档时 |
| `filling` | 正在写入（`.tmp` 已生成） | 写作任务 |
| `filled` | 正文完整并已 rename | 写作任务 |
| `reviewed` | 通过审查 | 审查任务 |
| `needs_review` | 超出重试上限或存在无法确认内容，待人工处理 | 主 Agent |

### 2.4 `vf_status` 三态

| 值 | 含义 | 可否自动更新 |
|---|---|---|
| `pristine` | 系统生成后用户未编辑 | 可以（需用户确认） |
| `user_modified` | 检测到用户编辑（hash/mtime 变化） | 禁止覆盖 |
| `locked` | 用户显式冻结 | 禁止覆盖 |

---

## 3. 课程索引模板

课程索引由 `course-index-manager` 维护，含四个受管章节。**卡片部分使用 Dataview 自动生成**，不手工登记。

````markdown
---
type: index
course_id: AIAA4220
status: reviewed
vf: true
vf_version: course-cn-v2
vf_status: pristine
---

# AIAA 4220 Embodied AI — 课程索引

## 1. 课程目录

| 顺序 | 课次 | 主题 | 来源课件 | 状态 |
|---|---|---|---|---|
| 1 | [[L01 - ...]] | 具身智能导论 | `Resource/AIAA 4220 L1.pdf` | reviewed |

## 2. 本课关联的知识卡片

```dataview
TABLE level AS "分级", file.folder AS "领域", source_lessons AS "涉及课次"
FROM "50 Knowledge"
WHERE type = "concept" AND contains(courses, "AIAA4220")
SORT level ASC, file.name ASC
```

## 3. 知识点覆盖进度

| 课次 | 课件页数 | 覆盖 | 待复核 |
|---|---:|---:|---:|

## 4. 课件原文位置

- `Resource/xxx.pdf` — 讲次标题（N 页）
````

**知识库索引**（知识区根目录 `_index.md`）同样用 Dataview：

````markdown
# 知识库索引

## 全部概念卡片
```dataview
TABLE level AS "分级", courses AS "来源课程", file.folder AS "领域"
FROM "50 Knowledge"
WHERE type = "concept"
SORT level ASC, file.name ASC
```
````

> 已取消的旧章节：`## 课程目标`（合入索引开头说明）、`## 全课程知识网络`（知识关联改由 wikilink 表达）、手工的 `## 知识卡片索引` 表（改由 Dataview 生成）。

---

## 4. 课次笔记模板

完整格式规范见 [`obsidian-conventions.md`](./obsidian-conventions.md)。结构如下：

```markdown
---
type: lesson
course_id: AIAA4220
lesson_id: L02
lesson_order: 2
title: Embodied AI System Overview
aliases: [L02 具身 AI 系统概览]
source_file: Resource/AIAA 4220 L2.pdf
source_hash: sha256:...
source_range: "Resource/AIAA 4220 L2.pdf:1-63"
tags: [course/AIAA4220]
status: reviewed
vf: true
vf_version: course-cn-v2
vf_status: pristine
---

# L02 - Embodied AI System Overview

> [!abstract] 本讲要解决的问题
> （一两句：这节从哪里来、要解决什么）

## 0. 知识地图
### 0.1 本讲结构      # mermaid 图
### 0.2 覆盖的知识点   # 表：知识点 / 英文 / 课件页

## 1. <主题一>（课件 p.X–Y）
### 1.1 <小节>
### 1.2 <小节>

## N. 复习
### N.1 核心结论
### N.2 自测题         # > [!question]- 可折叠
### N.3 术语表         # 中英对照

## 来源
- 课件：`<路径>` —— <讲次标题>（N 页）
- 延伸阅读：…
```

**写作约束**：

1. 按**认知顺序**组织，不按课件页序；
2. 正文**不挂页码**，页码只在章节覆盖范围、知识点表、必要回看提示中出现；
3. H1 唯一，**禁止伪标题**（`**1.1 …**`），内容多的章节用 H3 细分；
4. 专业术语保留英文，末尾附术语表；
5. 关键处用 callout / mermaid / LaTeX；
6. **不得出现审计语言**（“课件未展开”等）与**课件项目符号**（●○■）。

---

## 5. 知识卡片模板

卡片存放在**知识区**（如 `50 Knowledge/AI/`），以概念为中心，**独立于课件**。完整格式规范见 [`obsidian-conventions.md`](./obsidian-conventions.md)。

```markdown
---
type: concept
concept_id: world-model
canonical_name: World Model
aliases: [世界模型, WAM]
level: 核心                     # 核心 | 一般
courses: [AIAA4220]
source_lessons: [L02]
source_files: [Resource/AIAA 4220 L2.pdf]
source_range: "Resource/AIAA 4220 L2.pdf:7-8"
tags: [concept/embodied-ai]
status: reviewed
vf: true
vf_version: course-cn-v2
vf_status: pristine
---

# World Model

> [!abstract] 一句话
> （对象 + 边界：它是什么、解决什么、与最相近概念的关键差别）

## 定义
## 为什么重要
## 核心机制 / 形式化
## 类型与实例
## 常见误区
## 相关概念
## 自测
## 参考
```

**硬性要求**：

- 文件名与 H1 用**英文概念名**；`concept_id` 用 kebab-case；
- 必须满足三条**建卡门槛**（跨课程复用 + 独立机制 + 领域通用）；
- **读者不打开课件也能读懂**——自检方式：假设看不到 PDF，卡里的每个术语是否都有交代？
- 八个段落齐全，`## 常见误区` 不得空壳；
- 正文**不逐句引课件**，出处写在 `## 参考`；
- **不得出现审计语言**（“课件未展开/未覆盖”）；
- 至少 2 道自测题；相关概念链接目标必须真实存在。

---

## 6. 逐页知识点账本模板

账本是阶段 1 的防漏证据层，不是最终产物。每页一条记录：

```yaml
- source: lectures/L02.pdf
  page: 8
  role: mechanism
  points: [参数共享, 局部连接]
  evidence: "权重在空间位置间复用，因此参数量与输入尺寸无关"
  visual_only: false
  needs_review: false
  note: ""
```

| 字段 | 必填 | 说明 |
|---|---|---|
| `source` | ✅ | 课件相对路径 |
| `page` | ✅ | 正整数；PPT 用 slide 序号 |
| `role` | ✅ | 见下表 |
| `points` | ✅ | 该页提出/展开的知识点；`no_knowledge` 时为空数组 |
| `evidence` | ✅ | 关键原文或图示说明；无法确认时写“仅图片/公式，内容无法确认” |
| `visual_only` | 推荐 | 该页信息主要存在于图片/公式/动画中 |
| `needs_review` | 推荐 | 是否需要人工复核 |
| `note` | 可选 | 上下文、与他页的关系 |

`role` 枚举：

| `role` | 含义 |
|---|---|
| `concept` | 提出或命名概念 |
| `definition` | 给出定义、边界或术语约定 |
| `mechanism` | 解释如何工作：步骤、因果链、推导 |
| `example` | 案例、数据、实验结果、应用示例 |
| `formula` | 公式、符号、变量含义 |
| `transition` | 章节过渡、课程安排、回顾 |
| `reference` | 参考文献、延伸阅读、工具链接 |
| `no_knowledge` | 封面、目录、致谢等无知识页 |
| `needs_review` | 只有图片/公式/动画，无法确认内容 |

账本另需汇总（可在阶段 1 结束时输出）：

```yaml
ledger_summary:
  source: lectures/L02.pdf
  total_pages: 42
  roles: {concept: 6, definition: 4, mechanism: 9, example: 5, formula: 3, transition: 4, reference: 1, no_knowledge: 8, needs_review: 2}
  knowledge_points:
    - name: 参数共享
      first_seen: 7
      expanded: [7, 8, 9]
      kind: mechanism
      visual_only: false
      relations: [{type: component, target: CNN}]
```

---

## 7. 覆盖清单（coverage）模板

coverage 既写入课次笔记，也作为 `lesson-organizer` 返回结构：

```yaml
coverage:
  - source: lectures/L02.pdf
    page: 8
    knowledge_points: [参数共享, 局部连接]
    status: covered
    evidence: "权重在空间位置间复用，因此参数量与输入尺寸无关"
  - source: lectures/L02.pdf
    page: 2
    knowledge_points: []
    status: no_knowledge
    evidence: "章节封面"
  - source: lectures/L02.pdf
    page: 17
    knowledge_points: []
    status: needs_review
    evidence: "反向传播公式为图片，数值与符号无法确认"
```

校验规则（与 `course_contracts.validate_coverage` 一致）：

- `source` 必须在任务信封的 `source_files` 中；
- `page` 必须是 ≥1 的整数；
- `status` ∈ {`covered`, `no_knowledge`, `needs_review`}；
- `status != no_knowledge` 时 `knowledge_points` 不能为空。

---

## 8. 子 Agent 任务信封

由 `scripts/course-orchestrator.py` 生成，字段与 `course_contracts.validate_task` 对齐：

```yaml
task_id: lesson-L02
agent: lesson-organizer
course_id: deep-learning
lesson_id: L02
lesson_order: 2
source_files:
  - file: lectures/L02.pdf
    hash: sha256:3f1c...
    state: NEW
allowed_writes:
  - 01. 课程笔记/L02 - CNN.md
context_packet: /tmp/L02-context.json
must_return: [output_files, coverage, concept_candidates, warnings]
schema_version: course-cn-v3
```

必填字段：`task_id`、`agent`、`course_id`、`source_files`、`allowed_writes`、`must_return`、`schema_version`。

`source_files[]` 的字段名固定为 `file` / `hash` / `state`：`course-manifest.py` 输出 `file`（相对路径）、`hash`（`sha256:` 前缀）、`bytes`、`state`；`course-orchestrator.py` 直接透传，**不生成 `lesson_order`**，由主 Agent 在分发前按教学顺序补充。

写入边界：`allowed_writes` 中任何路径解析后越出课程目录 → `write_outside_course`；任何路径以 `.` 开头（隐藏文件）→ `hidden_write`。两类都会导致任务信封校验失败，主 Agent 必须修正后再分发。

---

## 9. 子 Agent 返回契约

所有返回值共用必填字段：`task_id`、`status`、`output_files`、`coverage`、`warnings`、`schema_version`。

`status` ∈ {`success`, `needs_review`, `blocked`, `failed`}；`schema_version` 必须等于 `course-cn-v3`。

### 9.1 `lesson-organizer`

```yaml
task_id: lesson-L02
status: success
output_files: [01. 课程笔记/L02 - CNN.md]
output_hash: sha256:9a2b...
coverage:
  - {source: lectures/L02.pdf, page: 8, knowledge_points: [参数共享], status: covered, evidence: "..."}
concept_candidates:
  - name: CNN
    action: create
    reason: "跨页展开，具有独立机制与后续复用价值"
    source_range: lectures/L02.pdf:3-9
  - name: 池化
    action: lesson_only
    reason: "课件仅提及一次，未展开"
    source_range: lectures/L02.pdf:10
warnings: []
schema_version: course-cn-v3
```

### 9.2 `concept-card-builder`

```yaml
task_id: concepts-L02
status: success
output_files: [50 Knowledge/AI/World Model.md]
decisions:
  - candidate: CNN
    action: create
    target: 50 Knowledge/AI/World Model.md
    concept_id: cnn
    questions: ["它解决什么问题？", "卷积如何提取局部模式？"]
    source_ranges: [lectures/L02.pdf:3-9]
    reason: "来源跨多个页面，具有独立机制和后续复用价值"
coverage: []
warnings: []
schema_version: course-cn-v3
```

### 9.3 `course-index-manager`

```yaml
task_id: index-update-20260922
status: success
output_files: [00. 课程索引.md, .course-progress.md, .course-progress.json]
updated: {lessons_added: 1, cards_added: 2, links_deduped: 3}
stats: {lessons: 3, concepts: 5, covered_points: 46, needs_review: 1}
coverage: []
warnings: []
schema_version: course-cn-v3
```

### 9.4 `course-reviewer`

```yaml
task_id: review-L02
status: pass            # pass | needs_fix | blocked
output_files: [50 Knowledge/AI/World Model.md]   # 实际修复写入的文件；未修复时为 []
coverage: []                          # 审查任务不产出覆盖清单，固定空数组
checks:
  frontmatter: pass
  coverage: pass
  source_evidence: pass
  completeness: pass
  non_repetition: pass
  links: pass
  protection: pass
issues:
  - severity: P1
    file: 50 Knowledge/AI/World Model.md
    section: 工作机制或推导
    problem: "账本记录 p.9 的池化步骤，正文没有解释"
    source_range: lectures/L02.pdf:9
repair_files: [50 Knowledge/AI/World Model.md]
coverage: []
warnings: []
schema_version: course-cn-v3
```

---

## 10. 进度文件格式

### 10.1 `.course-progress.md`（人类可读，索引 Agent 维护）

```markdown
# 课程进度

## 源文件

| 文件 | sha256 | 状态 | 首次处理 | 最近处理 |
|---|---|---|---|---|
| lectures/L01.pdf | sha256:1a2b... | DONE | 2026-09-01 | 2026-09-01 |
| lectures/L02.pdf | sha256:3f1c... | DONE | 2026-09-08 | 2026-09-08 |

## 课次

| lesson_id | 文件 | lesson_order | status | vf_status |
|---|---|---|---|---|
| L01 | 01. 课程笔记/L01 - 神经网络基础.md | 1 | reviewed | pristine |
| L02 | 01. 课程笔记/L02 - CNN.md | 2 | reviewed | pristine |

## 事件日志

- [阶段 0] 扫描：NEW 1 / UPDATED 0 / DONE 1 / REMOVED 0
- [阶段 2] L02 - CNN.md → filled
- [阶段 5] 索引更新完成，覆盖点数 46
```

### 10.2 `.course-progress.json`（机器状态，`course-manifest.py` 读取）

```json
{
  "schema_version": "course-cn-v3",
  "sources": [
    {"file": "lectures/L01.pdf", "hash": "sha256:1a2b...", "state": "DONE", "processed_at": "2026-09-01"},
    {"file": "lectures/L02.pdf", "hash": "sha256:3f1c...", "state": "DONE", "processed_at": "2026-09-08"}
  ],
  "lessons": [{"lesson_id": "L01", "file": "01. 课程笔记/L01 - 神经网络基础.md", "lesson_order": 1, "status": "reviewed", "vf_status": "pristine"}],
  "concepts": [{"concept_id": "world-model", "canonical_name": "World Model", "file": "50 Knowledge/AI/World Model.md", "status": "reviewed", "vf_status": "pristine"}]
}
```

`scan()` 用 `sources[].file` + `sources[].hash` 判定 `NEW/UPDATED/DONE/REMOVED`：字段名与层级必须保持 `sources` 数组、`file` 用相对路径、`hash` 带 `sha256:` 前缀。文件损坏时按“全部 NEW”容错处理。

---

## 11. 关系标注格式

- 正文内联：`[[目标卡片或课次]] —(关系类型)→ 一句理由`
- 索引/网络中每行一条，禁止重复行；
- 关系类型仅限：`prerequisite`、`component`、`contrast`、`extension`、`application`、`sequence`；
- 理由必须能回溯到课件；仅因标题共享词语而连边视为无效。

`source_range` 格式（供 `scripts/context-extractor.py` 解析）：

```
source_range: {文件名}:{页码段}, {页码段}, ...
```

| 形式 | 示例 |
|---|---|
| 单页 | `L02.pdf:102` |
| 连续范围 | `L02.pdf:12-15` |
| 多段混合 | `L02.pdf:12-15, 45-48, 102` |
| 多文件 | `L02.pdf:12-15, overview.md` |
| 无页码的非 PDF | `overview.md` |

被解析的文件扩展名限定为 `.pdf` / `.md` / `.txt`；PPT/DOCX/HTML 没有固定页码，由 Agent 读取全文并在正文中记录 slide/段落范围，不要伪造页码。

### 11.1 临时抽取清单（供 `context-extractor.py`）

课程版不生成路线图。需要精确抽取原文时，主 Agent 由阶段 1 账本生成一个临时清单（放 `/tmp`，不写入课程目录），格式与脚本解析规则一致——知识点标题加粗，`source_range` 用反引号包裹，位于**同一行**：

```markdown
# L02 抽取清单

## 01. CNN

### 核心机制

**卷积核与局部连接**  `source_range: lectures/L02.pdf:3-6`
**参数共享**  `source_range: lectures/L02.pdf:7-9, 21-22`
**池化**  `source_range: lectures/L02.pdf:10`
```

`source_range` 也可写在标题的下一行（允许中间空行，脚本向前最多搜索 3 行）：

```markdown
**参数共享**
`source_range: lectures/L02.pdf:7-9`
```

抽取命令：

```bash
python3 scripts/context-extractor.py <课程目录> /tmp/L02-extract.md -o /tmp/L02-context.json --buffer 1
```

---

## 12. 写入协议与自检

任何文件写入都必须遵循：

1. 写 `{目标文件名}.tmp`，内容完整（含 frontmatter）；
2. 暂存期间将 frontmatter `status` 置为 `filling`；
3. 校验：文件非空；frontmatter 以 `---` 开始并以 `---` 结束；必要的结构标题齐全；卡片八个段落齐全；
4. `rename` 覆盖目标文件；
5. 将 `status` 更新为 `filled`（审查后为 `reviewed`）；
6. 追加进度事件，汇报实际文件 hash。

失败回滚：第 4 或第 5 步失败时，清理 `.tmp`，保持原文件不变，任务标记 `failed`，由主 Agent 决定是否重试（同一任务最多 2 次，超限记 `needs_review`）。

写入自检清单：

- [ ] 只写了 `allowed_writes` 中的路径；
- [ ] 没有覆盖 `user_modified` / `locked` 文件正文；
- [ ] 没有残留 `.tmp`；
- [ ] `status` 与磁盘实际状态一致；
- [ ] 统计数字来自实际扫描，不是模型自报；
- [ ] 关键 frontmatter 字段均为单行标量。

---

## 13. 禁止写法清单

| 禁止 | 反例 | 正确做法 |
|---|---|---|
| **逐句挂页码** | `p.27 的标题即定义："Classification + Localization"；p.28 …` | 章节标题标一次「课件 p.27–30」 |
| **审计式声明** | “课件未展开”“课件未覆盖”“本课程未提供”“不能作为数据来源” | 如实简述；确需回看写「建议对照课件 p.17」 |
| **复制课件符号** | 正文出现 `●` `○` `■` `▪` | 用 Markdown 列表 `-` |
| **伪标题** | `**2.1 世界模型（p.7）**` | `### 2.1 World Model（课件 p.7–8）` |
| **课件页序当叙述顺序** | 按 p.2 / p.3 / p.10 逐页编号 | 按「先懂什么才能懂什么」组织 |
| 用一段总述代替多个知识点 | “本节讲了 A、B、C，都很重要” | 逐个给出定义、机制、例子、边界 |
| 依据标题或记忆补写 | 只看到标题就写满一页 | 如实简述，或标 `needs_review` |
| 编造案例/实验/引用 | 自造一个“例如某公司…” | 用课件里的例子；没有就换一种说明方式 |
| 把课外知识伪装成课件结论 | 把外部查到的公式说成“课件给出” | 自然说明来源：「值得一提的背景是…」 |
| **卡片依赖课件** | 卡片里写「见 p.7 的图」 | 卡片自足；确需引用时用 `![[xxx.pdf#page=7]]` 嵌入 |
| **为“网络完整”穷举连边** | 产出上百条纯文本关系边 | 只在读者会想跳转时连线 |
| 文件名排序当作课次顺序 | `sorted(glob("*.md"))` | 用 `lesson_order` 数值排序 |
| 用摘要/笔记替代原文 | 从旧笔记反推内容 | 回到课件原文或上下文包 |
| 覆盖用户内容 | 直接重写 `user_modified` 文件 | 保留正文，仅返回建议 |

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
| 课程目录 | 用户指定，`course_id` 取目录名 | `深度学习/` |
| 课次编号 | `L` + 两位序号，由课件在课程中的教学顺序决定 | `L01`、`L02`、`L12` |
| 课次笔记文件 | `01. 课程笔记/{lesson_id} - {主题}.md` | `01. 课程笔记/L02 - CNN.md` |
| 知识卡片文件 | `02. 知识卡片/{canonical_name}.md` | `02. 知识卡片/自注意力.md` |
| 课程索引 | 固定 `00. 课程索引.md`（课程根目录唯一） | `00. 课程索引.md` |
| 临时文件 | `{目标文件名}.tmp`，rename 前不得视为产物 | `L02 - CNN.md.tmp` |
| `lesson_order` | 正整数，连续递增，用于排序；**不使用文件名排序** | `1`、`2`、`3` |
| `concept_id` | 稳定 ID，来自标准名规范化，见下 | `cnn`、`自注意力` |

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
course_id: deep-learning
lesson_id: L02
lesson_order: 2
source_file: lectures/L02.pdf
source_hash: sha256:3f1c...
source_range: lectures/L02.pdf:1-42
status: reviewed
vf: true
vf_version: course-cn-v1
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
| `vf_version` | ✅ | `course-cn-v1` | 生成器版本 |
| `vf_status` | ✅ | 三态 | 见 2.4 |

### 2.2 知识卡片（`type: concept`）

```yaml
---
type: concept
course_id: deep-learning
concept_id: cnn
canonical_name: CNN
aliases: [卷积神经网络, ConvNet]
source_lessons: [L02, L03]
source_files: [lectures/L02.pdf]
source_range: lectures/L02.pdf:12-25
status: reviewed
vf: true
vf_version: course-cn-v1
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

```markdown
---
type: index
course_id: deep-learning
status: reviewed
vf: true
vf_version: course-cn-v1
vf_status: pristine
---

# 深度学习

## 课程目标

（一句话说明这门课要解决什么；来源为用户说明或课件首页，无来源时写“课件未说明”。）

## 课程目录

| 顺序 | 课次 | 主题 | 来源课件 | 状态 |
|---|---|---|---|---|
| 1 | [[L01 - 神经网络基础]] | 神经网络基础 | lectures/L01.pdf | reviewed |
| 2 | [[L02 - CNN]] | CNN | lectures/L02.pdf | reviewed |

## 全课程知识网络

- [[CNN]] —(prerequisite)→ [[神经网络基础]]
- [[池化]] —(component)→ [[CNN]]
- [[CNN]] —(contrast)→ [[RNN]]

## 知识卡片索引

| 卡片 | 标准名 | 别名 | 出现课次 |
|---|---|---|---|
| [[CNN]] | CNN | 卷积神经网络, ConvNet | L02, L03 |
| [[RNN]] | RNN | 循环神经网络 | L05 |

## 进度概览

- 课件：3（DONE 2 / NEW 1）
- 课次笔记：2
- 知识卡片：5
- 覆盖点数：46
- 待复核：1

## 用户自定义

（保留用户在此追加的内容，索引 Agent 只做最小增量追加，不重排、不删除。）
```

---

## 4. 课次笔记模板

```markdown
---
type: lesson
course_id: deep-learning
lesson_id: L02
lesson_order: 2
source_file: lectures/L02.pdf
source_hash: sha256:3f1c...
source_range: lectures/L02.pdf:1-42
status: reviewed
vf: true
vf_version: course-cn-v1
vf_status: pristine
---

# L02 - CNN

## 本节学习目标

- （来自课件明确说明的目标；课件未说明时，按实际内容归纳并标注“由内容归纳”）

## 课件主线

> 按课件顺序记录主线，一段话说明本节的推进逻辑（问题 → 概念 → 机制 → 案例 → 边界）。

### 1. 问题与动机

### 2. 核心概念

### 3. 机制、步骤或公式

### 4. 例子与系统案例

### 5. 限制、边界与后续扩展

## 知识点覆盖清单

- [x] 卷积核与局部连接 — lectures/L02.pdf:3-6
- [x] 参数共享 — lectures/L02.pdf:7-9
- [ ] 池化 — lectures/L02.pdf:10（课件仅提及，未展开）
- ⚠️ 反向传播推导 — lectures/L02.pdf:17（公式为图片，needs_review）

## 本节知识网络

- [[CNN]] —(prerequisite)→ [[神经网络基础]]
- [[池化]] —(component)→ [[CNN]]

## 本节知识卡片

- [[CNN]]（create）
- [[池化]]（lesson_only，未单独建卡）

## 来源与复核项

| 来源 | 覆盖范围 | 状态 |
|---|---|---|
| lectures/L02.pdf | 1-42 | covered 38 / no_knowledge 2 / needs_review 2 |

复核项：p.17 公式图、p.23 动画中的状态转移过程。
```

**逐节写作要求**：每一节必须出现问题、定义或假设、机制、课件证据或例子、与前后的关系这五类信息中的相关部分；材料未覆盖的部分直接写明“课件未展开”。

---

## 5. 知识卡片模板

```markdown
---
type: concept
course_id: deep-learning
concept_id: cnn
canonical_name: CNN
aliases: [卷积神经网络, ConvNet]
source_lessons: [L02]
source_files: [lectures/L02.pdf]
source_range: lectures/L02.pdf:3-9
status: reviewed
vf: true
vf_version: course-cn-v1
vf_status: pristine
---

# CNN

## 一句话定义

（对象 + 边界：它是什么、用于什么、与最相近概念的关键差别。）

## 核心知识点

### 背景与要解决的问题

### 精确定义与边界

### 工作机制或推导

（按步骤写清因果链；有公式就说明变量含义与直觉。）

### 例子、公式或实现直觉

### 应用条件与失败模式

### 与其他知识点的关系

（只写有课件依据的关系，格式 `[[目标]] —(关系类型)→ 理由`。）

## 相关案例

（背景 / 过程 / 结果 / 启示。课件没有案例时写“课件未提供案例”。）

## 原文引用

> {课件中的实际原文摘录，保留原语言，不得改写}

> — 来源：{文件}，{页码/slide 范围}

## 在课程中的出现位置

| 课次 | 页码/slide | 该处讲了什么 |
|---|---|---|
| L02 | 3-9 | 定义与卷积操作 |
| L03 | 1-4 | 与池化的组合使用 |

## 核心思考

1. （检验理解的迁移问题）
2. （检验边界与失效条件的问题）
```

**硬性要求**

- 六段式（`一句话定义`、`核心知识点` 六个子节、`相关案例`、`原文引用`、`在课程中的出现位置`、`核心思考`）一个都不能省；材料未覆盖的子节写“课件未覆盖”，不得用外部内容填充。
- `原文引用` 必须是实际摘录；只写来源元数据、没有引文视为无效。
- `核心思考` 至少 2 题，不得出现“请总结本文”类问题。
- 不得机械复制课次笔记段落；卡片应把散落在多页的解释组织成独立学习路径。

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
schema_version: course-cn-v2
```

必填字段：`task_id`、`agent`、`course_id`、`source_files`、`allowed_writes`、`must_return`、`schema_version`。

`source_files[]` 的字段名固定为 `file` / `hash` / `state`：`course-manifest.py` 输出 `file`（相对路径）、`hash`（`sha256:` 前缀）、`bytes`、`state`；`course-orchestrator.py` 直接透传，**不生成 `lesson_order`**，由主 Agent 在分发前按教学顺序补充。

写入边界：`allowed_writes` 中任何路径解析后越出课程目录 → `write_outside_course`；任何路径以 `.` 开头（隐藏文件）→ `hidden_write`。两类都会导致任务信封校验失败，主 Agent 必须修正后再分发。

---

## 9. 子 Agent 返回契约

所有返回值共用必填字段：`task_id`、`status`、`output_files`、`coverage`、`warnings`、`schema_version`。

`status` ∈ {`success`, `needs_review`, `blocked`, `failed`}；`schema_version` 必须等于 `course-cn-v2`。

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
schema_version: course-cn-v2
```

### 9.2 `concept-card-builder`

```yaml
task_id: concepts-L02
status: success
output_files: [02. 知识卡片/CNN.md]
decisions:
  - candidate: CNN
    action: create
    target: 02. 知识卡片/CNN.md
    concept_id: cnn
    questions: ["它解决什么问题？", "卷积如何提取局部模式？"]
    source_ranges: [lectures/L02.pdf:3-9]
    reason: "来源跨多个页面，具有独立机制和后续复用价值"
coverage: []
warnings: []
schema_version: course-cn-v2
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
schema_version: course-cn-v2
```

### 9.4 `course-reviewer`

```yaml
task_id: review-L02
status: pass            # pass | needs_fix | blocked
output_files: [02. 知识卡片/CNN.md]   # 实际修复写入的文件；未修复时为 []
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
    file: 02. 知识卡片/CNN.md
    section: 工作机制或推导
    problem: "账本记录 p.9 的池化步骤，正文没有解释"
    source_range: lectures/L02.pdf:9
repair_files: [02. 知识卡片/CNN.md]
coverage: []
warnings: []
schema_version: course-cn-v2
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
  "schema_version": "course-cn-v2",
  "sources": [
    {"file": "lectures/L01.pdf", "hash": "sha256:1a2b...", "state": "DONE", "processed_at": "2026-09-01"},
    {"file": "lectures/L02.pdf", "hash": "sha256:3f1c...", "state": "DONE", "processed_at": "2026-09-08"}
  ],
  "lessons": [{"lesson_id": "L01", "file": "01. 课程笔记/L01 - 神经网络基础.md", "lesson_order": 1, "status": "reviewed", "vf_status": "pristine"}],
  "concepts": [{"concept_id": "cnn", "canonical_name": "CNN", "file": "02. 知识卡片/CNN.md", "status": "reviewed", "vf_status": "pristine"}]
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
3. 校验：文件非空；frontmatter 以 `---` 开始并以 `---` 结束；必要的结构标题齐全；卡片含六段式；
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
| 用一段总述代替多个知识点 | “本节讲了 A、B、C，都很重要” | 每个知识点单列，给出定义、机制、证据 |
| 依据标题或记忆补写 | 只看到标题就写满一页 | 写“课件未展开” |
| 编造案例/实验/引用 | 自造一个“例如某公司…” | 写“课件未提供案例” |
| 伪引用 | 只写“— 来源：L02.pdf p.9” 无引文 | 给出实际摘录 + 来源 |
| 同一内容多文件重复 | 课次笔记与卡片整段复制 | 卡片独立组织，课次保留顺序 |
| 固定字数凑长度 | 为达字数重复同义句 | 深度与来源成比例 |
| 文件名排序当作课次顺序 | `sorted(glob("*.md"))` | 用 `lesson_order` 数值排序 |
| 用摘要/笔记替代原文 | 从路线图或旧笔记反推内容 | 回到课件原文或上下文包 |
| 未标注的补充知识 | 把常识写成课件结论 | 标注“（补充解释）” |
| 覆盖用户内容 | 直接重写 `user_modified` 文件 | 保留正文，仅返回建议 |

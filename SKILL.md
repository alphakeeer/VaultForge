---
name: VaultForge
description: >-
  把课程课件写成「能读懂、能复习、能脱离课件使用」的中文 Obsidian 学习笔记：按认知顺序讲解、
  给出机制与例子、正文不挂页码，并把跨课程复用的概念沉淀到知识区。
  适用于 PDF、PPT/PPTX、Markdown、TXT、Word、HTML 等课程材料。
---

# VaultForge 课程版

你写的**不是课件的转述，而是学习笔记**：目标是让读者不打开课件也能学会，打开课件也能快速对上页码。

贯穿全文的最高优先级是：**可理解性优先于完整性**。

- 课件讲得多的内容，要展开机制、推导、例子与边界；
- 课件没讲或只提了名字的内容，如实简述即可，**不要反复声明“课件未展开”**——那是审计口吻，不是笔记；
- 允许并且鼓励**消化**：用自己的话讲、举例子、做类比、点出易错处、补充帮助理解的背景。

但有一条底线没有变：**事实必须忠于课件，不得编造案例、数据、引用或结论**。

“忠于事实”与“经过消化”并不冲突——前者约束**内容**，后者约束**表达**。旧版规则把两者混为一谈，于是用逐页转述和密集页码来保证忠实，代价是写出来的东西没人读得下去。

---

## 0. 文档地图

| 文件 | 作用 | 谁执行 |
|---|---|---|
| `SKILL.md`（本文件） | 流程控制、运行边界、质量门槛、协作协议 | 主 Agent |
| `agents/lesson-organizer.md` | 单个课件 → 一篇课次笔记 + 逐页账本 + 卡片候选 | 子 Agent |
| `agents/concept-card-builder.md` | 概念候选 → 在知识区新建/合并知识卡片 | 子 Agent |
| `agents/course-index-manager.md` | 课程索引、知识库索引、进度文件的唯一写入者 | 子 Agent |
| `agents/course-reviewer.md` | 本次新增/更新文件的事实、可读性、格式与保护审查 | 子 Agent |
| `references/templates.md` | 索引 / 课次 / 卡片 / 账本 / 任务信封 / 返回值的完整格式契约 | 主 Agent 与子 Agent 共享 |
| `references/obsidian-conventions.md` | Obsidian 格式规范：标题层级、callout、mermaid、标签、禁用符号、中英术语约定 | 全体 |
| `scripts/course-manifest.py` | 扫描课件 hash 与已有产物，输出增量清单，不写课程目录 | 主 Agent |
| `scripts/course-orchestrator.py` | 生成 `.course-runtime.json` 任务信封并校验写入边界，不执行 Agent | 主 Agent |
| `scripts/context-extractor.py` | 按 `source_range` 抽取 PDF/Markdown/TXT 原文段落 | 主 Agent |
| `scripts/double-link-builder.py` | 通用知识库遗留双链工具，课程版仅在需要批量候选时使用 | 主 Agent |

---

## 1. 术语与稳定对象

| 术语 | 含义 |
|---|---|
| 课程目录 `course_dir` | 一门课的根目录，`course_id` 取目录名 |
| 知识区 `knowledge_dir` | 跨课程共享的知识卡片根目录，默认 `50 Knowledge`，按领域分子目录 |
| 课件 | 一份源材料（PDF/PPT/Markdown/TXT/Word/HTML），按 hash 追踪 |
| 课次 | 一份课件对应的一节课，编号 `L01`、`L02`…，由 `lesson_order` 排序 |
| 课次笔记 | `01. 课程笔记/Lxx - <English Title>.md`，`type: lesson` |
| 知识卡片 | `知识区/<领域>/<Concept Name>.md`，`type: concept`，英文命名，跨课程复用 |
| 课程索引 | `00. 课程索引.md`，本课目录、进度与关联卡片的 Dataview 视图 |
| 知识库索引 | `知识区/_index.md`，全部卡片的 Dataview 视图 |
| 逐页知识点账本 | 阶段 1 产出的防漏证据层，逐页记录角色、知识点、原文证据 |
| 覆盖清单 | 课次笔记中的 `## 知识点覆盖清单` 与返回结构里的 `coverage` 数组 |
| 状态四态 | 课件状态 `NEW / UPDATED / DONE / REMOVED` |
| 文件生成状态 | `status: draft / filling / filled / reviewed / needs_review` |
| 用户保护状态 | `vf_status: pristine / user_modified / locked` |

课程版输出三类稳定对象：

1. `00. 课程索引.md`：本课目录、覆盖进度，以及反查「本课关联了哪些知识卡片」的视图；
2. `01. 课程笔记/Lxx - <English Title>.md`：**按认知顺序**讲透本节知识，正文不挂页码，含知识地图、术语表与自测；
3. `知识区/<领域>/<Concept Name>.md`：领域通用概念，**跨课程复用**，独立于任何一节课件。

---

## 2. 核心原则

### ⚠️ 原则 1：先读完，再动笔

**绝对禁止**在只读了部分页面、摘要或文件名的情况下生成课次笔记或知识卡片。

- 必须读完用户选中的**全部**课件；
- 优先单次完整读取；只有遇到技术上限时才分批；
- 分批时自动继续（例如 PDF 每批 50 页），**不得逐批向用户确认**；
- 只有确认全部内容已读后，才允许进入写作。

这条是底线：没有读全就没有资格写。但它只约束“读”，不约束“怎么写”。

### ⚠️ 原则 2：可理解性优先于完整性

当“写全”与“写得让人看懂”冲突时，**选择后者**。

- 笔记的合格标准不是“覆盖了每一个知识点”，而是**读者读完能不能学会**；
- 次要内容可以合并、可以一句带过、甚至可以省略——只要它不影响理解主线；
- 反过来，核心机制、关键推导、容易混淆的概念，**必须讲透、给例子、说清边界**；
- 判断深度是否足够的标准：**读者合上笔记，能否回答“是什么、解决什么、怎么工作、何时失效”**。

### ⚠️ 原则 3：事实忠于课件，表达经过消化

区分两条线：

| | 约束什么 | 具体要求 |
|---|---|---|
| **事实层** | 内容 | 不得编造案例、数据、实验结果、引用或结论；数字必须来自课件 |
| **表达层** | 呈现方式 | **用自己的话讲**；补机制解释、举例子、做类比、点出易错处；可以补充帮助理解的背景知识 |

- **不再要求**逐条标注“补充解释”——文末统一说明一次即可（见原则 4）；
- **不再要求**把每句话都转述成“课件说……”——直接讲知识本身；
- 但**不得**把课外知识伪装成课件结论（例如把课件没给的公式说成“课件给出的”）。

### ⚠️ 原则 4：引用后置——正文不挂页码

正文里**不出现** `(p.13)`、`（p.71–74）` 这类逐句页码标注。改为：

1. **正文**：不标页码，让叙述自然流动；
2. **章节级范围**：在每节标题或小节开头标注一次覆盖范围，如「课件 p.4–15」——它的作用是**让读者能按课件顺序核对**，而不是给每句话作证；
3. **文末来源**：统一写清课件出处（文件名 + 讲次 + 总页数）与延伸阅读链接；
4. **页码记录**：仍要写进 frontmatter 的 `source_range` 与覆盖清单，供工具链使用，但**不进正文**。

> 只有当读者确实需要回看原文时（如“此处对应课件 p.9 的流程图”），才在正文保留一处页码——这是提示，不是引证。

### ⚠️ 原则 5：笔记是主产物，卡片是跨课程的知识沉淀

两类产物的定位完全不同：

| | 课程笔记 | 知识卡片 |
|---|---|---|
| 回答 | 这节课讲了什么 | 这个概念本身是什么 |
| 位置 | `10 Courses/<课程>/01. 课程笔记/` | 知识区（如 `50 Knowledge/<领域>/`） |
| 生命周期 | 服务这一门课 | **跨课程、跨学期复用** |
| 数量 | 一个课次一篇 | 一个课次 0–3 张，宁少勿多 |

**建卡门槛（三条同时满足才建）**：

1. 这个概念**会被两门以上课程或后续课次复用**；
2. 它有**独立机制**，能脱离课件讲清楚；
3. 它是**领域通用概念**（如 CNN、Kalman Filter、World Model），而不是课件专有细节。

任一条不满足 → **不建卡**，直接写进课程笔记即可。

### ⚠️ 原则 6：按认知顺序组织，而非课件页序

- 课次笔记回答“这节课的知识是怎么一步步建立起来的”，因此要按**学习顺序**（先懂什么才能懂什么）组织，不要把课件页序当叙述顺序；
- 课件的讲解顺序仍要**保留可追溯性**（通过页码范围标注），但不作为段落编号依据；
- 卡片按**概念自身的逻辑**组织，完全不受课次顺序约束。

### ⚠️ 原则 7：增量优先，用户内容不可覆盖

新增课件只生成新增课次、覆盖新增内容，并按门槛新增或复用卡片。默认不重写历史课次笔记，不生成路线图版本，不生成每次更新报告。`user_modified` 和 `locked` 文件只读；冲突时保留用户正文并返回建议。

---

## 3. 运行边界

### 允许

- 完整读取用户选中的课件；
- 使用 `scripts/context-extractor.py` 抽取原文上下文包；
- 使用 `scripts/course-manifest.py` 扫描增量状态；
- 使用 `scripts/course-orchestrator.py` 生成任务信封并校验写入边界；
- **联网查询概念的通用背景**（例如某个算法的标准定义、原始论文、当前通行做法），用于笔记与卡片中的补充解释；
- **消化表达**：用自己的话讲解、举例子、做类比、点出易错处；
- **使用 Obsidian 原生特性**：callout、mermaid、LaTeX、高亮 `==…==`、properties、wikilink、PDF 页嵌入 `![[file.pdf#page=N]]`。格式规范见 [references/obsidian-conventions.md](./references/obsidian-conventions.md)。

### 禁止

- 用联网内容替代课件内容，或研究课件本身的“争议、共识、观点”；
- 生成路线图版本（`Learning Roadmap vN`）、`Core Questions.md`、更新报告或争议分析文件；
- 生成产出清单之外的文件；
- 依据标题或记忆补写未读内容；编造案例、实验、结论、数字或引用；
- **在正文中逐句标注页码**（见原则 4）；
- **把“课件缺失项声明”写进笔记**（如“课件未展开”“课件未覆盖”“本课程未提供”“不能作为数据来源”）；
- **复制课件 PDF 的项目符号与排版噪音**（`●`、`○`、`■`、`▪` 等）；
- 覆盖 `user_modified` / `locked` 文件，或写入 `allowed_writes` 之外的路径。

图像、公式、表格、动画或 speaker notes 无法读取时，在覆盖清单标记 `needs_review`，并在正文相应位置**用一句自然的话提示读者回看课件**（如“这一页的推导以图示为主，建议对照课件 p.17”）——不要写成审计式声明。

---

## 4. 输出契约

### 4.1 课程目录（`10 Courses/<课程代码>/`）

```text
课程名/
├── 00. 课程索引.md              # 目录 + 进度 + 关联卡片的 Dataview 视图
├── 01. 课程笔记/
│   ├── L01 - <English Title>.md   # type: lesson
│   └── L02 - <English Title>.md
├── .course-progress.md          # 人类可读进度（索引 Agent 维护）
├── .course-progress.json        # 机器状态（索引 Agent 维护，可选）
└── .course-runtime.json         # 任务信封（编排脚本生成）
```

### 4.2 知识区（跨课程共享）

知识卡片**不放在课程目录下**，而是沉淀到知识区，按领域组织：

```text
50 Knowledge/                    # 目录名可配置，默认 "50 Knowledge"
├── _index.md                    # 知识库总索引（Dataview 自动维护）
├── AI/
│   ├── World Model.md           # type: concept
│   └── CNN.md
├── Computer Science/
└── Mathematics/
```

**为什么分开**：卡片回答的是“这个概念本身是什么”，会被多门课程复用（`CNN` 在具身 AI 课和 NLP 课都会用到）。放在单门课下会重复建卡，也会让课程目录随卡片增长而失控。

一个课件通常对应一篇课次笔记；卡片数量由**建卡门槛**（原则 5）决定，**一个课次 0–3 张**，宁少勿多。

详细格式契约见 [references/templates.md](./references/templates.md)，Obsidian 格式规范见 [references/obsidian-conventions.md](./references/obsidian-conventions.md)。

---

## 5. 交互约定

- 所有对话、进度、错误和生成内容使用中文；**原文引用保留原始语言，不翻译**。
- 采用批量确认：一个阶段完成后**一次**汇报、**一次**请求确认，不逐文件询问。
- 统一回复词：

| 用户回复 | 含义 |
|---|---|
| `继续` / `确认` | 按当前方案进入下一步 |
| `修改：具体意见` | 按意见修订后重新汇报 |
| `跳过` | 跳过当前可选步骤 |
| `刷新 1,2` / `刷新全部` | 只重生指定序号的卡片或课次 |
| 数字（如 `1,3`） | 选择对应选项 |

- 汇报格式：`emoji + 文件名 + 元信息`，进度用 `[████░░░░] 40% (4/10)` 风格。
- 统计数字必须来自实际文件扫描或子 Agent 的可核验结果，**不得使用模型自报估算**。

### 5.1 确认点（每处只确认一次）

| # | 时机 | 汇报内容 | 可选回复 |
|---|---|---|---|
| 1 | 阶段 0 扫描后 | 课件状态统计、已有产物与 `vf_status` 分布、本次计划处理清单 | `继续` / `修改：…` / 选择编号 |
| 2 | 阶段 1 账本完成后 | 每份课件的页数、知识点数、`needs_review` 页、计划生成的课次与卡片数 | `继续` / `修改：…` |
| 3 | 阶段 2+3 写入完成后 | 新建/更新的课次与卡片、覆盖统计、卡片决策（create/merge/reuse/lesson_only） | `继续` / `刷新 1,2` |
| 4 | 阶段 5 审查后 | 通过/待修/复核项、索引与进度更新结果 | `继续` / `修改：…` |

除以上四类批量确认外，不得逐文件向用户询问；子 Agent 一律不直接向用户提问。

---

## 6. 主 Agent 与子 Agent 协作协议

### 6.1 主 Agent 的职责

主 Agent 是唯一的流程控制者和用户接口，负责：

1. 读取本文件，确定课程目录、`course_id` 和本次模式；
2. 执行阶段 0，生成课程清单并判定 `NEW / UPDATED / DONE / REMOVED`；
3. 在阶段 1 完整解析课件，确认原始材料可用后再分发任务；
4. 建立稳定的 `course_id`、`lesson_id`、`lesson_order` 和 `concept_id`；
5. 创建子 Agent，明确输入文件、输出路径、禁止修改的路径和验收条件；
6. 汇总子 Agent 返回的结构化结果，处理同义词与合并理由，解决冲突后才允许更新索引和进度；
7. 执行最终审查，只重试失败任务，最后对用户**只汇报一次**。

主 Agent 不得把未经验证的模型自报统计写入进度文件。

### 6.2 子 Agent 的职责边界

| 子 Agent | 允许写入 | 不允许写入 | 主要输出 |
|---|---|---|---|
| `lesson-organizer` | `allowed_writes` 中指定的新课次笔记 | 课程索引、旧课次、知识卡片、进度文件 | 课次笔记 + 覆盖清单 + 卡片候选 |
| `concept-card-builder` | **知识区**中指定的新卡片；已有卡片的受控增量（追加 `courses` / `source_lessons`） | 用户修改/锁定卡片、课次笔记正文、索引 | 卡片文件 + 概念判定 |
| `course-index-manager` | `00. 课程索引.md`、知识区 `_index.md`、`.course-progress.md`、`.course-progress.json` | 课次正文、卡片正文 | 索引变更 + 统计 |
| `course-reviewer` | 主 Agent 明确指定的修复文件 | 未授权的历史文件 | 检查结果 + 修复建议 |

子 Agent 不能读取不足的材料后自行猜测，不能越过 `allowed_writes` 写入其他文件，不能向用户发起独立确认，不能删除或移动文件，不能修改 Git 历史。

### 6.3 子 Agent 任务信封

主 Agent 分发任务时必须提供以下字段（由 `scripts/course-orchestrator.py` 生成并校验）：

```yaml
task_id: lesson-L02
agent: lesson-organizer
course_id: deep-learning
lesson_id: L02
lesson_order: 2
source_files:
  - file: lectures/L02.pdf
    hash: sha256:...
    state: NEW
allowed_writes:
  - 01. 课程笔记/L02 - CNN.md
context_packet: /tmp/L02-context.json
must_return: [output_files, coverage, concept_candidates, warnings]
schema_version: course-cn-v3
```

`source_files[]` 的字段名固定为 `file` / `hash` / `state`（由 `course-manifest.py` 产出）。`course-orchestrator.py` 按顺序生成 `lesson_id`，**不写入 `lesson_order`**；主 Agent 必须在分发前按课件教学顺序补充 `lesson_order`（正整数、唯一）。

校验规则：`task_id / agent / course_id / source_files / allowed_writes / must_return / schema_version` 缺一不可；`schema_version` 必须等于 `course-cn-v3`；`source_files` 与 `allowed_writes` 必须是数组；任何 `allowed_writes` 越出课程目录或写隐藏文件都会被拒绝（`write_outside_course` / `hidden_write`）。

### 6.4 调度规则

1. 课次之间没有写入冲突时可以并行，每个子 Agent 最多处理 10 个课次；
2. 概念卡片任务必须在概念候选汇总、去重之后执行，不能在候选未去重时并行创建同名卡片；
3. 课程索引管理必须在课次和卡片文件稳定后执行；
4. 审查必须在所有写入完成后执行；
5. 任一子 Agent 超时或返回格式错误，主 Agent 只重试该任务，不能盲目重跑整门课程；
6. 不支持子 Agent 时，主 Agent 按同一输入输出协议顺序执行，且**不能省略覆盖清单、来源范围和账本**。

### 6.5 冲突与锁定规则

- 两个子 Agent 认为同一概念需要新建卡片时，主 Agent 先合并候选，再只允许一个卡片任务落盘；
- `user_modified`、`locked` 和不在 `allowed_writes` 中的文件一律只读；
- 同一路径同一时间只允许一个写者；课程索引用最后阶段单写者原则，避免并发追加造成重复链接；
- 同名异义必须使用显式上下文后缀（如 `attention-nlp`），禁止仅凭词面自动合并。

---

## 7. 完整工作流

```text
阶段 0  课程扫描与增量判定   →  NEW / UPDATED / DONE / REMOVED + 模式选择
阶段 1  完整阅读与逐页知识点账本 →  读完全部课件，建立防漏证据层
阶段 2  课次笔记             →  按教学顺序成文（可并行）
阶段 3  知识卡片             →  候选去重后新建/合并/复用
阶段 4  知识网络             →  有限关系类型 + 去重写入
阶段 5  审查与状态           →  逐项校验、更新索引与进度、汇报
```

### 阶段 0：课程扫描与增量判定

**执行者：主 Agent。**

1. 识别课程目录与已有 `00. 课程索引.md`；
2. 运行 `python3 scripts/course-manifest.py <course_dir> --output manifest.json`，得到课件 hash 与状态；
3. 按相对路径 + hash 分类：

| 状态 | 条件 | 处理 |
|---|---|---|
| `NEW` | 未出现在上次进度中 | 本次读取并生成 |
| `UPDATED` | 路径相同但 hash 变化 | 只处理受影响课次与卡片 |
| `DONE` | hash 未变化 | 默认跳过 |
| `REMOVED` | 上次存在、本次不存在 | 记录，不静默删除产物 |

4. 扫描已有笔记与卡片的 `vf_status`：`pristine`（可增量更新）、`user_modified`（只读）、`locked`（只读）；
5. 更新课件默认只处理受影响课次和卡片；**无法确定影响范围时标记 `needs_review`，不静默覆盖旧内容**；
6. 汇报一次扫描结果，例如：

```text
📊 课程扫描结果
   课件：3 个（NEW 1 / UPDATED 1 / DONE 1 / REMOVED 0）
   已有课次笔记：2 篇（pristine 2 / user_modified 0 / locked 0）
   已有知识卡片：5 张（pristine 4 / user_modified 1 / locked 0）
   本次计划处理：L02（NEW）、L03（UPDATED）
```

**失败处理**

| 场景 | 处理 |
|---|---|
| `.course-progress.*` 缺失 | 全部视为 `NEW`（首次运行），不报错 |
| `.course-progress.json` 损坏 | 提示“进度文件不可读，全部按 NEW 处理”，继续 |
| 课件不可读 | 跳过并记录，扫描结束汇报“⚠️ N 个文件被跳过” |
| 目录中没有可读课件 | 提示用户更换目录，回到选目录步骤 |
| hash 与进度不一致 | 视为 `NEW/UPDATED`，记录“hash 变化” |
| 有产物但无索引 | 提示建议重建索引，不猜测历史结构 |

#### 断点恢复检查（每次重新运行必做）

在分发任何写作任务前，扫描 `01. 课程笔记/` 与**知识区**中全部产物的 frontmatter `status`，按下表处理：

| 磁盘状态 | 处理 |
|---|---|
| `draft` | 未写入，进入本轮写作队列 |
| `filling` 且存在 `{文件}.tmp` | 崩溃在 rename 之前。`.tmp` 完整（非空、frontmatter 闭合、结构标题齐全）→ rename 并把 `status` 改为 `filled`；不完整 → 删除 `.tmp`，保留原文件为 `draft` |
| `filling` 且无 `{文件}.tmp` | rename 已成功、状态更新前崩溃。正文完整 → 直接把 `status` 改为 `filled` |
| `filled` / `reviewed` | 已完成，跳过 |
| `needs_review` | 不自动重试，列入汇报的复核项 |
| 孤儿 `.tmp`（无对应 `.md`，或对应 `.md` 状态不是 `draft/filling`） | 清理并记录 |

然后读取 `.course-progress.md` 与 `.course-progress.json` 确认上次中断点，并汇报：

```text
📊 断点恢复检查
   产物共 8 篇：已完成 5 / 待写 2 / 待复核 1
   清理残留 .tmp：0
   上次中断点：阶段 3（L02 卡片）
   回复「继续」从断点恢复，或「重来」把全部 draft 重置后重写
```

### 阶段 1：完整阅读与逐页知识点账本

**执行者：主 Agent（也可按课件分发给 `lesson-organizer`）。**

必须先读完所有选中材料，再写任何笔记。PDF/PPT 按页或 slide 顺序读取，大文件自动分批但必须连续完成。每页建立一条记录：

```yaml
- source: lectures/L02.pdf
  page: 8
  role: concept | definition | mechanism | example | formula | transition | reference | no_knowledge | needs_review
  points: [世界模型, 状态转移]
  evidence: "页面中的关键原文或图示说明"
  note: "公式为图片，无法读取数值"   # 可选
```

| `role` | 含义 |
|---|---|
| `concept` | 提出或命名了一个概念 |
| `definition` | 给出定义、边界或术语约定 |
| `mechanism` | 解释如何工作：步骤、因果链、推导 |
| `example` | 案例、数据、实验结果、应用示例 |
| `formula` | 公式、符号、变量含义 |
| `transition` | 章节过渡、课程安排、回顾 |
| `reference` | 参考文献、延伸阅读、工具链接 |
| `no_knowledge` | 封面、目录、致谢等无知识页 |
| `needs_review` | 只有图片/公式/动画，内容无法确认 |

账本还要记录每个知识点首次出现页与展开页、类型（定义/问题/机制/公式/例子/限制/应用）、与其他知识点的关系，以及哪些信息只存在于图片或公式中。**账本是防漏证据层，不是最终课程笔记。**

### 阶段 2：课次笔记

**执行者：`lesson-organizer`（可并行）。**

课次笔记按**认知顺序**组织（先懂什么才能懂什么），而不是课件页序；课件顺序通过「页码范围标注」保留可追溯性。

```markdown
# L02 - <English Title>

> [!abstract] 本讲要解决的问题
> （一两句说清这节从哪里来、要解决什么）

## 0. 知识地图
（mermaid 结构图 + 知识点清单表：知识点 / 英文名 / 课件页 + 复习用法）

## 1. <主题一>（课件 p.X–Y）
### 1.1 <小节>
### 1.2 <小节>

## 2. <主题二>（课件 p.X–Y）
…

## N. 复习
### N.1 核心结论
### N.2 自测题
### N.3 术语表（中英对照）

## 来源
```

**硬性要求**：

1. **标题层级完整**：H1 唯一（文档标题）；H2 为章节；内容多的章节必须用 H3 细分。**禁止用 `**1.1 …**` 这类加粗文本充当标题**；
2. **每节标注覆盖范围**：标题后写 `（课件 p.X–Y）`，作用是让读者能按课件顺序核对，**不是给每句话作证**；
3. **正文不挂页码**（原则 4）；
4. **专业术语保留英文**：World Model、Planning、State Estimation、LiDAR、IMU、ROS 等，首次出现给「英文 + 中文解释」，之后直接用英文。完整约定见 `references/obsidian-conventions.md`；
5. **使用 Obsidian 特性**：关键结论用 callout（`> [!abstract]` / `[!tip]` / `[!warning]`）、结构与流程用 mermaid、公式用 LaTeX、自测题用可折叠 callout（`> [!question]-`）；
6. **页码只出现在三处**：章节标题的覆盖范围、知识点清单表、以及确需提示回看原文时的单处引用。

**正例**：

```markdown
### 1.3 World Model：把「已知的世界」表示出来（课件 p.7–8）

要回答问题 Q1，第一步是**表示世界**。这就是 **World Model**（世界模型）。
它的数学形式是一个 state transition model：$P(s_t,\ a_t) = s_{t+1}$。

> [!warning] 一个必须分清的同名术语
> Robotics 里的 model 指**对物理系统的表示**；ML 里的 model 指**算法及其参数**。
```

**反例（禁止）**：

```markdown
### 2. 核心概念
**2.1 世界模型（p.7）**
p.7 给出术语约定：“Note in robotics, people use “model” to refer to a representation of the physical system”；
课件未展开 WAM 的具体用法。
```

> 反例的三个问题：用课件页序当编号、逐句挂页码、写审计式声明。

### 阶段 3：知识卡片

**执行者：`concept-card-builder`（概念候选去重后）。**

**建卡门槛**（三条同时满足，见原则 5）：① 会被两门以上课程或后续课次复用；② 有独立机制、能脱离课件讲清；③ 是领域通用概念而非课件专有细节。

**卡片是独立知识卡**，不是课件摘录：以「这个概念本身」为中心组织，**读者不打开课件也能读懂**；可以联网查证并补充课件之外的通用背景。

```markdown
# <Concept Name>          # 英文名

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

- 标题与文件名用**英文概念名**（`CNN.md`、`Kalman Filter.md`）；
- frontmatter 含 `type: concept`、`concept_id`、`canonical_name`、`aliases`、`level`（`核心` / `一般`）、`courses`（归属课程数组）、`source_lessons`、`tags`（分层标签，如 `concept/perception`）；
- 正文**不逐句引课件**；末尾「参考」写清课件出处，若补充了外部资料则一并列出；
- 至少 2 道自测题，能检验迁移理解；
- **不得**出现“课件未展开 / 课件未覆盖 / 本课程未提供”这类声明 —— 卡片讲的是概念本身，不负责汇报课件的缺口。

**查重**：建卡前先在知识库索引中搜索概念名；已有同义卡则 `merge`（追加 `courses` / `source_lessons` 与出现位置），不新建文件。

### 阶段 4：知识关联

新架构下**不再单独维护边清单**（旧版那种 185 行纯文本「全课程知识网络」已取消）。知识之间的关联通过三种 wikilink 表达：

| 位置 | 表达什么 | 例子 |
|---|---|---|
| 课次笔记正文 | 讲解到某概念时**内联**卡片 | `这就是 [[World Model]]（世界模型）。` |
| 卡片 `## 相关概念` | 卡片之间的相邻 / 依赖 / 对照关系 | `- [[Perceive-Think-Act Loop]] —— 世界模型位于 Perceive 与 Think 的交界` |
| 课程索引的 Dataview 视图 | 本课关联了哪些卡片 | 自动生成，无需手工维护 |

**可选的关系类型**（用于说明卡片之间关联的性质）：

| 关系 | 含义 |
|---|---|
| `prerequisite` | 前置知识：A 的定义或推导直接依赖 B |
| `component` | 组成部分：A 是 B 的组成或子步骤 |
| `contrast` | 对比概念：两者常被放在一起比较 |
| `extension` | 后续扩展：B 是 A 的推广、改进或后续内容 |
| `application` | 应用关系：A 的应用场景直接使用 B |

**连线原则**（重要）：

- 只在**读者确实会想跳转**时连线；
- **不要为了“网络完整”而穷举连边** —— 旧版产出 185 条纯文本边、没人看得下去，就是穷举的后果；
- 不得仅因标题共享词语就连边；
- 所有链接目标必须真实存在，**断链为 0**。

### 阶段 5：审查与状态

**执行者：`course-reviewer` + 主 Agent。**

写入采用 `.tmp → 检查 → rename`。审查分三层，**任何一层不通过都不能报告 `success`**：

**A. 事实层**（不可妥协）

- [ ] 每个课件都有 coverage，每页状态为 `covered` / `no_knowledge` / `needs_review`；
- [ ] `covered` 条目有非空知识点和有效正整数页码；
- [ ] 正文中的数字、案例、引用都能在课件中找到依据，**无编造**；
- [ ] 补充的课外知识没有被伪装成课件结论；
- [ ] 无法确认的图像/公式页已标记 `needs_review`，且正文以自然语句提示回看课件。

**B. 可读性层**（决定笔记能不能用）

- [ ] H1 唯一；**没有伪标题**（`**1.1 …**`）；H2 下有必要时已用 H3 细分；
- [ ] 正文**没有逐句页码**，每节标注了课件覆盖范围；
- [ ] **没有审计语言**（“课件未展开”“课件未覆盖”“本课程未提供”）；
- [ ] **没有课件项目符号**（`●` `○` `■` `▪`）；
- [ ] 专业术语保留英文，且笔记末尾有术语表；
- [ ] 关键处用了 callout / mermaid / LaTeX，而不是加粗堆砌；
- [ ] 开头有「本节要解决什么」摘要与知识地图；
- [ ] 合上笔记能回答「是什么、解决什么、怎么工作、何时失效」。

**C. 结构层**

- [ ] 卡片满足**建卡门槛**（跨课程复用 + 独立机制 + 领域通用概念）；
- [ ] 卡片位于知识区、用**英文命名**、frontmatter 含 `level` / `courses` / `tags`；
- [ ] 笔记提到概念处**内联了卡片链接**，全库断链为 0；
- [ ] 没有重复卡片、越权文件或用户内容覆盖；
- [ ] 没有残留 `.tmp` 文件与 `draft` / `filling` 状态。

### 阶段 5 附：frontmatter 契约

```yaml
# 课次笔记
type: lesson
course_id: AIAA4220
lesson_id: L02
lesson_order: 2
title: Embodied AI System Overview
aliases: [L02 具身 AI 系统概览]
source_file: lectures/L02.pdf
source_hash: sha256:...
source_range: lectures/L02.pdf:1-63
tags: [course/AIAA4220]
status: draft | filling | filled | reviewed | needs_review
vf: true
vf_version: course-cn-v2
vf_status: pristine | user_modified | locked
```

```yaml
# 知识卡片
type: concept
concept_id: world-model
canonical_name: World Model
aliases: [世界模型, WAM]
level: 核心 | 一般
courses: [AIAA4220]              # 归属课程，供课程索引反查
source_lessons: [L02]
tags: [concept/embodied-ai]
status: draft | filling | filled | reviewed | needs_review
vf: true
vf_version: course-cn-v2
vf_status: pristine | user_modified | locked
```

- `status` 是生成阶段，`vf_status` 是是否允许增量修改；
- `user_modified` 和 `locked` 默认只读；
- 旧文件被用户修改时保留原文，只在索引或新课次中补链接；
- 关键字段必须写成**单行标量**（工具链只解析单行 `key: value`）。

---

## 8. 失败处理与降级

| 失败场景 | 处理 |
|---|---|
| 源文件无法读取 | 停止该任务并报告具体文件，不使用摘要或索引替代原文 |
| PDF 后端不可用（缺 `pypdf`） | 回退到原始课件全文，仍不得使用路线图或笔记代替原文 |
| 页面只有无法确认的视觉内容 | 保留账本记录并标记 `needs_review`，不假装已读 |
| 找不到原文 | 删除伪引用，改为“课件未提供” |
| 卡片重复或空泛 | 只退回该卡片重写，不重跑整门课程 |
| 课次顺序错误 | 退回 `lesson-organizer`，按 `lesson_order` 重排 |
| 超时或返回格式错误 | 只重试该任务；同一任务最多重试 2 次，超限标记 `needs_review` |
| 单任务失败 | 只报告该任务，不伪造成功统计 |
| 不支持子 Agent / 不支持并行 | 每批最多 10 篇，顺序执行，协议不变 |

---

## 9. 脚本参考

### course-manifest.py

```bash
python3 scripts/course-manifest.py <course_dir> --output manifest.json
```

- 扫描 `SOURCE_EXTENSIONS = {.pdf, .ppt, .pptx, .md, .txt, .doc, .docx, .html, .htm}`；
- 跳过 `01. 课程笔记`、`02. 知识卡片`（旧结构）、`00. 课程索引.md`、隐藏文件；
- 读取 `.course-progress.json` 中记录的 `sources[].hash` 判定 `NEW/UPDATED/DONE/REMOVED`；
- 汇总 `lessons`、`concepts`、`states`，**不修改课程目录**。

### course-orchestrator.py

```bash
python3 scripts/course-orchestrator.py <course_dir> [--output .course-runtime.json]
```

- 为每个非 `DONE` 课件生成 `lesson-organizer` 任务信封；
- 用 `course_contracts.validate_task` 校验必填字段、`schema_version` 与写入边界；
- 输出 `.course-runtime.json`，包含 `tasks`、`invalid_tasks` 和说明字段；
- **不执行 Agent、不并发、不重试**。

### context-extractor.py

```bash
python3 scripts/context-extractor.py <vault_path> <extract_manifest> -o context_packets.json [--buffer 1] [--note-filter note1.md,note2.md]
```

- 第二个参数是**临时抽取清单**：课程版不生成路线图，因此用阶段 1 账本生成一个只含 `**知识点标题**  \`source_range: ...\`` 行的临时 markdown（放在 `/tmp`，**不写入课程目录**），格式见 [references/templates.md](./references/templates.md) 第 11 节；
- 解析 `source_range: {文件名}:{页码段}, ...`，支持单页 `102`、连续 `12-15`、混合 `12-15, 45-48, 102`、多文件 `A.pdf:12-15, B.md`；
- PDF 用 `pypdf` 按页抽取（默认 ±1 页缓冲）；Markdown/TXT 抽取全文；
- 缺少 `pypdf` 或文件不可读时输出 stderr 警告、跳过该文件并把对应 excerpt 置空，Agent 需回退到原始全文；
- 仅当课件为 PDF/Markdown/TXT 且需要精确抽取时使用；PPT/DOCX/HTML 由 Agent 直接读取全文。

### double-link-builder.py

课程版默认不生成 MOC 与路线图，因此该脚本仅作为批量候选工具：

```bash
python3 scripts/double-link-builder.py <course_dir> --output candidates.json
```

产出 `pairs` 候选对，由主 Agent 按阶段 4 的关系白名单人工/LLM 确认后写入；脚本产出的结构亲和候选**不得**直接当作已确认关系。

---

## 10. 输出质量标准

| 产物 | 核心要求 | 细则 |
|---|---|---|
| 逐页账本 | 每页都有 `role`、知识点、证据；无法确认的页标 `needs_review` | 阶段 1 |
| 课次笔记 | **按认知顺序讲透**；标题层级完整；正文无逐句页码、无审计语言；术语保留英文；含知识地图、术语表、自测 | 阶段 2 + `lesson-organizer` |
| 知识卡片 | **独立于课件**、不打开课件也能读懂；英文命名；含 `level` / `courses` / `tags`；≥2 个迁移问题 | 阶段 3 + `concept-card-builder` |
| 知识关联 | wikilink 目标真实存在；不为“网络完整”而穷举；断链 0 | 阶段 4 |
| 课程索引 | `lesson_order` 数字排序；含 Dataview 卡片视图；统计来自实际扫描 | `course-index-manager` |
| 知识库索引 | 全部卡片按领域/标签分组；新增卡片自动出现，无需手工登记 | `course-index-manager` |
| 格式合规 | 遵守 [`references/obsidian-conventions.md`](./references/obsidian-conventions.md)：无课件符号、无伪标题、callout/mermaid 使用得当 | 全体 |
| 状态与保护 | frontmatter 字段完整；无残留 `.tmp`；用户文件未被覆盖 | 阶段 5 + `course-reviewer` |

---

## 11. 交付汇报

只汇报处理的课件、生成/更新的课次与卡片、知识点覆盖情况及复核项。不要生成额外报告文件。建议格式：

```text
✅ 本次处理完成

📥 课件：L02（NEW）、L03（UPDATED）
📝 新课次：01. 课程笔记/L02 - CNN.md
🗂 知识卡片：新建 2 张、更新 1 张
📊 覆盖：L02 共 24 页，covered 21 / no_knowledge 2 / needs_review 1
⚠️ 复核项：L02 p.17 公式为图片，数值未确认（needs_review）
```

如果任一检查项未通过，先修复再汇报，**不得以 `success` 掩盖失败**。

---

## 12. 客户端差异与降级

| 能力 | 支持时 | 不支持时 |
|---|---|---|
| 子 Agent / 并行 | 每个 Agent ≤10 篇课次并行 | 主 Agent 顺序执行，每批 ≤10 篇，协议不变 |
| 子 Agent 文件访问 | 传递上下文包与 `allowed_writes` | 由主 Agent 代读原文，仍必须产出账本与覆盖清单 |
| 精确 PDF 抽取 | 使用 `context-extractor.py` | 读取原始全文，禁止用笔记或摘要替代 |
| 网络研究 | 不适用（课程版不需要） | 不适用 |

`agents/` 下的文件是平台无关的任务规格：支持子 Agent 的客户端将它们映射为子 Agent；不支持的客户端把每个文件当作提示词规格，由主 Agent 执行。

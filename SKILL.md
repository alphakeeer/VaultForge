---
name: VaultForge
description: >-
  将课程课件整理为中文 Obsidian 课程知识库：完整读取材料，建立逐页知识点账本，按教学顺序生成课次讲义，
  为重要知识点生成有证据、有案例、有原文引用的详细知识卡片，并支持低复杂度增量更新。
  适用于 PDF、PPT/PPTX、Markdown、TXT、Word、HTML 等课程材料。
---

# VaultForge 课程版

你不是在写摘要，也不是把每页幻灯片改写成几句 bullet。你要把课件变成可学习的课程材料：保留老师的讲解顺序，并让每个重要知识点都能独立回答“是什么、为什么、怎么工作、何时失效、课件在哪里讲”。

内容深度必须与来源材料成比例：材料讲得多就展开机制、步骤、公式、案例和限制；材料只提了名字就如实写“课件未展开”。不要用固定字数凑长度，也不要为了短而漏掉定义、机制、例子、限制或推导。

---

## 0. 文档地图

| 文件 | 作用 | 谁执行 |
|---|---|---|
| `SKILL.md`（本文件） | 流程控制、运行边界、质量门槛、协作协议 | 主 Agent |
| `agents/lesson-organizer.md` | 单个课件 → 一篇课次笔记 + 逐页账本 + 卡片候选 | 子 Agent |
| `agents/concept-card-builder.md` | 概念候选 → 新建/合并/复用知识卡片 | 子 Agent |
| `agents/course-index-manager.md` | 课程索引、全课程知识网络、进度文件的唯一写入者 | 子 Agent |
| `agents/course-reviewer.md` | 本次新增/更新文件的覆盖、证据、完整性审查 | 子 Agent |
| `references/templates.md` | 索引 / 课次 / 卡片 / 账本 / 任务信封 / 返回值的完整格式契约 | 主 Agent 与子 Agent 共享 |
| `scripts/course-manifest.py` | 扫描课件 hash 与已有产物，输出增量清单，不写课程目录 | 主 Agent |
| `scripts/course-orchestrator.py` | 生成 `.course-runtime.json` 任务信封并校验写入边界，不执行 Agent | 主 Agent |
| `scripts/context-extractor.py` | 按 `source_range` 抽取 PDF/Markdown/TXT 原文段落 | 主 Agent |
| `scripts/double-link-builder.py` | 通用知识库遗留双链工具，课程版仅在需要批量候选时使用 | 主 Agent |

---

## 1. 术语与稳定对象

| 术语 | 含义 |
|---|---|
| 课程目录 `course_dir` | 一门课的根目录，`course_id` 取目录名 |
| 课件 | 一份源材料（PDF/PPT/Markdown/TXT/Word/HTML），按 hash 追踪 |
| 课次 | 一份课件对应的一节课，编号 `L01`、`L02`…，由 `lesson_order` 排序 |
| 课次笔记 | `01. 课程笔记/Lxx - 主题.md`，`type: lesson` |
| 知识卡片 | `02. 知识卡片/概念.md`，`type: concept`，可跨课次复用 |
| 课程索引 | `00. 课程索引.md`，唯一目录与全课程知识网络 |
| 逐页知识点账本 | 阶段 1 产出的防漏证据层，逐页记录角色、知识点、原文证据 |
| 覆盖清单 | 课次笔记中的 `## 知识点覆盖清单` 与返回结构里的 `coverage` 数组 |
| 状态四态 | 课件状态 `NEW / UPDATED / DONE / REMOVED` |
| 文件生成状态 | `status: draft / filling / filled / reviewed / needs_review` |
| 用户保护状态 | `vf_status: pristine / user_modified / locked` |

课程版输出三类稳定对象：

1. `00. 课程索引.md`：整门课的目录、进度和全课程知识网络；
2. `01. 课程笔记/Lxx - 主题.md`：按课件顺序完整讲解本节课，并列出本节知识网络；
3. `02. 知识卡片/概念.md`：对可复用概念作独立、详细、可交叉引用的解释。

---

## 2. 核心原则

### ⚠️ 原则 1：完整性优先——没读完不许写

**绝对禁止**在只读了部分页面、摘要或文件名的情况下生成课次笔记或知识卡片。

- 必须读完用户选中的**全部**课件；
- 优先单次完整读取；只有遇到技术上限时才分批；
- 分批时自动继续（例如 PDF 每批 50 页），**不得逐批向用户确认**；
- 只有确认全部内容已读后，才允许进入写作。

### ⚠️ 原则 2：内容深度必须与来源材料成比例

| 材料情况 | 处理 | 反例 |
|---|---|---|
| 只提到名称、没有展开 | 在课次笔记中写“课件未展开”，不创建卡片 | 用常识把 1 行标题写成一整页科普 |
| 有定义与机制，跨 2–4 页 | 课次笔记展开 + 视复用价值建卡片 | 只写一句话定义 |
| 跨多页、含公式/步骤/案例/限制 | 必须展开机制、推导、案例与边界，可拆多张卡片或 `lesson_only` 多节 | 用一段总述代替多个知识点 |
| 逻辑连贯但篇幅大（如 15 页一个主题） | 保持为完整的一节/一张卡片，讲透 | 机械切成 15 个文件 |

判断标准不是字数，而是：读者读完能否回答**是什么、解决什么、怎么工作、何时不用、课件在哪里讲**。

### ⚠️ 原则 3：覆盖优先，文件克制

必须覆盖课件中的所有主要知识点，但不是每个知识点都创建一个文件。只有具有独立解释价值、会在后续课程复用、或被用户指定为重点的概念才创建知识卡片；其余内容写入对应课次笔记。

文件少不是目标；目标是没有重复文件、没有空壳文件、没有信息丢失。

### ⚠️ 原则 4：证据可回溯

每个课次笔记和知识卡片都记录来源文件、课次、页码/slide/段落范围与来源 hash。任何定义、数字、实验结果、引用和判断都必须能回到 `source_range`；无法定位就删除或标记 `needs_review`，不得保留伪引用。

### ⚠️ 原则 5：增量优先，用户内容不可覆盖

新增课件只生成新增课次、覆盖新增内容，并合并已有概念卡片。默认不重写历史课次笔记，不生成路线图版本，不生成每次更新报告。`user_modified` 和 `locked` 文件只读；冲突时保留用户正文并返回建议。

### ⚠️ 原则 6：课次顺序优先，卡片独立成篇

课次笔记回答“老师这一节课如何讲”，必须保留课件顺序，不得把材料重排成抽象主题列表。知识卡片回答“这个概念本身是什么”，按概念组织，不受某一节课的叙述顺序限制，但不得机械复制课次笔记段落。

### ⚠️ 原则 7：补充知识必须标注

允许补充帮助理解的常识性解释，但必须明确区分“课件内容”与“补充解释”，不得把补充知识伪装成课件结论。

---

## 3. 运行边界

### 允许

- 完整读取用户选中的课件；
- 使用 `scripts/context-extractor.py` 抽取原文上下文包；
- 使用 `scripts/course-manifest.py` 扫描增量状态；
- 使用 `scripts/course-orchestrator.py` 生成任务信封并校验写入边界；
- 补充帮助理解、且已明确标注的常识解释。

### 禁止

- 联网研究争议、共识或观点；
- 生成路线图版本（`Learning Roadmap vN`）、每个主题的 MOC、`Core Questions.md`、更新报告或争议分析文件；
- 生成 `00. 课程索引.md`、`01. 课程笔记/`、`02. 知识卡片/`、`.course-progress.md`、`.course-progress.json`、`.course-runtime.json` 之外的文件；
- 不生成额外报告文件（变更历史交给 Git）；
- 依据标题或记忆补写未读内容；用一段总述伪装多个知识点；编造案例、实验、结论或引用；
- 覆盖 `user_modified` / `locked` 文件，或写入 `allowed_writes` 之外的路径。

图像、公式、表格、动画或 speaker notes 无法读取时标记 `needs_review`，不能假装覆盖。

---

## 4. 输出契约

```text
课程名/
├── 00. 课程索引.md              # 目录 + 全课程知识网络 + 卡片索引
├── 01. 课程笔记/
│   ├── L01 - 课程主题.md        # type: lesson
│   └── L02 - 课程主题.md
├── 02. 知识卡片/
│   ├── CNN.md                   # type: concept
│   └── RNN.md
├── .course-progress.md          # 人类可读进度（索引 Agent 维护）
├── .course-progress.json        # 机器状态（索引 Agent 维护，可选）
└── .course-runtime.json         # 任务信封（编排脚本生成）
```

一个课件通常对应一篇课次笔记，但可以产生多个知识卡片。卡片按可独立学习的知识点拆分，不按 bullet 机械拆分。

详细格式契约见 [references/templates.md](./references/templates.md)。

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
| `concept-card-builder` | `allowed_writes` 中指定的新卡片；用户未修改卡片的受控增量 | 用户修改/锁定卡片、课次笔记正文、索引 | 卡片文件 + 概念判定 |
| `course-index-manager` | `00. 课程索引.md`、`.course-progress.md`、`.course-progress.json` | 课次正文、卡片正文 | 索引变更 + 统计 |
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
schema_version: course-cn-v2
```

`source_files[]` 的字段名固定为 `file` / `hash` / `state`（由 `course-manifest.py` 产出）。`course-orchestrator.py` 按顺序生成 `lesson_id`，**不写入 `lesson_order`**；主 Agent 必须在分发前按课件教学顺序补充 `lesson_order`（正整数、唯一）。

校验规则：`task_id / agent / course_id / source_files / allowed_writes / must_return / schema_version` 缺一不可；`schema_version` 必须等于 `course-cn-v2`；`source_files` 与 `allowed_writes` 必须是数组；任何 `allowed_writes` 越出课程目录或写隐藏文件都会被拒绝（`write_outside_course` / `hidden_write`）。

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

在分发任何写作任务前，扫描 `01. 课程笔记/` 与 `02. 知识卡片/` 中全部产物的 frontmatter `status`，按下表处理：

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

课次笔记保留讲解顺序，但不能用一段总述替代多个知识点。推荐结构：

```markdown
# L02 - 主题
## 本节学习目标
## 课件主线
### 1. 问题与动机
### 2. 核心概念
### 3. 机制、步骤或公式
### 4. 例子与系统案例
### 5. 限制、边界与后续扩展
## 知识点覆盖清单
## 本节知识网络
## 本节知识卡片
## 来源与复核项
```

每个小节必须说明：问题是什么、定义/假设、机制、课件证据或例子、与前后的关系。覆盖率与顺序的判定以阶段 1 账本为准。

**正例**：

```markdown
### 3. 自注意力机制
课件先用“句子中每个词都要参考其他词”的动机引入（p.12），然后给出 Q/K/V 三个投影矩阵…
公式 (3) 的 softmax 分母用于归一化注意力权重（p.13）。
⚠️ 课件未给出复杂度推导。
```

**反例（禁止）**：

```markdown
### 2. 核心概念
本节课讲了自注意力、多头注意力和位置编码，它们都很重要，是 Transformer 的基础。
```

> 反例用一个段落“覆盖”了三个知识点，却没有定义、机制、证据或来源，视为未覆盖。

### 阶段 3：知识卡片

**执行者：`concept-card-builder`（概念候选去重后）。**

卡片候选判定：

- 材料跨多个页面展开，或含公式/步骤/案例/限制；
- 后续课程会复用；
- 有独立学习目标。

只出现一次且只有标题的背景项可 `lesson_only`。合并必须写出理由和共同来源。

每张卡片必须使用：

```markdown
# 知识点名称
## 一句话定义
## 核心知识点
### 背景与要解决的问题
### 精确定义与边界
### 工作机制或推导
### 例子、公式或实现直觉
### 应用条件与失败模式
### 与其他知识点的关系
## 相关案例
## 原文引用
## 在课程中的出现位置
## 核心思考
```

硬性要求：

- 核心知识点必须覆盖背景、定义、机制、应用和关系；
- 案例必须来自课件，说明背景、过程、结果和启示；无案例时明确写“课件未提供案例”；
- 引用必须是实际摘录，标明来源与页码/slide，不能把改写当引文；
- 至少提出两个不重复、能检验迁移理解的问题，不得使用“请总结本文”；
- 材料未覆盖的章节写明“课件未覆盖”，不用外部内容填充。

质量按信息完整性判断：读者仍无法回答“是什么、解决什么、怎么工作、何时不用、课件在哪里讲”时，卡片不合格。

### 阶段 4：知识网络

只使用以下关系类型：

| 关系 | 含义 | 判定依据 |
|---|---|---|
| `prerequisite` | 前置知识 | A 的定义或推导直接依赖 B |
| `component` | 组成部分 | A 是 B 的组成或子步骤 |
| `contrast` | 对比概念 | 课件明确比较二者差异 |
| `extension` | 后续扩展或演化 | B 是 A 的推广、改进或后续课程内容 |
| `application` | 应用关系 | A 的应用场景直接使用 B |
| `sequence` | 课程讲解顺序 | 课件按顺序连续讲解，且无更强关系 |

链接必须有课件依据和理由，**不能仅因标题共享词语就连边**。关系脚本只生成候选，最终由主 Agent 确认；每个卡片反向链接至少一个课次。所有链接写入前去重，禁止重复行。

### 阶段 5：审查与状态

**执行者：`course-reviewer` + 主 Agent。**

写入采用 `.tmp → 检查 → rename`（暂存文件名如 `L02 - CNN.md.tmp`）。逐项检查：

- [ ] 每个课件都有 coverage，且每页状态为 `covered` / `no_knowledge` / `needs_review`；
- [ ] `covered` 条目有非空知识点和有效正整数页码；
- [ ] 主要知识点在课次正文有解释和来源；
- [ ] 卡片结构、案例、引用、思考题完整，无空壳章节；
- [ ] 没有重复卡片、断链、越权文件或用户内容覆盖；
- [ ] 无法确认的图像/公式/视频已标记 `needs_review`；
- [ ] 没有残留 `.tmp` 文件与 `draft/filling` 状态。

不满足时不能报告 `success`。

frontmatter 契约（完整字段见 [references/templates.md](./references/templates.md)）：

```yaml
---
type: lesson | concept
course_id: deep-learning
lesson_id: L02           # lesson 必填
lesson_order: 2          # lesson 必填
concept_id: cnn          # concept 必填
canonical_name: CNN      # concept 必填
aliases: [卷积神经网络, ConvNet]
source_file: lectures/L02.pdf
source_hash: sha256:...
source_range: lectures/L02.pdf:1-42
status: draft | filling | filled | reviewed | needs_review
vf: true
vf_version: course-cn-v1
vf_status: pristine | user_modified | locked
---
```

- `status` 是生成阶段，`vf_status` 是是否允许增量修改；
- `user_modified` 和 `locked` 默认只读；
- 旧文件被用户修改时保留原文，只在索引或新课次中补链接。

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
- 跳过 `01. 课程笔记`、`02. 知识卡片`、`00. 课程索引.md`、隐藏文件；
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
| 课次笔记 | 保留课件顺序；每个主要知识点有定义/边界、机制、证据、关系；覆盖清单与账本一致 | 阶段 2 + `lesson-organizer` |
| 知识卡片 | 六段式结构完整；案例来自课件；原文引用可定位；≥2 个迁移问题；无同义反复 | 阶段 3 + `concept-card-builder` |
| 知识网络 | 仅六种关系；有课件依据；去重；卡片反向链接课次 | 阶段 4 |
| 课程索引 | `lesson_order` 数字排序；链接目标存在；统计来自实际扫描 | `course-index-manager` |
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

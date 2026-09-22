# VaultForge 课程版

> **一句话定位**：把课程课件写成**能读懂、能复习、能脱离课件使用**的中文 Obsidian 学习笔记，并把跨课程复用的概念沉淀到知识区。

VaultForge 课程版面向“每周持续增加课件”的长期学习场景。产出分两类，定位不同：

- **课次笔记**（主产物）：按**认知顺序**讲透一节课——先懂什么才能懂什么。正文不挂页码，允许并鼓励用自己的话讲、举例子、做类比；
- **知识卡片**（跨课程资产）：抽取 CNN、Kalman Filter、World Model 等**领域通用概念**，存放在**知识区**（如 `50 Knowledge/`），不被任何一门课独占，**读者不打开课件也能读懂**。

最高优先级是**可理解性优先于完整性**：材料讲得多就展开机制与例子；材料只提了名字就如实简述——**不写“课件未展开”这类审计式声明**。

本文件是使用说明；**流程控制、运行边界与质量门槛的唯一契约来源是 [SKILL.md](./SKILL.md)**。

---

## 与通用版 / 传统流程的差异

| 对比项 | 传统笔记流程 / 通用知识库版 | VaultForge 课程版 |
|---|---|---|
| 组织主轴 | 抽象主题分类、MOC、路线图 | 课次顺序 `lesson_order`（L01、L02…），卡片按概念独立组织 |
| 阅读要求 | 抽查式阅读即可动笔 | 必须读完选中课件；是否读完以逐页账本为准 |
| 防漏机制 | 靠自觉 | 逐页知识点账本 + `coverage` 覆盖清单 + 阶段 5 逐项审查 |
| 研究能力 | 联网做争议/共识/观点分析 | **不联网研究**，只用课件原文，补充解释必须标注 |
| 导航产物 | 每个主题一个 MOC、双版本路线图 | 唯一的 `00. 课程索引.md`（目录 + 知识网络 + 卡片索引） |
| 增量方式 | 生成更新报告并刷新历史笔记 | 只处理受影响课次与卡片，不重写历史、不生成报告 |
| 报告文件 | 每次更新一份 Update Report | 不生成额外报告文件，变更历史交给 Git |
| 契约校验 | 无 | 任务信封与返回值按 `course-cn-v2` schema 校验 |

---

## 核心概念术语表

| 术语 | 含义 |
|---|---|
| 课程目录 `course_dir` | 一门课的根目录，`course_id` 取目录名 |
| 课件 | 一份源材料（PDF/PPT/PPTX/Markdown/TXT/Word/HTML），按 sha256 hash 追踪 |
| 课次 | 一份课件对应的一节课，编号 `L01`、`L02`…，由 `lesson_order` 排序 |
| 课次笔记 | `01. 课程笔记/Lxx - 主题.md`，frontmatter `type: lesson` |
| 知识卡片 | `02. 知识卡片/概念.md`，frontmatter `type: concept`，可跨课次复用 |
| 课程索引 | `00. 课程索引.md`，整门课唯一的目录与全课程知识网络 |
| 逐页知识点账本 | 阶段 1 产出的防漏证据层，逐页记录 `role`、知识点、原文证据 |
| 覆盖清单 | 课次笔记中的 `## 知识点覆盖清单` 与返回结构里的 `coverage` 数组 |
| 状态四态 | 课件状态 `NEW / UPDATED / DONE / REMOVED` |
| 文件生成状态 `status` | `draft / filling / filled / reviewed / needs_review` |
| 用户保护状态 `vf_status` | `pristine`（可增量更新）/ `user_modified`（只读）/ `locked`（只读） |
| 概念候选判定 | `create / reuse / merge / lesson_only` |
| 知识网络关系 | 仅六种：`prerequisite / component / contrast / extension / application / sequence` |
| 覆盖状态 | 每页为 `covered` / `no_knowledge` / `needs_review` |

---

## 输出目录树

产出分布在**两个位置**：课程目录放笔记，知识区放跨课程卡片。

```text
10 Courses/AIAA4220/                 # 课程目录
├── 00. 课程索引.md                  # 目录 + 进度 + 关联卡片的 Dataview 视图
├── 01. 课程笔记/
│   └── L02 - Embodied AI System Overview.md   # type: lesson
├── .course-progress.md              # 人类可读进度（索引 Agent 维护）
├── .course-progress.json            # 机器状态（索引 Agent 维护）
└── .course-runtime.json             # 任务信封（编排脚本生成）

50 Knowledge/                        # 知识区（跨课程共享）
├── _index.md                        # 知识库索引（Dataview 自动维护）
├── AI/
│   └── World Model.md               # type: concept
└── Computer Science/
    └── Kalman Filter.md
```

一个课件通常对应一篇课次笔记；知识卡片的数量由**建卡门槛**决定（跨课程复用 + 独立机制 + 领域通用），**一个课次 0–3 张**，宁少勿多。

知识区位置可用课程目录下的 `.vaultforge.json` 配置：

```json
{ "knowledge_root": "50 Knowledge", "course_code": "AIAA4220" }
```

未配置时自动探测：从课程目录向上找到含 `.obsidian` 的 vault 根，取其中的 `50 Knowledge/`。

除上述路径外不生成任何文件（不生成路线图、MOC、争议分析或更新报告）。详细字段契约见 [references/templates.md](./references/templates.md)，格式规范见 [references/obsidian-conventions.md](./references/obsidian-conventions.md)。

---

## 五阶段工作流

```text
阶段 0  课程扫描与增量判定   →  NEW / UPDATED / DONE / REMOVED + 模式选择
阶段 1  完整阅读与逐页知识点账本 →  读完全部课件，建立防漏证据层
阶段 2  课次笔记             →  按教学顺序成文（可并行）
阶段 3  知识卡片             →  候选去重后新建 / 合并 / 复用
阶段 4  知识网络             →  六种关系白名单 + 去重写入
阶段 5  审查与状态           →  逐项校验、更新索引与进度、一次性汇报
```

阶段 0、1、4 由主 Agent 执行（阶段 1 的阅读与账本也可按课件分发给 `lesson-organizer`），阶段 2 由 `lesson-organizer`、阶段 3 由 `concept-card-builder`、阶段 5 由 `course-reviewer` 与主 Agent 共同完成。索引与进度文件只由 `course-index-manager` 写入。

---

## 安装与快速开始

```bash
# 1. 放入 Agent Skills 目录
git clone https://github.com/alphakeeer/VaultForge.git ~/.agents/skills/VaultForge

# 2. （推荐）安装 PDF 精确页码抽取依赖
pip install pypdf
```

将课程课件放进一个课程目录（例如 `~/vault/深度学习/`），在客户端中加载 `SKILL.md` 并用中文说明需求。预生成任务信封：

```bash
python3 scripts/course-orchestrator.py <课程目录>
```

该命令会扫描增量状态、为每个非 `DONE` 课件生成 `lesson-organizer` 任务信封、校验写入边界，并写出 `.course-runtime.json`（含 `tasks`、`invalid_tasks` 与说明字段）。**它不执行 Agent、不并发、不重试**，课程内容仍由 Agent 按 `SKILL.md` 生成。所有任务信封与返回值必须符合 `course_contracts.py` 定义的 `course-cn-v2` 契约。

---

## 支持格式

| 格式 | 处理方式 | 页码粒度 |
|---|---|---|
| PDF | `scripts/context-extractor.py` 用 `pypdf` 抽取 | 精确到页，支持 `12-15, 45-48` |
| PPT / PPTX | 由宿主 Agent 直接读取全文 | 记录 slide 范围 |
| Markdown / TXT | 可全文抽取，也可按段落范围定位 | 段落 / 行 |
| Word（.doc/.docx） | 由宿主 Agent 读取全文 | 无固定页边界 |
| HTML（.html/.htm） | 由宿主 Agent 读取全文 | 无固定页边界 |

图像、公式、表格、动画或 speaker notes 无法读取时，必须标记 `needs_review`，不得假装已覆盖。

---

## 工程保障

- **增量扫描**：`course-manifest.py` 用相对路径 + sha256 判定 `NEW / UPDATED / DONE / REMOVED`，默认跳过 `DONE`，被删除的课件记为 `REMOVED` 而不静默删产物。
- **原子写入与断点恢复**：统一 `.tmp → 校验 → rename`，崩溃不破坏已完成文件；每篇产物带 `status`（`draft → filling → filled → reviewed`），重跑时按状态续做，同一任务最多重试 2 次，超限标记 `needs_review`。
- **概念去重**：卡片任务在候选汇总、去重之后才执行；优先复用 `concept_id` / 标准名 / 别名，同名异义用显式上下文后缀（如 `attention-nlp`）。
- **用户修改保护**：`vf_status` 为 `user_modified` 或 `locked` 的文件只读，冲突时保留用户正文并返回建议。
- **来源可回溯**：笔记与卡片记录 `source_file`、`source_hash`、`source_range`（页码/slide/段落范围），无法定位的引用必须删除或标记 `needs_review`。
- **写入边界与契约校验**：任务信封的 `allowed_writes` 越出课程目录或指向隐藏文件即被拒绝（`write_outside_course` / `hidden_write`）；`schema_version` 必须为 `course-cn-v2`，`source_files`、`allowed_writes` 必须是数组，覆盖条目页码必须是正整数。

---

## 常见问题 FAQ

**Q1：如何开始？**
把课件放进一个课程目录，加载 `SKILL.md`，用中文说明课程目录和要处理的课件。首次运行 `.course-progress.*` 缺失时全部按 `NEW` 处理，不会报错。建议先用小课件试跑。

**Q2：任务中断后如何恢复？**
重新触发即可。阶段 0 会重扫 hash，阶段 5 会检查每篇产物的 `status`；已 `DONE` 的课件默认跳过，只继续未完成或失败的任务。同一任务最多重试 2 次，超限标记 `needs_review`，不会重跑整门课程。

**Q3：生成内容太薄怎么办？**
课程版不以固定字数衡量质量，而是看读者能否回答“是什么、解决什么、怎么工作、何时不用、课件在哪里讲”。`lesson-organizer` 必须按账本逐项回答，`concept-card-builder` 必须展开机制、案例、限制与引用；用一段总述“覆盖”多个知识点会被阶段 5 判为未覆盖。材料本身只提了名称时，如实写“课件未展开”，不用外部常识填充。

**Q4：如何增量添加课件？**
把新课件放进同一个课程目录（或用新版本覆盖同名文件）后重新触发。阶段 0 判定 `NEW` / `UPDATED`，只生成新增课次、合并已有卡片、更新受影响课次；历史课次笔记默认不重写，`user_modified` / `locked` 文件只读。无法确定影响范围时标记 `needs_review`，不会静默覆盖旧内容。

**Q5：支持哪些格式？**
PDF（精确页码抽取）、PPT/PPTX（slide 范围）、Markdown、TXT、Word（.doc/.docx）、HTML（.html/.htm）。PDF / Markdown / TXT 可走 `context-extractor.py` 精确抽取；其余由宿主 Agent 读取全文，因为缺少固定页边界。

**Q6：为什么没有路线图、MOC 和争议分析？**
课程版的定位是“把这门课讲清楚”，不是“构建一个领域知识地图”。路线图、每主题 MOC、`Core Questions.md`、更新报告和联网争议研究都已被移除，导航统一收敛到唯一的 `00. 课程索引.md`；联网研究被明确禁止，因为课件之外的观点无法回溯到 `source_range`。

**Q7：统计数字是怎么来的？**
所有统计必须来自实际文件扫描或子 Agent 的可核验结果，**禁止使用模型自报估算**。`course-manifest.py` 的 `states` 汇总四态数量，索引 Agent 重新扫描实际文件统计课次数、卡片数、覆盖点数与待审查数；无法确认的页面计入 `needs_review` 而非 `covered`。

---

## 设计取舍

已移除的通用知识库功能：

- 联网争议研究、共识与观点分析；
- 每个主题单独的 MOC、双版本学习路线图、`Core Questions.md`；
- 每次增量更新的独立报告文件；
- 以“一个 bullet 一个原子笔记”为默认规则；
- 所有 `00. 课程索引.md`、`01. 课程笔记/`、`02. 知识卡片/`、`.course-progress.*`、`.course-runtime.json` 之外的产物。

保留并强化的工程能力：

- 完整阅读 + 逐页知识点账本 + 覆盖清单的防漏链路；
- 增量扫描、断点恢复、原子写入、概念去重、用户修改保护、来源可回溯；
- 六种关系白名单的知识网络，链接必须有课件依据而非词面相似；
- `course-cn-v2` schema 的任务信封与写入边界校验。

---

## 开发与测试

```bash
cd VaultForge
python3 -m unittest discover -s tests
```

测试覆盖上下文抽取、双链候选、课程运行时契约（稳定 `concept_id`、越权写入拒绝、覆盖条目校验）与 Skill 完整性检查。

---

## 项目结构

```text
VaultForge/
├── README.md                    # 本文件：使用说明
├── SKILL.md                     # 唯一契约：流程、边界、质量门槛
├── COMPATIBILITY.md             # 多客户端兼容与降级说明
├── HISTORY.md                   # 失败案例与改进记录
├── EVALUATION.md                # 自评与验收口径
├── agents/
│   ├── lesson-organizer.md      # 单课件 → 课次笔记 + 逐页账本 + 卡片候选
│   ├── concept-card-builder.md  # 概念候选 → 新建 / 合并 / 复用卡片
│   ├── course-index-manager.md  # 索引与进度文件的唯一写入者
│   └── course-reviewer.md       # 覆盖、证据与完整性审查
├── references/
│   └── templates.md             # 索引 / 课次 / 卡片 / 账本 / 信封 / 返回值契约
├── scripts/
│   ├── course-manifest.py       # 增量清单（只读课程目录）
│   ├── course-orchestrator.py   # 生成并校验 .course-runtime.json
│   ├── context-extractor.py     # 按 source_range 抽取原文段落
│   ├── double-link-builder.py   # 双链候选工具（仅批量候选）
│   └── course_contracts.py      # course-cn-v2 契约与路径安全
└── tests/                       # fixtures/ 与 test_*.py
```

---

## 分支说明

- 本地定制分支：`course-cn-v1`（课程版开发主线）；
- `origin`：个人 Fork（`https://github.com/alphakeeer/VaultForge.git`）；
- `upstream`：原始通用版仓库（`https://github.com/Easonnotsing/VaultForge.git`）。

# VaultForge 课程版设计评估

> 评估对象：课程版（`course-cn-v1` 产物 / `course-cn-v2` 运行时契约）。
> 评估方式：以 `SKILL.md` 为唯一契约来源，以 `scripts/` 的实际行为与 `tests/` 的覆盖为准，不采用主观评分。
> 术语与 `SKILL.md` 第 1 节一致：课程目录、课件、课次、课次笔记、知识卡片、逐页知识点账本、覆盖清单、`NEW/UPDATED/DONE/REMOVED`、`status`、`vf_status`。

---

## 一、评估目标与适用范围

### 1.1 评估目标

课程版面向的是一条高频重复的工作流：学习者每周新增一到多份课件，希望把它们持续沉淀成可复习的中文 Obsidian 课程知识库。评估要回答四个问题：

1. **不遗漏**：新增课件的主要知识点是否都被读入并落到产物里，而不是被摘要吞掉；
2. **不重复**：跨课次的同一概念是否收敛到唯一一张知识卡片；
3. **不欺骗**：来源是否可回溯、无法确认的内容是否诚实标记，而不是用模型记忆补齐；
4. **不退化**：重复运行时是否只处理增量、是否保护用户已经手改的内容。

### 1.2 适用范围

| 适用 | 不适用 |
|---|---|
| 有明确课次边界的课件集合（PDF/PPT/PPTX/Markdown/TXT/Word/HTML） | 无结构的长篇资料汇总、需要主题重排的知识库 |
| 需要保留“老师这一节课怎么讲”的顺序与讲解脉络 | 只需一句话摘要或背诵卡片（Anki 式抽认）的场景 |
| 概念会跨课次复用的课程（如神经网络、平台战略） | 一次性读物、单篇论文精读 |
| 增量式维护、用户会手工修改部分笔记 | 一次性全量生成后不再维护的静态导出 |

### 1.3 不在评估范围内

课程版已删除通用版的路线图版本、每主题 MOC、`Core Questions.md`、联网争议研究与 Phase 6 深度研究、独立更新报告（见 `SKILL.md` 第 3 节禁止项与 `test_skill_integrity.py::test_research_and_redundant_outputs_removed`）。这些能力不再作为评估维度，也不应被视为缺项。

---

## 二、关键质量指标

所有指标的“测量方法”都要求从**实际文件、frontmatter 或脚本输出**取数；`SKILL.md` 第 5 节明确禁止把模型自报估算写入进度文件或用于汇报。

| 指标 | 定义 | 测量方法（来自实际扫描，非模型自报） | 目标值 |
|---|---|---|---|
| 知识点覆盖率 | 账本中已读且确有知识内容的页，其知识点在课次正文有对应解释与来源的比例 | 用 `course_contracts.validate_coverage` 校验子 Agent 返回的 `coverage`：每页 `source` 属于 `source_files`、`page` 为正整数、`status ∈ {covered,no_knowledge,needs_review}`、非 `no_knowledge` 页必须有非空 `knowledge_points`；再把课次笔记 `## 知识点覆盖清单` 与账本逐页对照 | 100%（缺口只能表现为 `needs_review`，不能无声缺失） |
| 课次顺序忠实度 | 课次笔记正文小节顺序与课件页序一致的程度 | 从笔记小节的页码标注（如 `p.12`）与账本各知识点首次出现页分别抽取序号，比较是否单调不减；合并相邻稀疏页不算逆序 | 无逆序对；`SKILL.md` 第 2 节原则 6 要求保留讲解顺序 |
| 概念卡片重复率 | 规范化名称相同的概念被写成多张卡片的比例 | 扫描 `02. 知识卡片/*.md` 的 `canonical_name` / `aliases` / `concept_id`，用 `course_contracts.normalize_name`（NFKC + casefold + 去空格与连字符）归并后统计 | 0 重复卡片；同名异义必须带显式上下文后缀（如 `attention-nlp`） |
| 来源可回溯率（`source_range` 完整度） | 定义、数字、实验结果、引用、判断等关键条目带有可解析来源文件与页码/slide 段的比例 | 正则扫描 frontmatter 的 `source_range` 与正文引用，并用 `context-extractor.py` 的 `_parse_multi_source_ranges` 实际解析；解析失败或缺失即计入缺口，同时检查 `source_hash` 是否与 `course-manifest.py` 的 sha256 一致 | 关键条目 100%；无法定位的删除或标 `needs_review` |
| 增量处理文件数 | 单次运行实际读取并生成产物的课件数 | `python3 scripts/course-manifest.py <course_dir>` 输出 `states`（`NEW` / `UPDATED` / `DONE` / `REMOVED`），以及 `.course-runtime.json` 中 `tasks` 的数量；`DONE` 课件不应产生任务 | 默认只处理 `NEW` + `UPDATED`；`DONE` 任务数为 0 |
| 用户修改文件保护率 | `vf_status` 为 `user_modified` 或 `locked` 的文件在运行前后内容未被改写 | 运行前后对候选文件做 sha256 与 mtime 对比，并扫描 frontmatter 的 `vf_status`；`course-reviewer` 的“关系与保护”检查项要求正文、hash、mtime 均未变 | 100%；冲突时保留用户正文并返回建议 |
| 空壳/占位内容率 | 必填章节为空、仅含模板占位文本，或课次正文用一段总述冒充多个知识点的条目比例 | 脚本扫描卡片六段式结构（一句话定义/核心知识点/案例/原文引用/出现位置/核心思考）与课次小节的正文长度和占位词；命中“待补充”“TBD”“…”或空章节即计入。显式声明“课件未展开 / 课件未提供案例 / 课件未覆盖”**不算**空壳 | 0；`SKILL.md` 阶段 5 要求无空壳章节 |
| `needs_review` 诚实标记率 | 实际存在图片、公式、动画或 speaker notes 而无法确认内容的页面中，被标记 `needs_review` 的比例 | 账本页数与源文件实际页数核对（无缺页），再对无法确认页抽样人工比对；同时确认 `status` 中不残留 `draft/filling` | 100%；不得出现“正文声称已覆盖、实际未读”的页面 |

> 说明：上表是**可复核的检查口径**，不引入 1–5 星或百分制主观打分。每一条都能通过运行脚本和对产物 grep/parse 复现。

---

## 三、设计取舍

| 取舍点 | 课程版选择 | 放弃的方案 | 理由与代价 |
|---|---|---|---|
| 产物结构 | 双层：课次笔记（`01. 课程笔记/Lxx - 主题.md`）+ 知识卡片（`02. 知识卡片/概念.md`） | 一个 bullet 一个原子笔记；或只做单一课程摘要 | 课次笔记保留课件顺序回答“这节课怎么讲”，知识卡片按概念组织回答“这个概念本身是什么”。代价是同一知识可能同时出现在两处，因此规定卡片不得机械复制课次笔记段落，且用 `lesson_only` 抑制无复用价值的一次性内容 |
| 路线图 / MOC / 争议研究 | 全部不做，只保留唯一 `00. 课程索引.md` | 双版本路线图 `Learning Roadmap vN`、每主题 MOC、联网争议分析、Phase 6 深度研究 | 课程整理的既有结构来自课件本身（课次边界天然存在），再叠加人工路线图与 MOC 只会产生与课次笔记竞争的重复产物和额外联网成本。代价是失去跨课程的“学习路径推荐”，这部分交给用户或索引中的课程目录 |
| 内容深度 | 按来源材料的展开量成比例：跨多页且有机制/公式/案例就展开，只提名字就写“课件未展开” | 固定字数下限（如“每篇 200+ 字”）、固定模板槽位 | 固定字数会诱导用常识和套话凑长度，破坏可回溯性。代价是产物长度不可预测，需要靠覆盖率与空壳率而非字数来验收 |
| 索引写入 | 最后阶段由 `course-index-manager` 单写者完成，关系去重后写入 | 多个 Agent 并行追加索引或双链 | 并发追加会产生重复链接与顺序错乱。代价是索引成为流程末端瓶颈，必须等课次与卡片稳定后才执行 |
| 增量策略 | 以课件 hash 为判据，默认只处理 `NEW/UPDATED`，不重写历史课次 | 每次全量重算整门课程 | 高频课件场景下全量重算成本过高且会覆盖用户修改。代价是影响范围判断出错时可能漏更新，因此规定无法确定影响范围时标 `needs_review` 而非静默覆盖 |
| 概念卡片并发 | 必须先汇总、去重候选，再串行落盘 | 候选未去重就让多个卡片 Agent 并行创建 | 未去重的并行创建几乎必然产生同名卡片。代价是卡片阶段无法完全并行，吞吐略低 |

---

## 四、工程保障评估

### 4.1 增量扫描（`scripts/course-manifest.py`）

- 按 `SOURCE_EXTENSIONS = {.pdf, .ppt, .pptx, .md, .txt, .doc, .docx, .html, .htm}` 递归扫描，跳过 `01. 课程笔记`、`02. 知识卡片`、`00. 课程索引.md` 与隐藏文件，因此产物不会被误判为课件；
- 每个课件计算 sha256，与 `.course-progress.json` 的 `sources[].hash` 比对，得到 `DONE`（hash 未变）/ `UPDATED`（路径同、hash 变）/ `NEW`（未记录）/ `REMOVED`（记录中存在、磁盘上消失）；
- 输出 `lessons`、`concepts`、`states` 与 `progress_exists`，**不修改课程目录**；扫描后只读，写入由后续 Agent 负责。

覆盖证据：`test_course_runtime.py::ManifestStateTest::test_new_done_updated_removed` 实际构造 hash 变化并断言 `DONE → UPDATED`。

### 4.2 原子写入

- JSON 侧：`course_contracts.atomic_json_write` 先写 `<name>.tmp`，再 `json.loads` 回读校验，最后 `replace` 为正式文件；写坏或中断只会留下 `.tmp`，不会破坏旧文件；
- Markdown 侧：`SKILL.md` 阶段 5 与各 Agent 规格统一要求 `.tmp → 检查 → rename`，并把“没有残留 `.tmp` 文件”列为审查项，同时要求不残留 `draft/filling` 状态。

覆盖证据：`test_skill_integrity.py` 校验契约文本存在；脚本语法由 `ScriptSyntaxTest` 编译验证。

### 4.3 断点恢复

- 挂起点由两类稳定状态描述：课件级 `NEW/UPDATED/DONE/REMOVED`（`course-manifest.py` 依据 hash 复算）与文件级 `status: draft/filling/filled/reviewed/needs_review`；
- 重启后 `DONE` 课件被天然跳过，`filling` 文件按“存在 `.tmp` → 完成 rename；无 `.tmp` → 标记 `filled`”的规则收敛，`needs_review` 条目在阶段 0 汇总上报；
- `.course-progress.md` / `.course-progress.json` 缺失或损坏时不报错：缺失视为首次运行全部 `NEW`，`json.JSONDecodeError` / `OSError` 被捕获后按空进度处理（`course-manifest.py` 的 `progress_data = {}` 分支）。

### 4.4 写入边界校验（`scripts/course_contracts.py`）

- `validate_write_path(raw, course_dir)` 将目标 resolve 后要求必须位于课程目录内，越界返回 `write_outside_course`，文件名以 `.` 开头返回 `hidden_write`；
- `validate_task` 强制 `task_id / agent / course_id / source_files / allowed_writes / must_return / schema_version` 齐全，要求 `source_files` 与 `allowed_writes` 为数组，并对每个写入路径调用上面的边界函数；
- 子 Agent 的授权写入范围由任务信封的 `allowed_writes` 表达，`SKILL.md` 第 6.2 节进一步规定各 Agent 的允许/禁止写入矩阵，索引与进度文件只归 `course-index-manager`。

覆盖证据：`test_course_runtime.py::RuntimeContractTest::test_rejects_write_outside_course` 用 `../escape.md` 断言校验失败。

### 4.5 `course-cn-v2` schema 契约

- `SCHEMA_VERSION = "course-cn-v2"`，任务与返回值都必须携带该版本号，否则 `validate_task` / `validate_result` 报 `schema_version` 错误；
- `RESULT_REQUIRED = {task_id, status, output_files, coverage, warnings, schema_version}`，`STATUSES = {success, needs_review, blocked, failed}`，`RELATION_TYPES` 恰好是阶段 4 的六种白名单关系；
- `course-orchestrator.py` 为每个非 `DONE` 课件生成 `lesson-organizer` 任务信封，写 `.course-runtime.json`（含 `tasks` / `invalid_tasks` / `instruction`），并明确“不执行、不重试、不并发调度 Agent”。

### 4.6 概念去重

- `normalize_name` 做 NFKC、去首尾空白、casefold，并删除空格、下划线、`-`、`–`、`—`，使 `CNN` / `cnn` / `C N N` 归并为同一键；
- `concept_id` 在规范化基础上生成 ≤48 字符的稳定 slug，中文与字母数字保留，其余折叠为 `-`；
- 合并必须写出理由和共同来源，同名异义使用显式上下文后缀，用户修改或锁定卡片只返回建议不覆盖正文。

覆盖证据：`test_course_runtime.py::test_stable_concept_id_and_normalization` 断言 `concept_id(" CNN ") == concept_id("cnn")`。

### 4.7 测试覆盖现状

`python3 -m unittest discover -s tests` 共 69 个测试，覆盖四块：运行时契约与增量状态（`test_course_runtime.py`）、技能完整性/契约文本/脚本语法（`test_skill_integrity.py`）、`source_range` 解析与原文抽取（`test_context_extractor.py`）、双链候选与去重写入（`test_double_link_builder.py`）。测试全部通过是本评估的前提。

---

## 五、风险与已知局限

| 局限 | 具体表现 | 当前缓解 |
|---|---|---|
| PPT/DOCX/HTML 无精确页码 | `context-extractor.py` 只对 PDF（`pypdf`，默认 ±1 页缓冲）与 Markdown/TXT 做精确抽取；PPT/DOCX/HTML 由宿主 Agent 直接读全文，无法给出稳定页号 | `source_range` 允许记录 slide/段落范围，缺失时标 `needs_review`，不伪造页码 |
| 视觉内容依赖 `needs_review` | 公式为图片、图表、动画、speaker notes 无法读取时，Agent 可能高估覆盖 | 账本 `role: needs_review` 与 `status: needs_review` 双标记，并由 `course-reviewer` 与阶段 5 清单核验 |
| 并行能力依赖宿主 | 是否支持子 Agent、能否并行、超时阈值都由客户端决定 | `SKILL.md` 第 12 节给出降级表：不支持时主 Agent 顺序执行、每批 ≤10 篇，且不得省略账本与覆盖清单 |
| 统计口径依赖实际扫描 | 覆盖率、卡片数、双链数若由模型回忆汇报会系统性偏高 | 统一要求用 `course-manifest.py` 扫描结果与脚本解析取数；进度文件禁止写入未经验证的自报统计 |
| 断点恢复未全部脚本化 | `status: filling` 的两种崩溃场景由协议规定，缺少自动检测脚本 | 阶段 5 把“无残留 `.tmp`、无 `draft/filling`”列为硬性检查项 |
| 编排器的 `lesson_id` 只是顺序提示 | `build_tasks` 按扫描顺序生成 `L01…`，且 `REMOVED` 课件同样会进入 `tasks`，与已有 `lesson_order` 的一致性需主 Agent 复核 | `SKILL.md` 第 6.1 节要求主 Agent 建立稳定 `lesson_id` / `lesson_order`，`.course-runtime.json` 仅为信封草案 |
| 概念去重是词面归并 | `normalize_name` 不做语义判断，缩写与全称（如 `CNN` 与“卷积神经网络”）需要 `aliases` 与人工确认 | 合并必须写明理由与共同来源，同名异义强制上下文后缀 |

---

## 六、质量门槛小结（对应 `SKILL.md` 阶段 5）

产物只有同时满足下列检查项，才允许报告 `success`；任一未通过必须先修复：

- [ ] 每个课件都有 `coverage`，且每页状态为 `covered` / `no_knowledge` / `needs_review`；
- [ ] `covered` 条目有非空知识点和有效正整数页码（由 `validate_coverage` 强制）；
- [ ] 主要知识点在课次正文有解释和来源，覆盖清单与阶段 1 账本一致；
- [ ] 卡片结构、案例、引用、思考题完整，无空壳章节；
- [ ] 没有重复卡片、断链、越权文件或用户内容覆盖；
- [ ] 无法确认的图像/公式/视频已标记 `needs_review`；
- [ ] 没有残留 `.tmp` 文件与 `draft` / `filling` 状态。

与代码的对应关系：第 1–2 条由 `course_contracts.validate_coverage` 与 `validate_result` 保证；第 5 条的“越权文件”由 `validate_write_path` 保证；第 7 条为 `course-reviewer` 的固定检查项。第 3、4、6 条依赖子 Agent 的账本与审查，属于协议约束而非脚本强校验，是本评估中最需要人工抽查的部分。

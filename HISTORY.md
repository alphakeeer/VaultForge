# VaultForge 课程版改造记录与失败分析

> 记录课程版从通用主题知识库改造为课程/课次/概念三层模型的过程、失败场景与工程对策。
> 术语与 `SKILL.md` 一致：课次笔记、知识卡片、逐页知识点账本、覆盖清单、`status`、`vf_status`、`allowed_writes`、`source_range`。

---

## 一、失败场景与解决方案

| # | 失败场景 | 原因分析 | 解决方案 |
|---|---|---|---|
| 1 | 生成中途崩溃，把 `.md` 写成半截内容，旧笔记被损坏 | 直接原地覆盖写目标文件，没有事务保护 | 统一原子写：先写 `L02 - 主题.md.tmp` → 校验完整性 → rename 为 `.md`；JSON 侧由 `course_contracts.atomic_json_write` 先写 `.tmp`、回读 `json.loads` 校验、再 `replace`，阶段 5 检查无残留 `.tmp` |
| 2 | 长课程中断后无法判断做到哪一步，只能整门重跑 | 没有持久化状态，笔记没有阶段字段 | 引入状态机：课件级 `NEW/UPDATED/DONE/REMOVED`（hash 判定）+ 文件级 `status: draft/filling/filled/reviewed/needs_review`；重启时扫描 `.course-progress.*` 与 frontmatter 续传 |
| 3 | 子 Agent 写到课程目录之外，或覆盖了别的课次、索引、用户文件 | 任务下发时只有自然语言描述，没有可执行的写入边界 | 任务信封声明 `allowed_writes`，`course_contracts.validate_task` 逐条调用 `validate_write_path`：越出课程目录报 `write_outside_course`，写隐藏文件报 `hidden_write`；`SKILL.md` 第 6.2 节给出每个 Agent 的允许/禁止写入矩阵 |
| 4 | 汇报的“覆盖 24 页 / 生成 5 张卡片”与磁盘实际不符 | 统计数字来自模型回忆或中间推算，存在系统性偏差 | 规定统计必须来自实际文件扫描或子 Agent 的可核验返回值：`course-manifest.py` 输出 `states`，覆盖情况用 `validate_coverage` 校验，双链用实际 `[[wikilink]]` 扫描；禁止把未验证的自报统计写入进度文件 |
| 5 | 课次笔记只有几段总述，把三个知识点“一句带过” | 缺少防漏证据层，模型倾向于压缩输出 | 阶段 1 强制建立逐页知识点账本（`role` / `points` / `evidence` / `note`），阶段 2 必须按账本组织正文；`SKILL.md` 阶段 2 给出正例/反例，用一段总述冒充多个知识点视为未覆盖 |
| 6 | 同一概念在多个课次各建一张卡片（CNN / cnn / C N N） | 各课次并行产出候选，没有统一键 | `normalize_name`（NFKC + casefold + 去除空格/下划线/连字符）与 `concept_id` 稳定 slug 作为唯一键；卡片阶段必须先汇总去重再落盘，同名异义强制上下文后缀（如 `attention-nlp`） |
| 7 | 卡片正文是模型用常识补写的“科普”，却挂着课件页码 | 缺少“只能来自课件”的硬约束与原文锚点 | 强制记录来源文件、课次、页码/slide/段落范围与来源 hash；引用必须是实际摘录；找不到原文就删除伪引用或标 `needs_review`，只提名字的知识点写“课件未展开” |
| 8 | 用户手改过的笔记在增量更新中被覆盖 | 没有区分“机器生成”与“用户内容”，增量默认重写 | `vf_status` 三层保护：`pristine`（可更新）/ `user_modified`（只读）/ `locked`（只读）；冲突时保留用户正文，只在索引或新课次中补链接；`course-reviewer` 核对正文、hash、mtime 未变 |
| 9 | 每轮增量都产出路线图、MOC、更新报告，产物膨胀且互相冲突 | 通用版的路线图/MOC/报告是面向“无结构资料”的，与课次笔记职责重叠 | 课程版删除路线图、每主题 MOC、`Core Questions.md`、争议研究与独立更新报告，改为唯一 `00. 课程索引.md`（目录 + 全课程知识网络 + 卡片索引）；变更历史交给 Git |
| 10 | 一次并行几十个子 Agent，大量超时，用户被拉去手动干预 | 固定并发量未按工作量计算，且无降级路径 | 每个子 Agent 最多处理 10 个课次；超时或返回格式错误只重试该任务（上限 2 次，超限标 `needs_review`）；宿主不支持并行时主 Agent 顺序执行，每批 ≤10 篇，输入输出协议不变 |
| 11 | 卡片写了页码但写不出合法 `source_range`，抽取工具解析失败 | 缺少格式规范与自检 | 固定格式 `source_range: {文件名}:{页码段}`，支持单页 `102`、连续 `12-15`、混合 `12-15, 45-48, 102`、多文件；生成后自检并用 `context-extractor.py` 实际解析，解析失败即视为无效来源 |
| 12 | `.course-progress.json` 手改坏或截断，流程直接报错中断 | 把进度文件当强依赖，没有容错分支 | `course-manifest.py` 捕获 `OSError` / `json.JSONDecodeError` 后退化为空进度，全部课件按 `NEW` 处理并提示“进度文件不可读”，不中断流程；`.course-progress.*` 完全缺失同样视为首次运行 |
| 13 | 覆盖清单宣称全覆盖，但账本里存在缺页，或页面上只有图片被当成已读 | 覆盖状态没有枚举约束，`needs_review` 可被省略 | `coverage` 契约强制每页 `status ∈ {covered, no_knowledge, needs_review}`、`page` 为正整数、非 `no_knowledge` 页必须有非空 `knowledge_points`；只有图片/公式/动画的页必须标 `needs_review`，不得假装覆盖 |
| 14 | `UPDATED` 课件被当成新课件重复生成，或 `DONE` 课件被反复处理 | 只用文件名判断，课件改名或内容微调都会误判 | 以“相对路径 + sha256”双键判定：路径相同 hash 变化为 `UPDATED`，hash 未变为 `DONE`，上次存在本次消失为 `REMOVED`（记录但不静默删除产物）；`DONE` 不生成任务信封 |
| 15 | 并发写入索引导致重复链接行，或卡片反向链接缺失 | 多写者追加同一文件，缺少去重与单写者约定 | 索引与进度只由 `course-index-manager` 单写者维护；关系仅使用六种白名单类型（`prerequisite/component/contrast/extension/application/sequence`），写入前去重，并强制每张卡片至少反向链接一个课次 |
| 16 | 卡片用“结构亲和”候选直接当已确认关系，产生大量无课件依据的连边 | 把候选生成等同于关系判定，缺少证据门槛 | 关系必须有课件依据和理由，仅标题共享词语不得连边；候选只由工具产出，最终由主 Agent 按六种关系白名单确认后写入 |
| 17 | 卡片“相关案例”“原文引用”章节留空或写“待补充”，验收却通过 | 空壳章节没有量化判定，容易被忽略 | 无案例必须写明“课件未提供案例”，材料未覆盖的章节写“课件未覆盖”；阶段 5 把“无空壳章节”列为硬性检查，占位词与空章节计入空壳率 |

### 失败模式的共同根因

把上述 17 条按根因归类，可以看到课程版的改进集中在三个方向：

1. **证据层缺失**（#5、#7、#11、#13、#16、#17）——模型可以“说得像”，但无法证明内容来自课件。对策是引入可核验的中间产物：逐页账本、`coverage` 数组、可解析的 `source_range`、原文摘录。
2. **边界与状态缺失**（#1、#2、#3、#8、#12、#14）——崩溃、并发、增量、用户手改都需要明确的“谁可以写什么、写到哪一步”。对策是事务化写入、状态机、`allowed_writes`、`vf_status`。
3. **度量口径缺失**（#4、#6、#9、#10、#15）——一旦用模型自报或结构估算代替实际扫描，数字与产物都会失真。对策是让所有统计都能由脚本或文件扫描复现。

---

## 二、版本记录

### `course-cn-v1`：从通用主题知识库到课程知识库

改造内容：

- **对象模型重构**：从“主题 → 原子笔记”改为“课程 → 课次 → 概念”三层，稳定 ID 为 `course_id`、`lesson_id`（`L01`、`L02`…）、`lesson_order`、`concept_id`；
- **删除冗余能力**：联网争议研究、`Core Questions.md`、Phase 6 深度研究、双版本路线图 `Learning Roadmap vN`、每主题 MOC、每次增量更新的独立报告；
- **产物收敛为三类**：`00. 课程索引.md`、`01. 课程笔记/Lxx - 主题.md`、`02. 知识卡片/概念.md`，外加 `.course-progress.md` / `.course-progress.json` 两个进度文件；
- **课次笔记保留课件顺序**，并强制 `## 知识点覆盖清单` 与逐页账本一致；
- **仅为可复用或重点概念创建知识卡片**，其余进入 `lesson_only`；
- **增量以课件 hash 判定**，默认不重写历史课次笔记；
- **frontmatter 契约**：`type: lesson | concept`、`lesson_id`、`lesson_order`、`concept_id`、`canonical_name`、`aliases`、`source_file`、`source_hash`、`source_range`、`status`、`vf`、`vf_version: course-cn-v1`、`vf_status`；
- **保留工程能力**：来源溯源、原子写入、断点恢复、用户修改保护。

### `course-cn-v2`：契约层与编排脚本

在 v1 的产物格式之上补齐可执行的运行时契约（`schema_version: course-cn-v2`）：

| 组件 | 职责 | 关键实现 |
|---|---|---|
| `scripts/course_contracts.py` | 稳定 ID、路径安全、任务/返回值/覆盖校验、原子 JSON 写入 | `SCHEMA_VERSION`、`TASK_REQUIRED`、`RESULT_REQUIRED`、`STATUSES`、`RELATION_TYPES`、`normalize_name`、`concept_id`、`validate_write_path`、`validate_task`、`validate_result`、`validate_coverage`、`atomic_json_write` |
| `scripts/course-orchestrator.py` | 为每个非 `DONE` 课件生成 `lesson-organizer` 任务信封并校验写入边界，写入 `.course-runtime.json` | `build_tasks` 产出 `task_id / agent / course_id / lesson_id / source_files / allowed_writes / must_return / schema_version / state`；输出 `tasks`、`invalid_tasks`、`instruction`；明确不执行、不重试、不并发调度 Agent |
| `scripts/course-manifest.py` | 扫描课件 hash 与已有产物，输出增量清单，不写课程目录 | `SOURCE_EXTENSIONS`、`GENERATED_DIRS`、`GENERATED_FILES`、`sha256_file`、`frontmatter`、`scan`；输出 `sources` / `lessons` / `concepts` / `states` / `progress` |
| `.course-runtime.json` | 本次运行的机器可读任务信封 | 由 `course-orchestrator.py` 通过 `atomic_json_write` 生成，主 Agent 据此分发任务 |

v2 同时把“统计来自实际扫描”“无残留 `.tmp`”“每张卡片反向链接课次”等要求写进 `SKILL.md` 质量门槛，并由测试固定下来。

### 契约的验证方式

`python3 -m unittest discover -s tests`（共 69 个测试）把 v2 的关键约定固定为回归项：

- `test_course_runtime.py`：`concept_id(" CNN ") == concept_id("cnn")`；`../escape.md` 被 `validate_write_path` 拒绝；`validate_result` 与 `validate_coverage` 的字段/页码/状态约束；课件 `DONE → UPDATED` 的 hash 判定；
- `test_context_extractor.py`：`source_range` 的单页、连续段、混合段、多文件与空格容错解析，±1 页缓冲的合并与边界，缺源文件时保留页码标签并置空正文，缺 `pypdf` 后端不抛 `NameError`；
- `test_skill_integrity.py`：中文课程模型与质量门槛文本存在、争议研究与额外报告已移除、`Phase 6` 不再出现、四个 Agent 规格存在且均含“输入契约 / 返回格式”、旧 Agent 文件不存在、脚本可编译；
- `test_double_link_builder.py`：六种关系的启发式判定与去重写入、结构亲和过滤、中英文分词与停用词、中英文路线图/辅助文件过滤。

---

## 三、稳定性保障约定

1. **先读后写**：没有完整课件正文或上下文包时返回 `blocked`，禁止凭标题、记忆或摘要补写；
2. **先账本后成文**：逐页知识点账本是防漏证据层，课次笔记的覆盖与顺序以账本为准；
3. **单写者原则**：同一路径同一时间只有一个写者，索引与进度文件只归 `course-index-manager`；
4. **可核验统计**：进度与汇报中的数字必须来自 `course-manifest.py` 等脚本扫描或子 Agent 的可核验返回值；
5. **失败只重试局部**：单个任务失败或超时只重试该任务（≤2 次，超限标 `needs_review`），不盲目重跑整门课程；
6. **诚实失败优先**：任一检查项未通过先修复再汇报，不得用 `success` 掩盖失败，也不得伪造成功率。

---

## 四、未解决问题与后续计划

| 问题 | 现状 | 计划 |
|---|---|---|
| 断点恢复未完全脚本化 | `status: filling` 的两种崩溃场景（有 `.tmp` / 无 `.tmp`）目前是协议要求，没有自动检测脚本 | 增加恢复脚本，扫描 `filling` 文件并自动完成 rename 或标 `filled`，同时把结果并入阶段 0 汇报 |
| 编排器 `lesson_id` 只是顺序提示 | `build_tasks` 按扫描顺序生成 `L01…`，与已有 `lesson_order` 的一致性和 `REMOVED` 课件的处理需要主 Agent 复核 | 让 `course-manifest.py` / `course-orchestrator.py` 读取已有课次笔记的 `lesson_order` 做续号，并对 `REMOVED` 单独输出而不生成写作任务 |
| 概念去重是词面归并 | `normalize_name` 不做语义判断，`CNN` 与“卷积神经网络”依赖 `aliases` 与人工确认 | 引入 `aliases` 前置索引与候选相似度提示（由主 Agent 确认），保持“不自动合并同义”的安全边界 |
| PPT/DOCX/HTML 无精确页码 | 这些格式由宿主 Agent 直接读全文，`source_range` 只能记 slide/段落范围 | 在 `references/templates.md` 中细化各格式的范围写法与自检示例；无法确定范围的条目标 `needs_review` |
| 视觉内容覆盖依赖人工抽查 | 图片公式页只能靠 `needs_review` 标记，脚本难以独立判定 | 在 `course-reviewer` 中固定抽查比例与判定话术，把“正文声称已覆盖但账本为 `needs_review`”列为必须失败项 |
| 并行上限与超时由宿主决定 | `SKILL.md` 只约定“每 Agent ≤10 篇 + 超时只重试该任务”，实际阈值不可控 | 保持协议层约定，记录宿主差异；不改用自适应并发探测，避免重新引入过度工程化 |

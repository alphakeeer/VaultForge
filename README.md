# VaultForge 课程版

> 将课程课件整理为中文 Obsidian 课程知识库。

VaultForge 课程版适用于“每周持续增加课件”的学习场景。它不会把每个 bullet 都拆成一个小文件，而是同时保留两种视角：

- **课次笔记**：严格按课件顺序，完整讲解一节课并检查知识点覆盖；
- **知识卡片**：抽取 CNN、RNN、Attention 等可复用概念，提供更详细的独立解释。

## 输出结构

```text
课程名/
├── 00. 课程索引.md
├── 01. 课程笔记/
│   ├── L01 - 神经网络基础.md
│   └── L02 - CNN.md
├── 02. 知识卡片/
│   ├── CNN.md
│   └── RNN.md
└── .course-progress.md
```

## 工作流

```text
扫描课程与处理记录
  → 识别 NEW / UPDATED / DONE 课件
  → 完整解析新增课件
  → 生成按顺序的课次笔记
  → 抽取并去重概念
  → 新建或合并知识卡片
  → 更新局部和全课程知识网络
  → 轻量验证并记录进度
```

新增课件只影响新增课次和受影响的知识卡片，不会默认重写历史课程笔记。用户修改过或锁定的文件不会被自动覆盖。

## 安装

将仓库放入 Agent Skills 目录：

```bash
git clone https://github.com/alphakeeer/VaultForge.git ~/.agents/skills/VaultForge
```

需要 Python 3。PDF 精确页码抽取建议安装：

```bash
pip install pypdf
```

将 `SKILL.md` 作为 Agent Skill 加载，然后用中文说明课程目录和课件处理需求。

## 支持格式

- PDF：支持按页码范围抽取；
- PPT / PPTX：由宿主 Agent 读取幻灯片内容并记录 slide 范围；
- Markdown / TXT：支持全文抽取；
- Word / HTML：由宿主 Agent 读取全文。

## 设计取舍

课程版已移除以下通用知识库功能：

- 联网争议研究、共识与观点分析；
- 每个主题单独的 MOC；
- 双版本路线图；
- 每次增量更新的独立报告；
- 以“一个 bullet 一个原子笔记”为默认规则。

保留的工程能力包括来源溯源、断点恢复、原子写入、增量扫描、概念去重和用户修改保护。

## 开发

```bash
cd VaultForge
python3 -m unittest discover -s tests -v
```

本地定制分支：`course-cn-v1`。原始仓库配置为 `upstream`，个人 Fork 配置为 `origin`。


# 兼容性说明

VaultForge 课程版面向支持 Markdown 文件读写和 Agent Skill 加载的客户端。

## 文件格式

- PDF：由 `scripts/context-extractor.py` 按页码抽取，需要 `pypdf`；
- PPT/PPTX：由宿主 Agent 读取幻灯片，记录 slide 范围；
- Markdown/TXT：可全文抽取；
- DOCX/HTML：由宿主 Agent 读取全文。

## 能力降级

如果客户端不支持并行 Agent，课次和卡片按顺序执行，每批最多 10 个文件。如果 PDF 后端不可用，必须回退到原始课件全文，不能使用摘要或索引替代原文。

课程版不依赖联网搜索、Firecrawl、Exa 或 Phase 6 研究能力。


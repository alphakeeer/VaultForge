# 课程版模板

## 课程索引

```markdown
# {课程名}
## 课程目标
## 课程目录
1. [[L01 - {主题}]]
## 全课程知识网络
## 知识卡片索引
```

## 课次笔记

```markdown
---
type: lesson
course_id: {course_id}
lesson_id: L01
lesson_order: 1
source_file: {file}
source_hash: sha256:{hash}
status: reviewed
vf: true
vf_version: course-cn-v1
vf_status: pristine
---

# L01 - {主题}
## 本节学习目标
## 按课件顺序讲解
## 知识点覆盖清单
## 本节知识网络
## 关键公式与例子
## 本节知识卡片
## 来源与页码
```

## 知识卡片

```markdown
---
type: concept
course_id: {course_id}
concept_id: {stable_id}
canonical_name: {name}
aliases: []
source_lessons: [L01]
status: reviewed
vf: true
vf_version: course-cn-v1
vf_status: pristine
---

# {name}
## 一句话定义
## 要解决的问题
## 核心机制
## 工作过程
## 关键公式或直觉
## 常见变体与边界
## 与其他概念的关系
## 在课程中的出现位置
## 来源与原文引用
## 自测问题
```


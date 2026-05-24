# Java面试助手

基于 RAG（检索增强生成）的 Java 面试问答系统。

## ✨ 功能特点
- 基于 5 份 Java 面试文档（297 条知识片段）构建知识库
- 使用 ChromaDB 向量检索 + 通义千问 Embedding API
- 答案严格基于文档，可追溯来源，有效解决大模型幻觉问题
- 支持命令行和 Web 双交互模式

## 🛠️ 技术栈
- Python 3.13
- ChromaDB（向量数据库）
- 通义千问 Qwen-Plus（LLM）
- Streamlit（Web 界面）

## 🚀 快速开始

### 安装依赖
```bash
pip install pandas chromadb openai streamlit
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
```

### 运行
```bash
# 命令行版
python knowledge_bot_v2.py

# Web 版
streamlit run app.py
```
## 📸 效果演示

![p1](https://zhd-blog.oss-cn-beijing.aliyuncs.com/p1.png)

![p2](https://zhd-blog.oss-cn-beijing.aliyuncs.com/p2.png)

![p3](https://zhd-blog.oss-cn-beijing.aliyuncs.com/p3.png)
## 📄 项目结构
```
├── knowledge_base.csv    # 知识库数据（297条）
├── knowledge_bot_v2.py   # 命令行版主程序
├── app.py                # Web 版主程序
└── chroma_db/            # 向量索引（自动生成）
```
## 👤 作者
- GitHub: @zhd8528
## 📝 许可证
- MIT
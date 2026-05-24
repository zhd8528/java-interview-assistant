import pandas as pd
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from openai import OpenAI
import hashlib
import time

# ==================== 配置 ====================
API_KEY = "写你自己的key，我用的是千问"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen-plus"
EMBEDDING_MODEL = "text-embedding-v3"

CSV_PATH = "knowledge_base.csv"

# ==================== 自定义 Embedding 函数 ====================
class DashScopeEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str, base_url: str, model: str = EMBEDDING_MODEL):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def __call__(self, texts: Documents) -> Embeddings:
        """调用 DashScope 的 embedding API，每次最多处理 10 条"""
        try:
            # API 限制：一次最多 10 条
            if len(texts) > 10:
                raise ValueError(f"Batch size {len(texts)} exceeds API limit 10")
            
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            embeddings = [item.embedding for item in response.data]
            return embeddings
        except Exception as e:
            print(f"Embedding 调用失败: {e}")
            raise

# ==================== 1. 读取知识库 ====================
print("📚 正在加载知识库...")
df = pd.read_csv(CSV_PATH)

print(f"✅ 加载完成，共 {len(df)} 条知识片段")
print(f"📋 列名: {df.columns.tolist()}")
print(f"📝 第一条内容预览:\n{df['content'].iloc[0][:200]}...")

# ==================== 2. 构建向量索引 ====================
print("\n🔧 正在构建向量索引（使用云端 Embedding API）...")

client_chroma = chromadb.PersistentClient(path="./chroma_db")

embedding_fn = DashScopeEmbeddingFunction(API_KEY, BASE_URL)

# 删除旧集合
try:
    client_chroma.delete_collection("java_knowledge")
    print("  已删除旧集合")
except:
    pass

# 创建新集合
collection = client_chroma.create_collection(
    name="java_knowledge",
    embedding_function=embedding_fn
)

# 分批添加 - 每批 5 条，API 限制是 10，用 5 更稳定
batch_size = 5
success_count = 0

for i in range(0, len(df), batch_size):
    batch = df.iloc[i:i+batch_size]
    
    # 生成唯一ID
    ids = []
    for idx, (_, row) in enumerate(batch.iterrows()):
        doc_name = row.get('document_name', 'doc')
        chunk_idx = row.get('chunk_index', idx)
        unique_str = f"{doc_name}_{chunk_idx}_{i}_{idx}"
        ids.append(hashlib.md5(unique_str.encode()).hexdigest())
    
    documents = batch['content'].tolist()
    metadatas = [{"source": row.get('document_name', '未知')} for _, row in batch.iterrows()]
    
    # 重试机制
    max_retries = 3
    for retry in range(max_retries):
        try:
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            success_count += len(batch)
            print(f"  已添加 {success_count}/{len(df)} 条")
            time.sleep(0.5)  # 避免请求过快
            break
        except Exception as e:
            print(f"  批次 {i//batch_size + 1} 失败，重试 {retry+1}/{max_retries}: {str(e)[:100]}")
            time.sleep(2)
            if retry == max_retries - 1:
                print(f"  跳过该批次")

print(f"\n✅ 向量索引构建完成，成功添加 {success_count}/{len(df)} 条")

# ==================== 3. 初始化 LLM 客户端 ====================
client_llm = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

# ==================== 4. 问答函数 ====================
def ask(question: str, top_k: int = 3):
    """基于知识库回答问题"""
    print(f"\n🤔 问题: {question}")
    
    # 检索相关片段
    try:
        results = collection.query(
            query_texts=[question],
            n_results=top_k
        )
    except Exception as e:
        print(f"❌ 检索失败: {e}")
        return
    
    if not results['documents'] or len(results['documents'][0]) == 0:
        print("❌ 未找到相关知识")
        return
    
    # 组装上下文
    context_parts = []
    sources = []
    for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        doc_preview = doc[:800] + "..." if len(doc) > 800 else doc
        context_parts.append(f"【片段{i+1}】{doc_preview}")
        sources.append(meta.get('source', '未知来源'))
    
    context = "\n\n".join(context_parts)
    
    system_prompt = """你是一个Java面试助手。请严格基于下面提供的【知识内容】回答问题。
要求：
1. 每个要点用1-2句话简要解释
2. 保持分点格式，语言口语化，适合面试口述
3. 如果知识库中没有相关信息，请直接说"知识库中没有找到相关内容"
4. 绝对不要编造知识库以外的信息"""
    
    user_prompt = f"""【知识内容】
{context}

【用户问题】
{question}"""
    
    try:
        response = client_llm.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
    except Exception as e:
        print(f"❌ LLM 调用失败: {e}")
        return
    
    answer = response.choices[0].message.content
    
    print(f"💡 答案:\n{answer}")
    print(f"\n📖 参考来源: {', '.join(set(sources))}")
    return answer

# ==================== 5. 交互模式 ====================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🤖 Java面试助手已启动")
    print("输入 'quit' 或 'exit' 退出")
    print("="*50)
    
    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 再见！")
            break
        if not user_input:
            continue
        
        ask(user_input)
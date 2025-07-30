import uuid
import json
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
import re

# Import embedding functionality
from Embedding import get_embp_embedding, parser_Message

class MemoryNode:
    """
    Represents a single node in the semantic memory tree.
    Each node contains a piece of summarized information, its embedding vector,
    keywords, and links to its children.
    """
    def __init__(self, summary: str, embedding: Optional[List[float]] = None, children: Optional[List['MemoryNode']] = None, keywords: Optional[List[str]] = None, keywords_embedding: Optional[List[float]] = None):
        self.node_id: str = str(uuid.uuid4())
        self.timestamp: datetime = datetime.utcnow()
        self.summary: str = summary
        # 优化：不再存储摘要embedding，只保存关键词embedding
        self.embedding: Optional[List[float]] = []  # 废弃摘要embedding，为兼容性保留字段
        self.keywords: List[str] = keywords if keywords is not None else []  # 关键词列表
        self.keywords_embedding: Optional[List[float]] = keywords_embedding if keywords_embedding is not None else []  # 关键词embedding
        self.children: List['MemoryNode'] = children if children is not None else []

    def __repr__(self) -> str:
        return f"MemoryNode(id={self.node_id}, summary='{self.summary[:30]}...', children={len(self.children)})"

    def add_child(self, child_node: 'MemoryNode'):
        """Adds a child node to this node."""
        self.children.append(child_node)

    def remove_child(self, node_id: str) -> bool:
        """Removes a child node by its ID."""
        initial_len = len(self.children)
        self.children = [child for child in self.children if child.node_id != node_id]
        return len(self.children) < initial_len

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the node to a dictionary."""
        return {
            "node_id": self.node_id,
            "timestamp": self.timestamp.isoformat(),
            "summary": self.summary,
            "embedding": [],  # 不再保存摘要embedding
            "keywords": self.keywords,
            "keywords_embedding": self.keywords_embedding,
            "children": [child.to_dict() for child in self.children]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryNode':
        """Creates a node from a dictionary."""
        # Note: datetime.fromisoformat can't parse UTC 'Z' suffix in some Python versions, so we handle it manually.
        ts_str = data['timestamp'].replace('Z', '+00:00')
        node = cls(
            summary=data['summary'], 
            embedding=[],  # 不再加载摘要embedding
            keywords=data.get('keywords', []),
            keywords_embedding=data.get('keywords_embedding', [])
        )
        node.node_id = data['node_id']
        node.timestamp = datetime.fromisoformat(ts_str)
        node.children = [cls.from_dict(child_data) for child_data in data['children']]
        return node

class MemoryTree:
    """
    Manages the entire semantic memory structure.
    This class is responsible for building, searching, and persisting the memory tree.
    """
    def __init__(self, root: MemoryNode = None, embedding_config: Dict[str, str] = None):
        if root:
            self.root = root
        else:
            self.root = MemoryNode(summary="Robot's Core Memory")
        
        # Embedding configuration (using default values from Embedding.py)
        self.embedding_config = embedding_config or {
            'APPID': 'b32f165e',
            'APISecret': 'MmJiZjQ0NTIzOTdhOWU0ZWY5ZjUyNzI0',
            'APIKEY': 'bf4caffa0bd087acc04cd63d0ee27fc5'
        }
        
        # Conversation session management
        self.current_conversation = []  # Stores current conversation turns
        self.conversation_threshold = 5  # Number of turns before considering summarization

    def _extract_keywords_fast(self, text: str, max_keywords: int = 6) -> List[str]:
        """
        快速提取用户输入的关键词（用于实时检索）
        逻辑：删除停用词和标点符号后，保留有意义的词组
        """
        if not text:
            return []
        
        # 定义停用词库
        stop_words = {
            '的', '了', '在', '是', '有', '和', '就', '不', '都', '一', '一个', '上', '也', '很', '到', 
            '说', '要', '去', '会', '着', '没有', '看', '好', '这', '那', '还', '把', '做', '让', '给',
            '我', '你', '他', '她', '我们', '你们', '他们', '自己',
            '啊', '呢', '吧', '哦', '嗯', '么', '吗', '啦',
            '非常', '特别', '太', '比较', '其实', '突然',
            '什么', '怎么', '为什么', '谁', '哪里', '多少', '怎样', '如何', '怎么回事', '从哪里',
            '今天', '明天', '周末', '现在', '早上', '晚上', '这里', '那里', '附近',
            '用户', '对话', '交流', '聊天', '询问', '回答', '提到', '表示', '认为', '觉得', '请问', '听说', '记得', '要求',
            '这个', '那个', '一些', '几次', '一天', '一起', '得', '点', '但', '真的', '已经', '可以', '想',
            '还是', '只是', '应该', '大概', '也许', '可能', '如果', '然后', '不过', '因为', '所以', '但是', '而且', '或者', '还有',
            '时候', '之后', '之前', '刚才', '正在', '总是', '经常', '每次', '一直', '马上', '快点', '慢慢', '几乎', '完全',
            '挺', '稍微', '有点', '更加', '越来越', '最好', '必须', '一定', '不用', '不能', '不要', '再来', '再来一次',
            '一下', '一会儿', '先', '后', '再', '又', '这样', '那样', '这么', '那么', '怎么样', '什么样', '这种', '那种',
            '其他', '另外', '全部', '整个', '每个', '各位', '大家', '所有人', '一切', '所有', '任何', '某', '某些', '某个', '某位', '某事', '某物',
            '别人', '人家', '本人', '对方', '双方', '彼此', '之间', '其中', '当中', '中间', '之内', '之外',
            '以上', '以下', '以内', '以外', '前面', '后面', '左边', '右边', '旁边', '对面', '周围', '附近', '之中',
            '刚', '刚从', '回来', '真', '真是', '美', '美了'
        }
        
        import re
        
        # 先移除标点符号，替换为空格
        text_cleaned = re.sub(r'[！。，、；：？""''（）【】《》]', ' ', text)
        
        # 简化策略：直接移除停用词，然后提取连续的中文词组
        result_text = text_cleaned
        for stop_word in sorted(stop_words, key=len, reverse=True):
            result_text = result_text.replace(stop_word, ' ')
        
        # 按空格分割并清理
        parts = result_text.split()
        keywords = []
        
        for part in parts:
            part = part.strip()
            # 保留包含中文字符、长度≥2的部分
            if part and len(part) >= 2 and re.search(r'[\u4e00-\u9fff]', part):
                keywords.append(part)
        
        # 去重保持顺序
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords[:max_keywords]
    
    def _extract_keywords_with_llm(self, text: str, llm_client, max_keywords: int = 3) -> List[str]:
        """
        使用LLM提取记忆点的精准关键词（用于记忆存储）
        追求准确性和精简性，不在乎时间
        """
        if not text or not llm_client:
            return self._extract_keywords_fast(text, max_keywords)  # 降级处理
        
        prompt = (
            f"从以下文本中提取{max_keywords}个最重要的关键词。要求：\n"
            "1. 只返回名词、动词、形容词等实词\n"
            "2. 不要助词、副词、语气词\n"
            "3. 优先选择能概括主要内容的词汇\n"
            "4. 每个关键词2-6个字符\n"
            "5. e.g. 陆李昕最近去云南大理旅游，特别喜欢洱海的日落的关键词为：云南大理，旅游，洱海，日落，喜欢\n"
            "6. 只返回关键词，用逗号分隔，不要其他解释\n\n"
            f"文本：{text}\n\n"
            "关键词："
        )
        
        try:
            response = llm_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # 低随机性，保证稳定输出
                max_tokens=50
            )
            
            keywords_text = response.choices[0].message.content.strip()
            # 解析逗号分隔的关键词
            keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
            
            # 过滤和验证
            valid_keywords = []
            for kw in keywords:
                # 只保留中文关键词，2-6个字符
                if re.match(r'^[\u4e00-\u9fff]{2,6}$', kw):
                    valid_keywords.append(kw)
            
            return valid_keywords[:max_keywords]
            
        except Exception as e:
            print(f"LLM关键词提取失败: {e}，使用快速方法")
            return self._extract_keywords_fast(text, max_keywords)
    
    def _extract_keywords(self, text: str, max_keywords: int = 8) -> List[str]:
        """
        兼容性方法，默认使用快速提取（为了保持向后兼容）
        """
        return self._extract_keywords_fast(text, max_keywords)
    
    def _generate_embedding(self, text: str, max_retries: int = 3) -> List[float]:
        """
        Generate embedding vector for given text using the configured embedding service.
        Includes retry mechanism for better reliability.
        """
        import time
        
        for attempt in range(max_retries):
            try:
                desc = {"messages": [{"content": text, "role": "user"}]}
                response = get_embp_embedding(
                    desc, 
                    appid=self.embedding_config['APPID'],
                    apikey=self.embedding_config['APIKEY'],
                    apisecret=self.embedding_config['APISecret']
                )
                embedding_vector = parser_Message(response)
                result = embedding_vector.tolist() if hasattr(embedding_vector, 'tolist') else list(embedding_vector)
                
                # 验证embedding是否有效
                if result and len(result) > 0:
                    # print(f"成功生成embedding，维度: {len(result)}")  # 减少输出
                    return result
                else:
                    print(f"Embedding为空，尝试重试 (第{attempt + 1}次)")
                    
            except Exception as e:
                print(f"Error generating embedding (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print(f"等待2秒后重试...")
                    time.sleep(2)  # 等待后重试
                    
        print(f"生成embedding失败，已重试{max_retries}次，记忆点将不包含embedding")
        return []
    
    def _generate_batch_embeddings(self, texts: List[str], max_retries: int = 3) -> List[List[float]]:
        """
        批量生成embedding向量，提高效率
        暂时使用逐一生成，未来可优化为真正的批处理
        """
        results = []
        for text in texts:
            if text.strip():  # 跳过空文本
                embedding = self._generate_embedding(text, max_retries)
                results.append(embedding)
            else:
                results.append([])
        return results
    
    def repair_missing_embeddings(self):
        """
        修复缺失embedding的记忆点
        """
        print("开始检查和修复缺失的embedding...")
        
        def _traverse_and_repair(node: MemoryNode, level: int = 0):
            repaired_count = 0
            
            # 跳过root节点
            if node.summary != "Robot's Core Memory":
                # 检查是否缺少关键词embedding
                if node.keywords and (not node.keywords_embedding or len(node.keywords_embedding) == 0):
                    # print(f"发现缺失关键词embedding的节点: {node.summary[:50]}...")  # 减少输出
                    keywords_text = " ".join(node.keywords)
                    new_keywords_embedding = self._generate_embedding(keywords_text)
                    if new_keywords_embedding:
                        node.keywords_embedding = new_keywords_embedding
                        repaired_count += 1
                        # print(f"✓ 已修复关键词embedding")  # 减少输出
                    else:
                        print(f"✗ 修复关键词embedding失败")
            
            # 递归处理子节点
            for child in node.children:
                repaired_count += _traverse_and_repair(child, level + 1)
            
            return repaired_count
        
        total_repaired = _traverse_and_repair(self.root)
        print(f"修复完成，共修复了 {total_repaired} 个记忆点的embedding")
        return total_repaired
    
    def add_conversation_turn(self, user_input: str, assistant_response: str):
        """
        Add a single turn of conversation to current session.
        """
        self.current_conversation.append({
            'user': user_input,
            'assistant': assistant_response,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Check if conversation should be summarized and stored
        if len(self.current_conversation) >= self.conversation_threshold:
            print(f"Conversation reached {self.conversation_threshold} turns, considering summarization...")
            return True  # Signal that conversation might be ready for summarization
        return False

    def finalize_conversation(self, llm_client=None, person_name: str = ""):
        """
        End current conversation session and convert it to multiple memory points.
        Uses LLM to extract specific memory points from the conversation.
        """
        if not self.current_conversation:
            print("No conversation to finalize.")
            return []
            
        # Format conversation for memory extraction
        conversation_text = ""
        for turn in self.current_conversation:
            conversation_text += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
        
        # Extract memory points using LLM if provided
        if llm_client:
            memory_points = self._extract_memory_points_with_llm(conversation_text, llm_client, person_name)
        else:
            # Fallback: create simple memory points
            memory_points = [f"Conversation with {person_name}: {conversation_text[:100]}..."]
        
        # Create memory nodes for each memory point with keywords and embeddings
        memory_nodes = []
        
        # 为记忆点生成精准关键词（使用LLM）和关键词embedding
        for memory_point in memory_points:
            # 使用LLM生成精准关键词
            keywords = self._extract_keywords_with_llm(memory_point, llm_client, max_keywords=5)
            
            # 将人物姓名作为第一个关键词
            if person_name and person_name not in keywords:
                keywords.insert(0, person_name)
            
            # 生成关键词embedding
            keywords_text = " ".join(keywords) if keywords else ""
            keywords_embedding = self._generate_embedding(keywords_text) if keywords_text else []
            
            memory_node = MemoryNode(
                summary=memory_point,
                embedding=[],  # 不再生成摘要embedding
                keywords=keywords,
                keywords_embedding=keywords_embedding
            )
            
            # Add to tree (attach to root for now)
            self.root.add_child(memory_node)
            memory_nodes.append(memory_node)
            
            print(f"创建记忆点: {memory_point}")
            # print(f"  LLM生成关键词: {', '.join(memory_node.keywords)}")
        
        # Clear current conversation
        self.current_conversation = []
        
        print(f"对话已分解为 {len(memory_nodes)} 个记忆点并保存")
        return memory_nodes

    def _extract_memory_points_with_llm(self, conversation_text: str, llm_client, person_name: str) -> List[str]:
        """
        Use LLM to extract specific, actionable memory points from the conversation.
        Each memory point should be a discrete piece of information worth remembering.
        """
        prompt = (
            f"请分析以下与{person_name}的对话，提取出具体的、值得记住的记忆点。\n"
            "每个记忆点应该是独立的、具体的信息，比如：\n"
            "- '{person_name}喜欢摄影，特别是风景摄影'\n"
            "- '给{person_name}推荐了索尼A7相机'\n"
            "- '{person_name}提到他在学习Python编程'\n"
            "- '{person_name}对机器学习很感兴趣但觉得有难度'\n\n"
            "要求：\n"
            "1. 每个记忆点都要具体明确\n"
            "2. 包含人物、事件、偏好、状态等信息\n"
            "3. 每行一个记忆点\n"
            "4. 不要总结性语言，要具体的事实\n"
            "5. 如果对话内容不多，至少提取2-3个记忆点\n\n"
            f"对话内容:\n{conversation_text}\n\n"
            "记忆点列表（每行一个）:"
        )
        
        try:
            response = llm_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3  # 降低随机性，确保输出稳定
            )
            
            # 解析LLM输出，每行一个记忆点
            memory_points_text = response.choices[0].message.content.strip()
            memory_points = []
            
            for line in memory_points_text.split('\n'):
                line = line.strip()
                # 移除可能的序号或符号
                if line and not line.startswith('#'):
                    # 移除开头的数字、点号、破折号等
                    cleaned_line = line.lstrip('0123456789.-• ').strip()
                    if cleaned_line:
                        memory_points.append(cleaned_line)
            
            # 确保至少有一些记忆点
            if not memory_points:
                memory_points = [f"与{person_name}进行了对话交流"]
                
            return memory_points
            
        except Exception as e:
            print(f"Error extracting memory points with LLM: {e}")
            # 降级处理：基于对话轮次创建简单记忆点
            fallback_points = []
            for turn in self.current_conversation:
                if len(turn['user']) > 10:  # 过滤太短的输入
                    fallback_points.append(f"{person_name}说: {turn['user'][:50]}...")
            return fallback_points or [f"与{person_name}进行了对话交流"]

    def add_memory(self, text: str, parent_node_id: Optional[str] = None):
        """
        Processes a new piece of text, creates a memory node with keywords, and adds it to the tree.
        """
        # 1. Use the text as summary directly (or could add LLM summarization here)
        summary = text
        
        # 2. Extract keywords
        keywords = self._extract_keywords(summary)
        
        # 3. Generate embeddings for both summary and keywords
        summary_embedding = self._generate_embedding(summary)
        keywords_text = " ".join(keywords) if keywords else ""
        keywords_embedding = self._generate_embedding(keywords_text) if keywords_text else []

        new_node = MemoryNode(
            summary=summary, 
            embedding=summary_embedding,
            keywords=keywords,
            keywords_embedding=keywords_embedding
        )

        # 4. Find the parent node to attach to (or attach to root)
        parent = self.find_node(parent_node_id) if parent_node_id else self.root
        if parent:
            parent.add_child(new_node)
        else:
            # If specified parent isn't found, attach to root as a fallback
            self.root.add_child(new_node)
        
        return new_node

    def find_node(self, node_id: str, node: MemoryNode = None) -> Optional[MemoryNode]:
        """Recursively finds a node by its ID in the tree."""
        if node is None:
            node = self.root

        if node.node_id == node_id:
            return node
        
        for child in node.children:
            found = self.find_node(node_id, child)
            if found:
                return found
        return None

    def find_parent(self, child_id: str, node: MemoryNode = None) -> Optional[MemoryNode]:
        """Recursively finds the parent of a node by the child's ID."""
        if node is None:
            node = self.root

        for child in node.children:
            if child.node_id == child_id:
                return node
            found_parent = self.find_parent(child_id, child)
            if found_parent:
                return found_parent
        return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculates cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm_a = sum(a * a for a in vec1) ** 0.5
        norm_b = sum(b * b for b in vec2) ** 0.5
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)

    def _calculate_memory_decay(self, node: MemoryNode) -> float:
        """
        Calculate memory decay factor based on age.
        Newer memories have higher probability of being retrieved.
        """
        now = datetime.utcnow()
        age_days = (now - node.timestamp).days
        
        # Exponential decay: newer memories have higher retrieval probability
        # decay_factor decreases as age increases
        decay_factor = max(0.1, 0.95 ** age_days)  # Minimum 0.1, starts at 0.95
        return decay_factor

    def search(self, query_text: str, similarity_threshold: float = 0.6, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        优化后的关键词单层检索：只使用关键词 embedding 进行匹配
        提高检索速度，减少存储和计算开销
        """
        # print(f"Searching for: {query_text}")
        
        # 1. 使用快速方法提取查询关键词（用户输入，追求速度）
        query_keywords = self._extract_keywords_fast(query_text, max_keywords=6)
        print(f"Query keywords: {', '.join(query_keywords)}")
        
        if not query_keywords:
            print("No keywords extracted from query")
            return []
        
        # 2. 生成查询关键词的embedding
        query_keywords_text = " ".join(query_keywords)
        query_keywords_embedding = self._generate_embedding(query_keywords_text)
        
        if not query_keywords_embedding:
            print("Failed to generate query keywords embedding")
            return []
        
        # 3. 只使用关键词进行检索
        candidate_nodes = []
        self._keywords_only_search(
            self.root, 
            query_keywords_embedding,
            similarity_threshold, 
            candidate_nodes, 
            level=0
        )
        
        # 4. 计算最终得分（只基于关键词相似度 + 时间衰减）
        for candidate in candidate_nodes:
            node = candidate['node']
            keywords_similarity = candidate['keywords_similarity']
            decay_factor = self._calculate_memory_decay(node)
            
            # 只使用关键词相似度
            candidate['final_score'] = keywords_similarity * decay_factor
            candidate['decay_factor'] = decay_factor
        
        # 按最终得分排序
        candidate_nodes.sort(key=lambda x: x['final_score'], reverse=True)
        
        # 5. 返回结果（只返回摘要和时间，不返回embedding）
        results = []
        for candidate in candidate_nodes[:max_results]:
            results.append({
                'node_id': candidate['node'].node_id,
                'summary': candidate['node'].summary,
                'keywords': candidate['node'].keywords,
                'similarity': candidate['keywords_similarity'],  # 修改为单一相似度
                'decay_factor': candidate['decay_factor'],
                'final_score': candidate['final_score'],
                'timestamp': candidate['node'].timestamp.isoformat()
            })
        
        print(f"Found {len(results)} relevant memories")
        # for i, result in enumerate(results):
        #     print(f"  {i+1}. {result['summary'][:50]}... "
        #           f"(keywords: {result['similarity']:.3f}, "
        #           f"final: {result['final_score']:.3f})")
        
        return results
    
    def _keywords_only_search(self, node: MemoryNode, query_keywords_embedding: List[float], 
                             similarity_threshold: float, candidates: List[Dict], level: int = 0):
        """
        优化的关键词单层搜索 - 只使用关键词embedding进行匹配
        """
        # Skip root node (it's just a placeholder)
        if node.summary == "Robot's Core Memory":
            # Traverse children of root
            for child in node.children:
                self._keywords_only_search(
                    child, query_keywords_embedding, similarity_threshold, candidates, level
                )
            return
        
        # 只计算关键词相似度
        keywords_similarity = 0.0
        
        # 关键词相似度匹配
        if node.keywords_embedding and query_keywords_embedding:
            keywords_similarity = self._cosine_similarity(query_keywords_embedding, node.keywords_embedding)
        
        # 如果关键词相似度达到阈值，则加入候选结果
        if keywords_similarity >= similarity_threshold:
            candidates.append({
                'node': node,
                'keywords_similarity': keywords_similarity,
                'level': level
            })
            # print(f"  Found candidate at level {level}: {node.summary[:50]}... "
                #   f"(keywords: {keywords_similarity:.3f})")
            
            # 如果当前节点相似度很高，继续搜索子节点
            if keywords_similarity > 0.8:  # 高相似度阈值
                for child in node.children:
                    self._keywords_only_search(
                        child, query_keywords_embedding, similarity_threshold, candidates, level + 1
                    )
        
        # 即使当前节点不满足阈值，也探索子节点（但限制深度）
        elif node.children and level < 3:  # 限制搜索深度
            for child in node.children:
                self._keywords_only_search(
                    child, query_keywords_embedding, similarity_threshold, candidates, level + 1
                )
    
    def _enhanced_dfs_search(self, node: MemoryNode, query_summary_embedding: List[float], 
                           query_keywords_embedding: List[float], similarity_threshold: float, 
                           candidates: List[Dict], level: int = 0):
        """
        兼容性方法：保留原有的双层搜索（为了向后兼容）
        但实际上已经被新的关键词单层搜索替代
        """
        # Skip root node (it's just a placeholder)
        if node.summary == "Robot's Core Memory":
            # Traverse children of root
            for child in node.children:
                self._enhanced_dfs_search(
                    child, query_summary_embedding, query_keywords_embedding,
                    similarity_threshold, candidates, level
                )
            return
        
        # Calculate similarities
        keywords_similarity = 0.0
        summary_similarity = 0.0
        
        # Keywords similarity (fast filtering)
        if node.keywords_embedding and query_keywords_embedding:
            keywords_similarity = self._cosine_similarity(query_keywords_embedding, node.keywords_embedding)
        
        # Summary similarity (precise matching)
        if node.embedding:
            summary_similarity = self._cosine_similarity(query_summary_embedding, node.embedding)
        
        # Adaptive threshold: keywords for coarse filtering
        keywords_threshold = max(0.3, similarity_threshold - 0.2)  # Lower threshold for keywords
        
        # If keywords pass the coarse filter, check summary similarity
        if keywords_similarity >= keywords_threshold or summary_similarity >= similarity_threshold:
            # Composite similarity for final filtering
            composite_similarity = 0.4 * keywords_similarity + 0.6 * summary_similarity
            
            if composite_similarity >= similarity_threshold:
                candidates.append({
                    'node': node,
                    'keywords_similarity': keywords_similarity,
                    'summary_similarity': summary_similarity,
                    'level': level
                })
                print(f"  Found candidate at level {level}: {node.summary[:50]}... "
                      f"(kw: {keywords_similarity:.3f}, sum: {summary_similarity:.3f})")
                
                # Continue searching children if current node has high similarity
                if composite_similarity > 0.8:  # High similarity threshold for continuing
                    for child in node.children:
                        self._enhanced_dfs_search(
                            child, query_summary_embedding, query_keywords_embedding,
                            similarity_threshold, candidates, level + 1
                        )
            
            # Even if node doesn't meet threshold, still explore children (dynamic planning)
            elif node.children and level < 3:  # Limit search depth
                for child in node.children:
                    self._enhanced_dfs_search(
                        child, query_summary_embedding, query_keywords_embedding,
                        similarity_threshold, candidates, level + 1
                    )
    
    def check_conversation_end(self, user_input: str, llm_client) -> bool:
        """
        Use LLM to determine if the conversation should end.
        Returns True if conversation should end, False otherwise.
        """
        # Create a prompt to ask the LLM if the conversation seems to be ending
        recent_turns = self.current_conversation[-3:] if len(self.current_conversation) >= 3 else self.current_conversation
        conversation_context = ""
        for turn in recent_turns:
            conversation_context += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
        
        prompt = (
            "Based on the recent conversation turns and the latest user input, "
            "determine if this conversation appears to be ending or if the user is saying goodbye. "
            "Respond with exactly 'END' if the conversation should end, or 'CONTINUE' if it should continue.\n\n"
            f"Recent conversation:\n{conversation_context}\n"
            f"Latest user input: {user_input}\n\n"
            "Decision (END or CONTINUE):"
        )
        
        try:
            response = llm_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10
            )
            decision = response.choices[0].message.content.strip().upper()
            return decision == 'END'
        except Exception as e:
            print(f"Error checking conversation end: {e}")
            return False

    def save(self, file_path: str):
        """Saves the entire memory tree to a JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.root.to_dict(), f, ensure_ascii=False, indent=4)
        print(f"MemoryTree saved to {file_path}")

    @staticmethod
    def load(file_path: str, embedding_config: Dict[str, str] = None) -> 'MemoryTree':
        """Loads a memory tree from a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                root_node = MemoryNode.from_dict(data)
                tree = MemoryTree(root=root_node, embedding_config=embedding_config)
                print(f"MemoryTree loaded from {file_path}")
                return tree
        except FileNotFoundError:
            print(f"No memory file found at {file_path}. Creating a new MemoryTree.")
            return MemoryTree(embedding_config=embedding_config)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error reading or parsing JSON from {file_path}: {e}. Creating a new MemoryTree.")
            return MemoryTree(embedding_config=embedding_config)
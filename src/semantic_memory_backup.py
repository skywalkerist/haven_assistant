import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
import re

# Import embedding functionality
from Embedding import get_embp_embedding, parser_Message
import json

class MemoryNode:
    """
    Represents a single node in the semantic memory tree.
    Each node contains a piece of summarized information, its embedding vector,
    and links to its children.
    """
    def __init__(self, summary: str, embedding: Optional[List[float]] = None, children: Optional[List['MemoryNode']] = None, keywords: Optional[List[str]] = None, keywords_embedding: Optional[List[float]] = None):
        self.node_id: str = str(uuid.uuid4())
        self.timestamp: datetime = datetime.utcnow()
        self.summary: str = summary
        self.embedding: Optional[List[float]] = embedding if embedding is not None else []  # 摘要embedding
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
            "embedding": self.embedding,
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
            embedding=data.get('embedding'),
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

    def _extract_keywords(self, text: str, max_keywords: int = 8) -> List[str]:
        """
        从文本中提取关键词
        使用简单的规则和正则表达式提取中文关键词
        """
        if not text:
            return []
        
        # 定义停用词
        stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '还', '把', '做', '让', '给', '用户', '对话', '交流', '聊天', '询问', '回答', '提到', '表示', '认为', '觉得'
        }
        
        # 提取中文词汇（2-4个字符的中文词组）
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
        
        # 过滤停用词和过短词汇
        keywords = []
        for word in chinese_words:
            if word not in stop_words and len(word) >= 2:
                keywords.append(word)
        
        # 去重并按长度排序（优先选择较长的词汇）
        keywords = list(set(keywords))
        keywords.sort(key=len, reverse=True)
        
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
                    print(f"成功生成embedding，维度: {len(result)}")
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
                    print(f"成功生成embedding，维度: {len(result)}")
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
    
    def repair_missing_embeddings(self):
        """
        修复缺失embedding的记忆点
        """
        print("开始检查和修复缺失的embedding...")
        
        def _traverse_and_repair(node: MemoryNode, level: int = 0):
            repaired_count = 0
            
            # 跳过root节点
            if node.summary != "Robot's Core Memory":
                # 检查是否缺少embedding
                if not node.embedding or len(node.embedding) == 0:
                    print(f"发现缺失embedding的节点: {node.summary[:50]}...")
                    
                    # 尝试生成embedding
                    new_embedding = self._generate_embedding(node.summary)
                    if new_embedding:
                        node.embedding = new_embedding
                        repaired_count += 1
                        print(f"✓ 已修复embedding")
                    else:
                        print(f"✗ 修复失败")
            
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
        
        # Create memory nodes for each memory point
        memory_nodes = []
        for memory_point in memory_points:
            # Generate embedding for each memory point
            embedding = self._generate_embedding(memory_point)
            
            # Create memory node
            memory_node = MemoryNode(summary=memory_point, embedding=embedding)
            
            # Add to tree (attach to root for now)
            self.root.add_child(memory_node)
            memory_nodes.append(memory_node)
            
            print(f"创建记忆点: {memory_point}")
        
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
            for i, turn in enumerate(self.current_conversation):
                if len(turn['user']) > 10:  # 过滤太短的输入
                    fallback_points.append(f"{person_name}说: {turn['user'][:50]}...")
            return fallback_points or [f"与{person_name}进行了对话交流"]

    def _summarize_conversation_with_llm(self, conversation_text: str, llm_client, person_name: str) -> str:
        """
        Use LLM to create a concise summary of the conversation.
        """
        prompt = (
            f"Please create a concise, insightful summary of this conversation with {person_name}. "
            "Focus on key topics, emotions, and important information that should be remembered. "
            "Keep it under 100 words.\n\n"
            f"Conversation:\n{conversation_text}\n\n"
            "Summary:"
        )
        
        try:
            response = llm_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error summarizing conversation with LLM: {e}")
            return f"Conversation summary with {person_name}: {conversation_text[:100]}..."

    def add_memory(self, text: str, parent_node_id: Optional[str] = None):
        """
        Processes a new piece of text, creates a memory node, and adds it to the tree.
        Now uses real embedding generation.
        """
        # 1. Use the text as summary directly (or could add LLM summarization here)
        summary = text
        
        # 2. Generate embedding for the summary
        embedding = self._generate_embedding(summary)

        new_node = MemoryNode(summary=summary, embedding=embedding)

        # 3. Find the parent node to attach to (or attach to root)
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
        Searches the memory tree for nodes semantically similar to the query text.
        This implements the "Dynamic Planning Search" algorithm with:
        1. Hierarchical tree traversal
        2. Cosine similarity calculation at each node
        3. Memory decay factor consideration
        4. Adaptive threshold based on tree level
        """
        print(f"Searching for: {query_text}")
        
        # 1. Generate embedding for the query text
        query_embedding = self._generate_embedding(query_text)
        if not query_embedding:
            print("Failed to generate query embedding")
            return []
        
        # 2. Initialize search results
        candidate_nodes = []
        
        # 3. Traverse the tree using dynamic programming approach
        self._dfs_search(self.root, query_embedding, similarity_threshold, candidate_nodes, level=0)
        
        # 4. Sort candidates by composite score (similarity * decay_factor)
        for candidate in candidate_nodes:
            node = candidate['node']
            similarity = candidate['similarity']
            decay_factor = self._calculate_memory_decay(node)
            candidate['composite_score'] = similarity * decay_factor
            candidate['decay_factor'] = decay_factor
        
        # Sort by composite score in descending order
        candidate_nodes.sort(key=lambda x: x['composite_score'], reverse=True)
        
        # 5. Return top results
        results = []
        for candidate in candidate_nodes[:max_results]:
            results.append({
                'node_id': candidate['node'].node_id,
                'summary': candidate['node'].summary,
                'similarity': candidate['similarity'],
                'decay_factor': candidate['decay_factor'],
                'composite_score': candidate['composite_score'],
                'timestamp': candidate['node'].timestamp.isoformat()
            })
        
        print(f"Found {len(results)} relevant memories")
        return results
    
    def _dfs_search(self, node: MemoryNode, query_embedding: List[float], 
                   similarity_threshold: float, candidates: List[Dict], level: int = 0):
        """
        Depth-first search with dynamic programming principles.
        Implements the tree traversal logic shown in your diagram.
        """
        # Skip root node (it's just a placeholder)
        if node.summary == "Robot's Core Memory":
            # Traverse children of root
            for child in node.children:
                self._dfs_search(child, query_embedding, similarity_threshold, candidates, level)
            return
        
        # Calculate similarity if node has embedding
        if node.embedding:
            similarity = self._cosine_similarity(query_embedding, node.embedding)
            
            # Adaptive threshold: higher levels (deeper nodes) can have slightly lower thresholds
            # This implements the "hierarchical retrieval" concept
            adaptive_threshold = similarity_threshold - (level * 0.05)  # Slight reduction per level
            adaptive_threshold = max(0.3, adaptive_threshold)  # Don't go below 0.3
            
            if similarity >= adaptive_threshold:
                candidates.append({
                    'node': node,
                    'similarity': similarity,
                    'level': level
                })
                print(f"  Found candidate at level {level}: {node.summary[:50]}... (similarity: {similarity:.3f})")
                
                # Decision point: should we continue searching children?
                # If current node has high similarity, children might also be relevant
                if similarity > 0.8:  # High similarity threshold for continuing
                    for child in node.children:
                        self._dfs_search(child, query_embedding, similarity_threshold, candidates, level + 1)
                
            # If node doesn't meet threshold but has children, still explore them
            # This implements the "dynamic planning" aspect - don't miss relevant children
            elif node.children and level < 3:  # Limit search depth to prevent infinite recursion
                for child in node.children:
                    self._dfs_search(child, query_embedding, similarity_threshold, candidates, level + 1)
    
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

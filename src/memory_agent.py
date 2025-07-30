import uuid
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from openai import OpenAI

# Assuming the semantic_memory.py file is in the same directory
from semantic_memory import MemoryTree, MemoryNode
import random

class PersonProfile:
    """
    Manages the profile for a single person, including their habits,
    preferences, and personality traits.
    """
    def __init__(self, person_name: str, data_path: str = '/home/xuanwu/haven_ws/demos/data/profiles'):
        self.person_name = person_name
        self.profile_path = os.path.join(data_path, f"{person_name}_profile.json")
        self.attributes: Dict[str, Any] = {
            "name": person_name,
            "age": "",  # 年龄
            "occupation": "",  # 职业
            "hobbies": [],  # 爱好
            "personality": "",  # 性格
            "favorite_foods": [],  # 爱吃的菜
            "habits": [],  # 习惯
            "quirks": [],  # 癖好
            "hometown": "",  # 家乡
            "preferences": {},  # 其他偏好
            "mood": "neutral",
            "last_interaction": None
        }
        os.makedirs(data_path, exist_ok=True)
        self.load_profile()

    def load_profile(self):
        """Loads the person's profile from a JSON file."""
        try:
            with open(self.profile_path, 'r', encoding='utf-8') as f:
                self.attributes = json.load(f)
            # print(f"Profile for {self.person_name} loaded.")
        except FileNotFoundError:
            print(f"No profile found for {self.person_name}. Creating a new one.")
            self.save_profile()
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error reading or parsing profile for {self.person_name}: {e}. Creating a new one.")
            self.save_profile()

    def save_profile(self):
        """Saves the current profile to a JSON file."""
        self.attributes['last_interaction'] = datetime.utcnow().isoformat()
        with open(self.profile_path, 'w', encoding='utf-8') as f:
            json.dump(self.attributes, f, ensure_ascii=False, indent=4)
        print(f"Profile for {self.person_name} saved.")

    def update_attribute(self, key: str, value: Any):
        """Updates a specific attribute in the profile."""
        self.attributes[key] = value
        self.save_profile()

class MemoryAgent:
    """
    The main agent class that orchestrates conversation, memory, and personalization.
    """
    def __init__(self, deepseek_api_key: str, deepseek_base_url: str, memory_file_path: str = '/home/xuanwu/haven_ws/demos/data/memory_tree.json'):
        self.client = OpenAI(api_key=deepseek_api_key, base_url=deepseek_base_url)
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(memory_file_path), exist_ok=True)
        
        # Initialize memory tree with embedding configuration
        embedding_config = {
            'APPID': 'b32f165e',
            'APISecret': 'MmJiZjQ0NTIzOTdhOWU0ZWY5ZjUyNzI0',
            'APIKEY': 'bf4caffa0bd087acc04cd63d0ee27fc5'
        }
        self.memory_history=''
        # Load existing memory tree or create new one
        try:
            self.memory_tree = MemoryTree.load(memory_file_path, embedding_config)
            # Ensure conversation tracking is initialized
            if not hasattr(self.memory_tree, 'current_conversation'):
                self.memory_tree.current_conversation = []
            if not hasattr(self.memory_tree, 'conversation_threshold'):
                self.memory_tree.conversation_threshold = 5
        except:
            self.memory_tree = MemoryTree(embedding_config=embedding_config)
        
        self.memory_file_path = memory_file_path
        
        self.current_person_profile: Optional[PersonProfile] = None
        self.short_term_memory: List[Dict[str, str]] = []

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

    def self_reflect(self, reflection_type: str = 'summarize_similar'):
        """
        Triggers the agent's self-reflection process.
        This can be run periodically to organize memories and deepen insights.
        """
        print("\n--- Starting Self-Reflection Process ---")
        if reflection_type == 'summarize_similar':
            self._summarize_similar_memories()
        elif reflection_type == 'update_profile':
            self._reflect_on_profile()
        elif reflection_type == 'discover_relationships':
            self._discover_relationships()
        elif reflection_type == 'global_synthesis':
            self._synthesize_global_experience()
        
        # Future reflection types can be added here

        self.memory_tree.save(self.memory_file_path)
        print("--- Self-Reflection Process Finished ---")

    def _get_all_nodes(self, node: MemoryNode = None) -> List[MemoryNode]:
        """Traverses the tree and returns a flat list of all nodes."""
        if node is None:
            node = self.memory_tree.root
        
        nodes = [node]
        for child in node.children:
            nodes.extend(self._get_all_nodes(child))
        return nodes

    def _summarize_similar_memories(self):
        """
        随机挑选10条同一个人的记忆，查看是否有类似的记忆或者可能因为噪声等产生的无意义的记忆，精简删除，保留最新的记忆。
        """
        print("反思相似记忆，清理无意义记忆...")
        
        # 获取所有记忆节点
        all_nodes = self._get_all_nodes()
        
        # 按人物分组所有记忆
        person_memories = {}
        for node in all_nodes:
            if node.summary == "Robot's Core Memory":
                continue
            
            # 提取人物姓名（简单方式：查找关键词中的人名）
            person_found = None
            for keyword in node.keywords:
                # 假设人名通常2-4个字符且是中文
                if len(keyword) >= 2 and len(keyword) <= 4:
                    person_found = keyword
                    break
            
            if person_found:
                if person_found not in person_memories:
                    person_memories[person_found] = []
                person_memories[person_found].append(node)
        
        if not person_memories:
            print("未找到按人物分类的记忆。")
            return
        
        # 随机选择一个人物
        import random
        selected_person = random.choice(list(person_memories.keys()))
        person_nodes = person_memories[selected_person]
        
        if len(person_nodes) < 2:
            print(f"{selected_person}的记忆数量不足，无法比较相似性。")
            return
        
        print(f"选择分析{selected_person}的记忆，共{len(person_nodes)}条")
        
        # 随机选择最多10条记忆进行分析
        selected_memories = random.sample(person_nodes, min(len(person_nodes), 10))
        
        # 使用LLM分析这些记忆，找出相似或无意义的记忆
        memories_text = ""
        for i, node in enumerate(selected_memories, 1):
            memories_text += f"{i}. {node.summary} (时间: {node.timestamp.strftime('%Y-%m-%d %H:%M')})\n"
        
        prompt = (
            f"请分析以下关于{selected_person}的记忆，找出相似、重复或无意义的记忆：\n\n"
            f"{memories_text}\n"
            "请识别：\n"
            "1. 哪些记忆内容相似或重复？\n"
            "2. 哪些记忆是无意义的噪声（如识别错误、无关信息）？\n"
            "3. 当有相似记忆时，应该保留哪一条（通常保留时间最新的）？\n\n"
            "请以JSON格式返回要删除的记忆编号列表，例如：{\"delete_indices\": [2, 5, 7]}\n"
            "如果没有需要删除的记忆，返回：{\"delete_indices\": []}"
        )
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            delete_indices = result.get("delete_indices", [])
            
            if not delete_indices:
                print(f"✅ {selected_person}的记忆没有需要清理的内容")
                return
            
            print(f"🗑️ 准备删除{len(delete_indices)}条记忆")
            deleted_count = 0
            
            # 删除标记的记忆节点
            for index in sorted(delete_indices, reverse=True):  # 倒序删除避免索引问题
                if 1 <= index <= len(selected_memories):
                    node_to_delete = selected_memories[index - 1]
                    parent = self.memory_tree.find_parent(node_to_delete.node_id)
                    
                    if parent:
                        parent.remove_child(node_to_delete.node_id)
                        deleted_count += 1
                        print(f"  删除记忆: {node_to_delete.summary[:50]}...")
                    else:
                        print(f"  无法找到父节点，跳过删除: {node_to_delete.node_id}")
            
            print(f"✅ 成功清理了{deleted_count}条{selected_person}的相似/无意义记忆")
            
        except Exception as e:
            print(f"❌ 记忆清理分析失败: {e}")

    def _reflect_on_profile(self, profile_data_path: str = '/home/xuanwu/haven_ws/demos/data/profiles'):
        """
        随机分析一个人物的记忆，更新优化其个人画像
        """
        print("反思和更新用户画像...")
        
        # 查找现有的用户画像文件
        try:
            profiles = [f for f in os.listdir(profile_data_path) if f.endswith('_profile.json')]
            if not profiles:
                print("未找到用户画像文件。")
                return
            
            # 随机选择一个用户进行分析
            random_profile_file = random.choice(profiles)
            person_name = random_profile_file.replace('_profile.json', '')
            
            print(f"选择分析用户：{person_name}")
            profile = PersonProfile(person_name, profile_data_path)
            
        except FileNotFoundError:
            print(f"用户画像目录不存在：'{profile_data_path}'")
            return

        # 收集与该用户相关的所有记忆
        all_nodes = self._get_all_nodes()
        related_memories = []
        
        for node in all_nodes:
            if node.summary == "Robot's Core Memory":
                continue
            
            # 检查记忆是否与该用户相关（通过关键词或内容匹配）
            is_related = False
            
            # 方法1：检查关键词中是否包含用户名
            if person_name in node.keywords:
                is_related = True
            
            # 方法2：检查摘要内容中是否提及用户名
            elif person_name in node.summary:
                is_related = True
            
            if is_related:
                related_memories.append({
                    'summary': node.summary,
                    'keywords': node.keywords,
                    'timestamp': node.timestamp.strftime('%Y-%m-%d %H:%M')
                })

        if not related_memories:
            print(f"未找到与{person_name}相关的记忆。")
            return
            
        print(f"找到{len(related_memories)}条与{person_name}相关的记忆")

        # 按时间排序，分析最近的记忆以更好地理解用户状态
        related_memories.sort(key=lambda x: x['timestamp'], reverse=True)
        recent_memories = related_memories[:15]  # 分析最近15条记忆
        
        # 构建记忆文本
        memories_text = ""
        for i, memory in enumerate(recent_memories, 1):
            memories_text += f"{i}. {memory['summary']} (时间: {memory['timestamp']})\n"

        # 使用LLM分析记忆并更新画像
        prompt = (
            f"请基于以下关于{person_name}的记忆，分析并更新他/她的个人画像。\n\n"
            f"当前画像信息：\n"
            f"姓名: {profile.attributes.get('name', person_name)}\n"
            f"年龄: {profile.attributes.get('age', '未知')}\n"
            f"职业: {profile.attributes.get('occupation', '未知')}\n"
            f"爱好: {', '.join(profile.attributes.get('hobbies', []))}\n"
            f"性格: {profile.attributes.get('personality', '未知')}\n"
            f"爱吃的菜: {', '.join(profile.attributes.get('favorite_foods', []))}\n"
            f"习惯: {', '.join(profile.attributes.get('habits', []))}\n"
            f"癖好: {', '.join(profile.attributes.get('quirks', []))}\n"
            f"家乡: {profile.attributes.get('hometown', '未知')}\n"
            f"当前情绪: {profile.attributes.get('mood', 'neutral')}\n\n"
            f"相关记忆：\n{memories_text}\n"
            "请基于这些记忆分析，以JSON格式返回需要更新的画像字段。包括：\n"
            "- age: 年龄信息（如果从对话中能推断出来）\n"
            "- occupation: 职业信息\n"
            "- hobbies: 新发现的爱好（数组格式）\n"
            "- personality: 性格特征描述\n"
            "- favorite_foods: 喜欢的食物（数组格式）\n"
            "- habits: 生活习惯（数组格式）\n"
            "- quirks: 个人癖好（数组格式）\n"
            "- hometown: 家乡信息\n"
            "- mood: 更多的表现这个人的脾气\n"
            "- preferences: 其他偏好（对象格式）\n\n"
            "不要过多猜测，这将指导你和他的交流方式。如果没有新信息，返回空对象{}。\n"
            "示例：{\"hobbies\": [\"园艺\", \"阅读\"], \"mood\": \"焦虑\", \"habits\": [\"每天早起散步\"]}"
        )

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            import json
            updates = json.loads(response.choices[0].message.content)
            
            if not updates:
                print(f"✅ {person_name}的画像无需更新")
                return
            
            print(f"🔄 准备更新{person_name}的画像：{updates}")

            # 应用更新
            updated_fields = []
            for key, value in updates.items():
                if key in profile.attributes:
                    # 对于列表类型字段，合并新信息（去重）
                    if isinstance(value, list) and isinstance(profile.attributes[key], list):
                        original_count = len(profile.attributes[key])
                        for item in value:
                            if item not in profile.attributes[key]:
                                profile.attributes[key].append(item)
                        if len(profile.attributes[key]) > original_count:
                            updated_fields.append(f"{key}: 新增{len(profile.attributes[key]) - original_count}项")
                    
                    # 对于字典类型字段（如preferences），合并更新
                    elif isinstance(value, dict) and isinstance(profile.attributes[key], dict):
                        original_keys = set(profile.attributes[key].keys())
                        profile.attributes[key].update(value)
                        new_keys = set(profile.attributes[key].keys()) - original_keys
                        if new_keys or any(profile.attributes[key][k] != value.get(k) for k in value):
                            updated_fields.append(f"{key}: 更新{len(value)}项")
                    
                    # 对于其他类型，直接更新
                    else:
                        if profile.attributes[key] != value:
                            profile.attributes[key] = value
                            updated_fields.append(f"{key}: {value}")
            
            if updated_fields:
                profile.save_profile()
                print(f"✅ 成功更新{person_name}的画像：{', '.join(updated_fields)}")
            else:
                print(f"ℹ️ {person_name}的画像信息已是最新")

        except Exception as e:
            print(f"❌ 画像分析更新失败: {e}")

    def _discover_relationships(self, profile_data_path: str = '/home/xuanwu/haven_ws/demos/data/profiles'):
        """
        随机让DeepSeek分析两个人的记忆，推断他们之间的关系，更新在用户画像里
        """
        print("发现和分析人际关系...")
        
        try:
            profiles = [f.replace('_profile.json', '') for f in os.listdir(profile_data_path) if f.endswith('_profile.json')]
            if len(profiles) < 2:
                print("用户数量不足，无法分析人际关系。")
                return
            
            # 随机选择两个不同的用户
            person1_name, person2_name = random.sample(profiles, 2)
            print(f"分析{person1_name}和{person2_name}之间的关系")

        except FileNotFoundError:
            print(f"用户画像目录不存在：'{profile_data_path}'")
            return

        # 查找涉及这两个人的共同记忆
        all_nodes = self._get_all_nodes()
        shared_memories = []
        person1_memories = []
        person2_memories = []
        
        for node in all_nodes:
            if node.summary == "Robot's Core Memory":
                continue
            
            person1_mentioned = person1_name in node.keywords or person1_name in node.summary
            person2_mentioned = person2_name in node.keywords or person2_name in node.summary
            
            if person1_mentioned and person2_mentioned:
                # 两人都出现的记忆
                shared_memories.append({
                    'summary': node.summary,
                    'timestamp': node.timestamp.strftime('%Y-%m-%d %H:%M')
                })
            elif person1_mentioned:
                person1_memories.append({
                    'summary': node.summary,
                    'timestamp': node.timestamp.strftime('%Y-%m-%d %H:%M')
                })
            elif person2_mentioned:
                person2_memories.append({
                    'summary': node.summary,
                    'timestamp': node.timestamp.strftime('%Y-%m-%d %H:%M')
                })

        # 按时间排序
        shared_memories.sort(key=lambda x: x['timestamp'], reverse=True)
        person1_memories.sort(key=lambda x: x['timestamp'], reverse=True)
        person2_memories.sort(key=lambda x: x['timestamp'], reverse=True)

        print(f"找到共同记忆{len(shared_memories)}条，{person1_name}单独记忆{len(person1_memories)}条，{person2_name}单独记忆{len(person2_memories)}条")

        if not shared_memories and len(person1_memories) == 0 and len(person2_memories) == 0:
            print(f"{person1_name}和{person2_name}之间没有相关记忆。")
            return

        # 构建记忆文本用于LLM分析
        memories_text = ""
        
        if shared_memories:
            memories_text += f"=== {person1_name}和{person2_name}的共同记忆 ===\n"
            for i, memory in enumerate(shared_memories[:10], 1):  # 最多分析10条共同记忆
                memories_text += f"{i}. {memory['summary']} (时间: {memory['timestamp']})\n"
            memories_text += "\n"
        
        if person1_memories:
            memories_text += f"=== {person1_name}的相关记忆 ===\n"
            for i, memory in enumerate(person1_memories[:5], 1):  # 最多5条个人记忆作为背景
                memories_text += f"{i}. {memory['summary']} (时间: {memory['timestamp']})\n"
            memories_text += "\n"
        
        if person2_memories:
            memories_text += f"=== {person2_name}的相关记忆 ===\n"
            for i, memory in enumerate(person2_memories[:5], 1):  # 最多5条个人记忆作为背景
                memories_text += f"{i}. {memory['summary']} (时间: {memory['timestamp']})\n"

        # 使用LLM分析关系
        prompt = (
            f"请分析{person1_name}和{person2_name}之间的人际关系。\n\n"
            f"记忆信息：\n{memories_text}\n"
            "请基于这些记忆推断他们之间的关系类型。可能的关系包括但不限于：\n"
            "- 好友：经常一起活动，互相关心\n"
            "- 恋人：有浪漫关系的表现\n"
            "- 家人：亲属关系\n"
            "- 同事：工作上的合作关系\n"
            "- 邻居：居住地相近\n"
            "- 不太和睦：有冲突或矛盾\n"
            "- 陌生人：很少或没有互动\n"
            "- 其他：请具体描述\n\n"
            "请以JSON格式返回分析结果：\n"
            "{\n"
            "  \"relationship_type\": \"关系类型\",\n"
            "  \"relationship_description\": \"关系的具体描述\",\n"
            "  \"confidence\": \"high/medium/low\",\n"
            "  \"evidence\": \"支持这个判断的证据摘要\"\n"
            "}\n"
            "如果没有足够信息判断关系，返回relationship_type为\"未知\"。"
        )

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            import json
            relationship_analysis = json.loads(response.choices[0].message.content)
            
            relationship_type = relationship_analysis.get("relationship_type", "未知")
            relationship_desc = relationship_analysis.get("relationship_description", "")
            confidence = relationship_analysis.get("confidence", "low")
            evidence = relationship_analysis.get("evidence", "")
            
            print(f"🔍 关系分析结果：{person1_name} - {person2_name}")
            print(f"  关系类型：{relationship_type}")
            print(f"  描述：{relationship_desc}")
            print(f"  置信度：{confidence}")
            print(f"  证据：{evidence}")

            if relationship_type == "未知" or confidence == "low":
                print("关系证据不足，不更新画像")
                return

            # 更新两个人的画像，添加关系信息
            self._update_relationship_in_profiles(
                person1_name, person2_name, 
                relationship_type, relationship_desc, 
                profile_data_path
            )

        except Exception as e:
            print(f"❌ 关系分析失败: {e}")

    def _update_relationship_in_profiles(self, person1_name, person2_name, relationship_type, relationship_desc, profile_data_path):
        """
        在两个用户的画像中更新关系信息
        """
        try:
            # 更新person1的画像
            profile1 = PersonProfile(person1_name, profile_data_path)
            if 'relationships' not in profile1.attributes:
                profile1.attributes['relationships'] = {}
            
            profile1.attributes['relationships'][person2_name] = {
                'type': relationship_type,
                'description': relationship_desc,
                'updated_time': datetime.utcnow().strftime('%Y-%m-%d %H:%M')
            }
            profile1.save_profile()
            
            # 更新person2的画像（对称关系）
            profile2 = PersonProfile(person2_name, profile_data_path)
            if 'relationships' not in profile2.attributes:
                profile2.attributes['relationships'] = {}
            
            profile2.attributes['relationships'][person1_name] = {
                'type': relationship_type,
                'description': relationship_desc,
                'updated_time': datetime.utcnow().strftime('%Y-%m-%d %H:%M')
            }
            profile2.save_profile()
            
            print(f"✅ 成功更新{person1_name}和{person2_name}的关系信息：{relationship_type}")
            
        except Exception as e:
            print(f"❌ 更新关系信息失败: {e}")

    def _synthesize_global_experience(self, days_back: int = 7, profile_data_path: str = '/home/xuanwu/haven_ws/demos/data/profiles'):
        """
        从记忆样本中提取时间相近的记忆，让llm理解总体主题和结论，
        侧重于对环境对任务总体的理解，并在用户画像的目录下维护一个"机器人脑海"文件
        """
        print("进行全局经验综合，提取环境和任务认知...")
        
        # 确保机器人脑海目录存在
        brain_file_path = os.path.join(profile_data_path, "机器人脑海.json")
        
        # 获取指定时间范围内的记忆
        all_nodes = self._get_all_nodes()
        recent_memories = []
        
        # 计算时间阈值（几天前）
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(days=days_back)
        
        for node in all_nodes:
            if node.summary == "Robot's Core Memory":
                continue
                
            # 只分析最近几天的记忆
            if node.timestamp >= cutoff_time:
                recent_memories.append({
                    'summary': node.summary,
                    'keywords': node.keywords,
                    'timestamp': node.timestamp.strftime('%Y-%m-%d %H:%M'),
                    'date': node.timestamp.strftime('%Y-%m-%d'),
                    'time': node.timestamp.strftime('%H:%M')
                })
        
        if len(recent_memories) < 3:
            print(f"最近{days_back}天的记忆不足，无法进行全局分析。")
            return
        
        print(f"分析最近{days_back}天的{len(recent_memories)}条记忆")
        
        # 按日期分组记忆
        daily_memories = {}
        for memory in recent_memories:
            date = memory['date']
            if date not in daily_memories:
                daily_memories[date] = []
            daily_memories[date].append(memory)
        
        # 构建记忆文本，按日期组织
        memories_text = ""
        for date in sorted(daily_memories.keys()):
            memories_text += f"=== {date} ===\n"
            for memory in daily_memories[date]:
                memories_text += f"  {memory['time']}: {memory['summary']}\n"
            memories_text += "\n"
        
        # 加载现有的机器人脑海
        existing_insights = self._load_robot_brain(brain_file_path)
        existing_insights_text = ""
        if existing_insights:
            existing_insights_text = "\n现有的环境认知：\n"
            for i, insight in enumerate(existing_insights, 1):
                existing_insights_text += f"{i}. {insight['content']} (发现时间: {insight['discovered_time']})\n"
        
        # 使用LLM进行全局经验综合
        prompt = (
            f"请分析机器人最近{days_back}天的记忆，提取关于环境、任务和规律的认知洞察。\n"
            "重点关注：\n"
            "1. 重复出现的任务模式（如'每天上午八点送水'）\n"
            "2. 环境布局和功能区域的理解\n"
            "3. 用户的生活规律和需求模式\n"
            "4. 重要的操作流程和注意事项\n"
            "5. 异常情况和应对方式\n\n"
            "6. 这是一个讲给自己听的事情，用户的喜欢不必要记录太多，而是总结一些更有规律性的事情：比如，张奶奶很喜欢在早上问穿搭，那我们就很有必要在早上给他推荐穿搭。\n\n"
            f"时间相近的记忆数据：\n{memories_text}"
            f"{existing_insights_text}\n"
            "请提取新的环境和任务认知，以JSON数组格式返回：\n"
            "[\n"
            "  {\n"
            "    \"type\": \"task_pattern/environment/user_habit/procedure/emergency\",\n"
            "    \"content\": \"具体的认知内容描述\",\n"
            "    \"evidence\": \"支持这个认知的记忆证据\",\n"
            "    \"confidence\": \"high/medium/low\",\n"
            "    \"actionable\": \"这个认知是否可以指导机器人的行动（true/false）\"\n"
            "  }\n"
            "]\n\n"
            "避免重复已有的认知，只返回新发现的洞察。如果没有新发现，返回空数组[]。\n"
            "每个认知应该具体明确，有实际指导意义。"
        )

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            new_insights = result if isinstance(result, list) else result.get("insights", [])
            
            if not new_insights:
                print("✅ 没有发现新的环境和任务认知")
                return
            
            print(f"🧠 发现{len(new_insights)}条新的认知洞察")
            
            # 处理新洞察并添加到机器人脑海
            valid_insights = []
            for insight in new_insights:
                if self._validate_insight(insight):
                    insight['discovered_time'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
                    insight['id'] = str(uuid.uuid4())
                    valid_insights.append(insight)
                    
                    print(f"  💡 {insight['type']}: {insight['content']}")
                    print(f"     置信度: {insight['confidence']}, 可执行: {insight['actionable']}")
            
            if valid_insights:
                # 更新机器人脑海文件
                updated_brain = existing_insights + valid_insights
                self._save_robot_brain(brain_file_path, updated_brain)
                print(f"✅ 成功更新机器人脑海，新增{len(valid_insights)}条认知")
            else:
                print("⚠️ 新发现的认知未通过验证")

        except Exception as e:
            print(f"❌ 全局经验综合失败: {e}")

    def _load_robot_brain(self, brain_file_path: str) -> list:
        """
        加载机器人脑海文件
        """
        try:
            if os.path.exists(brain_file_path):
                with open(brain_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            print(f"❌ 加载机器人脑海失败: {e}")
            return []

    def _save_robot_brain(self, brain_file_path: str, insights: list):
        """
        保存机器人脑海文件
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(brain_file_path), exist_ok=True)
            
            # 按置信度和时间排序
            sorted_insights = sorted(insights, key=lambda x: (
                {'high': 3, 'medium': 2, 'low': 1}.get(x.get('confidence', 'low'), 1),
                x.get('discovered_time', '')
            ), reverse=True)
            
            with open(brain_file_path, 'w', encoding='utf-8') as f:
                json.dump(sorted_insights, f, ensure_ascii=False, indent=2)
            
            print(f"💾 机器人脑海已保存到: {brain_file_path}")
            
        except Exception as e:
            print(f"❌ 保存机器人脑海失败: {e}")

    def _validate_insight(self, insight: dict) -> bool:
        """
        验证认知洞察的有效性
        """
        required_fields = ['type', 'content', 'evidence', 'confidence', 'actionable']
        
        # 检查必需字段
        for field in required_fields:
            if field not in insight or not insight[field]:
                return False
        
        # 检查类型有效性
        valid_types = ['task_pattern', 'environment', 'user_habit', 'procedure', 'emergency']
        if insight['type'] not in valid_types:
            return False
        
        # 检查置信度有效性
        if insight['confidence'] not in ['high', 'medium', 'low']:
            return False
        
        # 检查内容长度
        if len(insight['content'].strip()) < 10:
            return False
        
        return True

    def get_robot_brain_insights(self, insight_type: str = None, actionable_only: bool = False, profile_data_path: str = '/home/xuanwu/haven_ws/demos/data/profiles') -> list:
        """
        获取机器人脑海中的认知洞察
        
        Args:
            insight_type: 筛选特定类型的洞察
            actionable_only: 只返回可执行的洞察
            profile_data_path: 画像数据路径
            
        Returns:
            符合条件的洞察列表
        """
        brain_file_path = os.path.join(profile_data_path, "机器人脑海.json")
        insights = self._load_robot_brain(brain_file_path)
        
        # 应用筛选条件
        filtered_insights = insights
        
        if insight_type:
            filtered_insights = [i for i in filtered_insights if i.get('type') == insight_type]
        
        if actionable_only:
            filtered_insights = [i for i in filtered_insights if i.get('actionable') == 'true']
        
        return filtered_insights


    def start_chat(self, person_name: str):
        """
        Starts or continues a conversation with a specific person.
        """
        try:
            self.current_person_profile = PersonProfile(person_name)
            self.short_term_memory = [] # Reset short-term memory for a new chat session
            # print(f"Chat started with {person_name}. Profile loaded.")
            return True
        except Exception as e:
            print(f"Error starting chat: {e}")
            return False

    def chat(self, user_input: str) -> str:
        """
        Handles a single turn of the conversation with enhanced memory management.
        """
        if not self.current_person_profile:
            return "Error: Chat not started. Please use start_chat(person_name) first."

        # 1. Add user message to short-term memory
        self.short_term_memory.append({"role": "user", "content": user_input})

        # 2. Retrieve relevant long-term memories using the new search algorithm
        retrieved_memories = self.memory_tree.search(user_input, similarity_threshold=0.6, max_results=3)
        
        # Format memory context for the LLM
        self.memory_history = ""
        if retrieved_memories:
            self.memory_history = "\n\n相关记忆:\n"
            for i, memory in enumerate(retrieved_memories, 1):
                self.memory_history += f"{i}. {memory['summary']} (相似度: {memory['similarity']:.2f})\n"

        # 3. Construct the full prompt for the LLM with enhanced profile information
        profile_info = self._format_profile_for_llm(self.current_person_profile.attributes)
        
        system_prompt = (
            f"你是一个老年机构的助手，. "
            f"You are talking to {self.current_person_profile.person_name}.\n"
            f"用户画像:\n{profile_info}"
            f"{self.memory_history}"
            f"你不必总是叫出对方发名字，但可以在合适的情况下使用敬语。\n"
        )
        
        # 4. Manage conversation context length (keep recent 10 turns + system prompt)
        max_history_turns = 10
        if len(self.short_term_memory) > max_history_turns * 2:  # Each turn has user + assistant
            # Keep the most recent turns
            self.short_term_memory = self.short_term_memory[-(max_history_turns * 2):]
        
        messages_for_api = [{"role": "system", "content": system_prompt}] + self.short_term_memory

        # 5. Call the DeepSeek API with proper multi-turn context
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages_for_api
            )
            assistant_response = response.choices[0].message.content
        except Exception as e:
            print(f"Error calling DeepSeek API: {e}")
            return "Sorry, I encountered an error."

        # 6. Add assistant response to short-term memory (maintaining conversation context)
        self.short_term_memory.append({"role": "assistant", "content": assistant_response})

        # 7. Add conversation turn to memory tree
        should_check_end = self.memory_tree.add_conversation_turn(user_input, assistant_response)
        
        # 8. Check if conversation should end (either by turn count or LLM detection)
        conversation_should_end = False
        if should_check_end:
            conversation_should_end = self.memory_tree.check_conversation_end(user_input, self.client)
        
        # Also check for explicit goodbye patterns
        goodbye_patterns = ['再见', 'bye', 'goodbye', '拜拜', '88', '结束对话', 'quit', 'exit']
        if any(pattern in user_input.lower() for pattern in goodbye_patterns):
            conversation_should_end = True

        # 9. Finalize conversation if needed
        if conversation_should_end:
            print(f"\n检测到对话结束，正在提取记忆点...")
            
            # 在finalize_conversation之前保存对话内容，用于画像更新
            conversation_text = ""
            for turn in self.memory_tree.current_conversation:
                conversation_text += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
            
            memory_nodes = self.memory_tree.finalize_conversation(
                llm_client=self.client, 
                person_name=self.current_person_profile.person_name
            )
            if memory_nodes:
                self.memory_tree.save(self.memory_file_path)
                print(f"已创建 {len(memory_nodes)} 个记忆点并保存")
                # 显示创建的记忆点
                for i, node in enumerate(memory_nodes, 1):
                    print(f"  {i}. {node.summary}")
            
            # 使用LLM更新用户画像（使用之前保存的对话内容）
            print(f"\n🧑‍💼 正在更新{self.current_person_profile.person_name}的用户画像...")
            
            updated_profile = self._update_profile_with_llm(
                self.current_person_profile.person_name,
                conversation_text,
                self.current_person_profile.attributes
            )
            
            # 保存更新后的画像
            if updated_profile != self.current_person_profile.attributes:
                self.current_person_profile.attributes = updated_profile
                self.current_person_profile.save_profile()
                print(f"✅ 用户画像已更新并保存")
            else:
                print(f"ℹ️ 用户画像无需更新")
        
        # 10. Update profile
        self.current_person_profile.update_attribute("last_interaction", datetime.utcnow().isoformat())

        return assistant_response

    def end_conversation(self):
        """
        Manually end the current conversation and save memory points.
        """
        if self.current_person_profile and self.memory_tree.current_conversation:
            print(f"手动结束与 {self.current_person_profile.person_name} 的对话...")
            
            # 在finalize_conversation之前保存对话内容，用于画像更新
            conversation_text = ""
            for turn in self.memory_tree.current_conversation:
                conversation_text += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
            
            memory_nodes = self.memory_tree.finalize_conversation(
                llm_client=self.client, 
                person_name=self.current_person_profile.person_name
            )
            if memory_nodes:
                self.memory_tree.save(self.memory_file_path)
                print(f"已创建 {len(memory_nodes)} 个记忆点并保存:")
                for i, node in enumerate(memory_nodes, 1):
                    print(f"  {i}. {node.summary}")
            
            # 使用LLM更新用户画像（使用之前保存的对话内容）
            print(f"\n🧑‍💼 正在更新{self.current_person_profile.person_name}的用户画像...")
            
            updated_profile = self._update_profile_with_llm(
                self.current_person_profile.person_name,
                conversation_text,
                self.current_person_profile.attributes
            )
            
            # 保存更新后的画像
            if updated_profile != self.current_person_profile.attributes:
                self.current_person_profile.attributes = updated_profile
                self.current_person_profile.save_profile()
                print(f"✅ 用户画像已更新并保存")
            else:
                print(f"ℹ️ 用户画像无需更新")
            
            return memory_nodes
        else:
            print("没有活跃的对话需要结束。")
            return []

    def repair_embeddings(self):
        """
        修复记忆树中缺失的embedding
        """
        print("开始修复记忆树中缺失的embedding...")
        repaired_count = self.memory_tree.repair_missing_embeddings()
        
        if repaired_count > 0:
            # 保存修复后的记忆树
            self.memory_tree.save(self.memory_file_path)
            print(f"修复完成并已保存，共修复了 {repaired_count} 个记忆点")
        else:
            print("没有发现需要修复的embedding")
        
        return repaired_count

    def _format_profile_for_llm(self, attributes: Dict[str, Any]) -> str:
        """
        格式化用户画像信息，供LLM使用
        """
        profile_lines = []
        
        # 基本信息
        if attributes.get('name'):
            profile_lines.append(f"姓名: {attributes['name']}")
        if attributes.get('age'):
            profile_lines.append(f"年龄: {attributes['age']}")
        if attributes.get('occupation'):
            profile_lines.append(f"职业: {attributes['occupation']}")
        if attributes.get('hometown'):
            profile_lines.append(f"家乡: {attributes['hometown']}")
        
        # 性格特征
        if attributes.get('personality'):
            profile_lines.append(f"性格: {attributes['personality']}")
        
        # 爱好兴趣
        if attributes.get('hobbies') and len(attributes['hobbies']) > 0:
            profile_lines.append(f"爱好: {', '.join(attributes['hobbies'])}")
        
        # 饮食偏好
        if attributes.get('favorite_foods') and len(attributes['favorite_foods']) > 0:
            profile_lines.append(f"爱吃的菜: {', '.join(attributes['favorite_foods'])}")
        
        # 习惯
        if attributes.get('habits') and len(attributes['habits']) > 0:
            profile_lines.append(f"习惯: {', '.join(attributes['habits'])}")
        
        # 癖好
        if attributes.get('quirks') and len(attributes['quirks']) > 0:
            profile_lines.append(f"癖好: {', '.join(attributes['quirks'])}")
        
        # 其他偏好
        if attributes.get('preferences') and len(attributes['preferences']) > 0:
            prefs = [f"{k}: {v}" for k, v in attributes['preferences'].items() if v]
            if prefs:
                profile_lines.append(f"其他偏好: {', '.join(prefs)}")
        
        # 当前状态
        if attributes.get('mood'):
            profile_lines.append(f"当前情绪: {attributes['mood']}")
        
        # 如果没有足够信息，返回基本提示
        if len(profile_lines) <= 1:  # 只有姓名
            return f"这是与{attributes.get('name', '用户')}的对话，暂无更多个人信息。"
        
        return "\n".join(profile_lines)

    def _update_profile_with_llm(self, person_name: str, conversation_content: str, current_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用LLM分析对话内容，更新用户画像
        """
        # 格式化当前画像信息
        current_profile_text = self._format_profile_for_llm(current_profile)
        
        prompt = (
            f"请分析以下与{person_name}的对话，基于对话内容更新用户画像。\n"
            "只有当你从对话中明确获得信息时才更新相应字段，不要猜测或假设。\n"
            f"当前用户画像:\n{current_profile_text}\n\n"
            f"对话内容:\n{conversation_content}\n\n"
            "请根据对话内容，以JSON格式返回需要更新的字段。可更新的字段包括但不限于：\n"
            "- age: 年龄（字符串，如'25岁'）\n"
            "- occupation: 职业（字符串）\n"
            "- hobbies: 爱好（字符串数组）\n"
            "- personality: 性格特征（字符串）\n"
            "- favorite_foods: 爱吃的菜（字符串数组）\n"
            "- habits: 习惯（字符串数组）\n"
            "- quirks: 癖好（字符串数组）\n"
            "- hometown: 家乡（字符串）\n"
            "- preferences: 其他偏好（对象）\n"
            "- mood: 当前情绪（字符串）\n\n"
            "示例返回格式:\n"
            "{\n"
            "  \"hobbies\": [\"旅游\", \"摄影\"],\n"
            "  \"occupation\": \"AI项目创作者\",\n"
            "  \"mood\": \"兴奋\"\n"
            "}\n\n"
            "如果没有信息需要更新，请返回空对象: {}\n"
        )
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            updates = json.loads(response.choices[0].message.content)
            print(f"🔄 LLM分析的画像更新: {updates}")
            
            # 合并更新到当前画像
            updated_profile = current_profile.copy()
            
            for key, value in updates.items():
                if key in updated_profile:
                    if isinstance(value, list) and isinstance(updated_profile[key], list):
                        # 对于列表类型，合并去重
                        existing_items = set(updated_profile[key])
                        for item in value:
                            if item not in existing_items:
                                updated_profile[key].append(item)
                    else:
                        # 对于其他类型，直接更新
                        updated_profile[key] = value
            
            return updated_profile
            
        except Exception as e:
            print(f"❌ LLM画像更新失败: {e}")
            return current_profile

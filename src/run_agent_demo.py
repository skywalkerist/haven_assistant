from memory_agent import MemoryAgent

def main():
    # --- 配置 ---
    DEEPSEEK_API_KEY = "sk-a4ce2451fc534091aff7704e5498a698"
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"
    
    # --- 初始化 ---
    print("初始化记忆智能体...")
    agent = MemoryAgent(
        deepseek_api_key=DEEPSEEK_API_KEY,
        deepseek_base_url=DEEPSEEK_BASE_URL
    )

    # --- Conversation 1: Zhang San ---
    # person1_name = "张三"
    # print(f"\n--- Starting chat with {person1_name} ---")
    # agent.start_chat(person1_name)
    
    # user_input_1 = "你好，我喜欢爬山和摄影。"
    # print(f"[{person1_name}]: {user_input_1}")
    # assistant_response_1 = agent.chat(user_input_1)
    # print(f"[Agent]: {assistant_response_1}")

    # --- Conversation 2: Li Si ---
    person2_name = "李四"
    print(f"\n--- Starting chat with {person2_name} ---")
    agent.start_chat(person2_name)

    user_input_2 = "你认识张三吗，他人怎么样，爱好是什么？"
    print(f"[{person2_name}]: {user_input_2}")
    assistant_response_2 = agent.chat(user_input_2)
    print(f"[Agent]: {assistant_response_2}")

    # --- Conversation 3: Zhang San mentions Li Si ---
    # print(f"\n--- Continuing chat with {person1_name} ---")
    # agent.start_chat(person1_name)

    # user_input_3 = f"我听我的同事李四说，你们的AI很懂技术，是真的吗？"
    # print(f"[{person1_name}]: {user_input_3}")
    # assistant_response_3 = agent.chat(user_input_3)
    # print(f"[Agent]: {assistant_response_3}")

    print("\n--- Demo Finished ---")
    print("\nDemo data has been generated for '张三' and '李四'.")
    print("A shared context between them has also been created.")
    print("You can now run the reflection script to discover their relationship.")


if __name__ == "__main__":
    main()

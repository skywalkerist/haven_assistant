import argparse
import random
from memory_agent import MemoryAgent

def main():
    """
    A script to manually trigger the MemoryAgent's self-reflection process.
    """
    parser = argparse.ArgumentParser(
        description="Trigger the self-reflection process for the MemoryAgent."
    )
    
    reflection_choices = [
        'summarize_similar', 
        'update_profile', 
        'discover_relationships', 
        'global_synthesis'
    ]
    
    parser.add_argument(
        '--type', 
        choices=reflection_choices + ['random'], 
        default='random',
        help="The type of reflection to perform. 'random' will pick one of the available types."
    )
    
    args = parser.parse_args()

    reflection_type_to_run = args.type
    if reflection_type_to_run == 'random':
        reflection_type_to_run = random.choice(reflection_choices)
        print(f"Randomly selected reflection type: '{reflection_type_to_run}'")


    # --- Configuration ---
    # IMPORTANT: Replace with your actual DeepSeek API key and base URL
    DEEPSEEK_API_KEY = "sk-a4ce2451fc534091aff7704e5498a698"
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"

    # --- Initialization ---
    print("Initializing MemoryAgent for reflection...")
    agent = MemoryAgent(
        deepseek_api_key=DEEPSEEK_API_KEY,
        deepseek_base_url=DEEPSEEK_BASE_URL
    )

    # --- Trigger Reflection ---
    agent.self_reflect(reflection_type=reflection_type_to_run)


if __name__ == "__main__":
    main()

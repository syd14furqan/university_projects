
import gradio as gr
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import requests
import json
import os

# LM Studio Configuration
LM_STUDIO_BASE_URL = "http://127.0.0.1:1234/v1"  # Updated to match your server
LM_STUDIO_API_KEY = "meta-llama-3.1-8b-instruct"

# Simple direct API function (fallback)
def direct_lm_studio_request(prompt):
    try:
        response = requests.post(
            f"{LM_STUDIO_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {LM_STUDIO_API_KEY}"},
            json={
                "model": "local",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.9,
                "max_tokens": 500
            }
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return None
    except:
        return None

# Initialize the language model (using LM Studio local server)
llm = ChatOpenAI(
    base_url=LM_STUDIO_BASE_URL,
    api_key=LM_STUDIO_API_KEY,
    temperature=0.9,
    max_tokens=500,
    model="local-model"
)

# Create a prompt template for prompt generation
prompt_template = """
You are an expert prompt engineer. Generate creative and effective prompts for AI assistants.

Topic/Context: {topic}
Prompt Type: {prompt_type}
Complexity: {complexity}

Create {num_prompts} high-quality prompt(s) that are:
- Clear and specific
- Engaging and creative
- Well-structured
- Suitable for the specified type and complexity level

Format each prompt clearly and make them ready to use with AI assistants.

Generated Prompts:
"""

prompt = PromptTemplate(
    input_variables=["topic", "prompt_type", "complexity", "num_prompts"],
    template=prompt_template
)

# Create the LangChain chain
prompt_chain = LLMChain(llm=llm, prompt=prompt)

def generate_prompts(topic, prompt_type, complexity, num_prompts):
    """Generate prompts based on user input"""
    if not topic.strip():
        return "Please enter a topic or context to generate prompts!"
    
    # Create the full prompt
    full_prompt = f"""You are an expert prompt engineer. Generate creative and effective prompts for AI assistants.

Topic/Context: {topic}
Prompt Type: {prompt_type}
Complexity: {complexity}

Create {num_prompts} high-quality prompt(s) that are:
- Clear and specific
- Engaging and creative  
- Well-structured
- Suitable for the specified type and complexity level

Format each prompt clearly and make them ready to use with AI assistants.

Generated Prompts:"""
    
    try:
        # Try LangChain first
        result = prompt_chain.run(
            topic=topic, 
            prompt_type=prompt_type,
            complexity=complexity,
            num_prompts=f"{num_prompts} different"
        )
        
        if result and result.strip():
            return result.strip()
        else:
            # Fallback to direct API call
            result = direct_lm_studio_request(full_prompt)
            if result:
                return result.strip()
            else:
                return "❌ No response from LM Studio. Check server status!"
        
    except Exception as e:
        # Try direct API as fallback
        result = direct_lm_studio_request(full_prompt)
        if result:
            return result.strip()
        
        return f"""❌ Connection Error!

**Error**: {str(e)}

**Quick Fix Steps**:
1. Open LM Studio
2. Load a model in Chat tab (wait for full loading)
3. Go to Developer tab → Start Server
4. Verify: http://127.0.0.1:1234 is running
5. Try again

**Alternative**: Use a different model or restart LM Studio"""

def clear_inputs():
    """Clear all inputs"""
    return "", "Creative Writing", "Beginner", 1, ""

# Create the Gradio interface
with gr.Blocks(title="AI Prompt Generator", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🎯 AI Prompt Generator
        
        Generate high-quality prompts for AI assistants! Perfect for writers, developers, 
        marketers, and anyone who wants better AI interactions.
        """
    )
    
    with gr.Row():
        with gr.Column(scale=1):
            # Input components
            topic_input = gr.Textbox(
                label="Topic/Context",
                placeholder="Enter your topic... (e.g., 'social media marketing', 'creative writing', 'coding tutorials')",
                lines=2
            )
            
            prompt_type = gr.Dropdown(
                choices=[
                    "Creative Writing",
                    "Content Creation",
                    "Marketing & Sales",
                    "Code Generation",
                    "Analysis & Research",
                    "Educational",
                    "Problem Solving",
                    "Brainstorming",
                    "Role Playing",
                    "General Purpose"
                ],
                value="Creative Writing",
                label="Prompt Type",
                info="What kind of prompts do you need?"
            )
            
            complexity = gr.Radio(
                choices=["Beginner", "Intermediate", "Advanced"],
                value="Intermediate",
                label="Complexity Level",
                info="How detailed should the prompts be?"
            )
            
            num_prompts = gr.Slider(
                minimum=1,
                maximum=5,
                step=1,
                value=3,
                label="Number of Prompts",
                info="How many different prompts to generate?"
            )
            
            with gr.Row():
                generate_btn = gr.Button("Generate Prompts", variant="primary")
                clear_btn = gr.Button("Clear", variant="secondary")
        
        with gr.Column(scale=2):
            # Output component
            prompts_output = gr.Textbox(
                label="Generated Prompts",
                lines=15,
                max_lines=25,
                show_copy_button=True,
                placeholder="Your generated prompts will appear here..."
            )
    
    # Example inputs
    gr.Markdown("### 💡 Example Topics:")
    example_topics = [
        ["Instagram post captions", "Content Creation", "Intermediate", 2],
        ["Python debugging help", "Code Generation", "Advanced", 1], 
        ["Blog post ideas", "Creative Writing", "Beginner", 3],
        ["Customer service responses", "Problem Solving", "Intermediate", 2],
        ["Product descriptions", "Marketing & Sales", "Advanced", 1]
    ]
    
    examples = gr.Examples(
        examples=example_topics,
        inputs=[topic_input, prompt_type, complexity, num_prompts]
    )
    
    # Tips section
    with gr.Accordion("💡 Tips for Better Results", open=False):
        gr.Markdown("""
        **For better prompt generation:**
        - Be specific about your topic (e.g., "email marketing for small businesses" vs just "marketing")
        - Choose the right prompt type for your use case
        - Start with "Intermediate" complexity for most needs
        - Generate multiple prompts to get variety
        
        **Example topics that work well:**
        - "LinkedIn content for tech startups"
        - "Creative writing prompts for sci-fi stories"  
        - "Python code review and optimization"
        - "Social media crisis management"
        """)
    
    # Event handlers
    generate_btn.click(
        fn=generate_prompts,
        inputs=[topic_input, prompt_type, complexity, num_prompts],
        outputs=prompts_output
    )
    
    clear_btn.click(
        fn=clear_inputs,
        outputs=[topic_input, prompt_type, complexity, num_prompts, prompts_output]
    )
    
    # Allow Enter key to generate prompts
    topic_input.submit(
        fn=generate_prompts,
        inputs=[topic_input, prompt_type, complexity, num_prompts],
        outputs=prompts_output
    )

# Launch the app
if __name__ == "__main__":
    demo.launch(
        share=True,  # Creates a public link you can share
        debug=True   # Shows detailed error messages
    )
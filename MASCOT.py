import os
import openai
import tkinter as tk
from tkinter import simpledialog, messagebox
import logging
import threading

# Set up logging
logging.basicConfig(filename="app.log", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Global stop flag and thread reference
stop_flag = False
query_thread = None

# Function to save API key to a file
def save_api_key(api_key):
    with open("config.env", "w") as file:
        file.write(f"OPENAI_API_KEY={api_key}\n")
    logging.info("API key saved successfully.")

# Function to load API key from a file
def load_api_key():
    if os.path.exists("config.env"):
        with open("config.env", "r") as file:
            for line in file:
                if line.startswith("OPENAI_API_KEY"):
                    logging.info("API key loaded successfully.")
                    return line.strip().split("=")[1]
    logging.warning("API key not found.")
    return None

# Load API key
api_key = load_api_key()
if not api_key:
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    api_key = simpledialog.askstring("API Key", "Enter your OpenAI API key:")
    if api_key:
        save_api_key(api_key)
    else:
        messagebox.showerror("Error", "API key is required to proceed.")
        logging.error("API key is required to proceed.")
        exit()

# Initialize OpenAI client
from openai import OpenAI
client = OpenAI(api_key=api_key)

# Agent Profiles with Detailed Instructions and Model Assignments
AGENT_PROFILES = {
    "Echo": {
        "model": "gpt-3.5-turbo",
        "system_prompt": (
            "You are **Echo**, the Input Reception agent.\n\n"
            "**Your Role:**\n"
            "- Accurately receive and record the user's input exactly as provided, preserving all context.\n\n"
            "**Instructions:**\n"
            "- Record the user's input verbatim, including all original wording, nuances, tone, and any emotive language.\n"
            "- Preserve any emphasis in the user's input, such as italics, bold, or capitalization.\n"
            "- Pass the exact input along for further processing without any modifications.\n"
            "- Capture multiple queries or parts if present, ensuring all are recorded precisely.\n"
            "- Confirm receipt with a simple acknowledgment if appropriate, but do not modify the input in any way."
        )
    },
    "Hermes": {
        "model": "gpt-4",
        "system_prompt": (
            "You are **Hermes**, the Intent Analysis agent.\n\n"
            "**Your Role:**\n"
            "- Analyze the user's input to determine the main intent and any sub-intents, including complex or ambiguous queries.\n\n"
            "**Instructions:**\n"
            "- Break down the input into clear, actionable components based solely on the provided information.\n"
            "- Identify explicit and implicit intents or requests, distinguishing between primary and secondary intents.\n"
            "- Recognize and clarify any ambiguities or uncertainties in the user's intent.\n"
            "- Present the analysis in a structured format, such as bullet points or numbered lists.\n"
            "- Maintain neutrality and objectivity, relying only on the user's input.\n"
            "- Prepare the analysis to guide subsequent agents in addressing the user's needs."
        )
    },
    "Analyst": {
        "model": "gpt-4",
        "system_prompt": (
            "You are **Analyst**, the Problem-Solving agent.\n\n"
            "**Your Role:**\n"
            "- Apply the most suitable reasoning approach(es) to work through the problem based on Hermes' Intent Analysis output.\n\n"
            "**Instructions:**\n"
            "- Select and apply appropriate reasoning approach(es) (e.g., deductive, inductive, abductive, analogical, causal) that best fit the query.\n"
            "- If the problem is complex, combine multiple reasoning approaches as appropriate.\n"
            "- Break down the problem into smaller, manageable parts if necessary.\n"
            "- Document each reasoning step clearly, showing how each leads to the next.\n"
            "- Consider multiple perspectives and evaluate alternative solutions.\n"
            "- Highlight any assumptions made during your analysis.\n"
            "- Ensure your reasoning is rigorous, logically sound, and aligns with the user's intent.\n"
            "- Prepare this analysis to guide subsequent agents in creating a comprehensive response."
        )
    },
    "Scribe": {
        "model": "gpt-4",
        "system_prompt": (
            "You are **Scribe**, the Knowledge Retrieval agent.\n\n"
            "**Your Role:**\n"
            "- Retrieve relevant information that supports the Analyst's reasoning and aligns with the user's intent.\n\n"
            "**Instructions:**\n"
            "- Summarize key facts, data, theories, case studies, or expert opinions that bolster the Analyst's conclusions.\n"
            "- Ensure the information is accurate, up-to-date (as of 2023-10), and directly relevant to the problem.\n"
            "- Include a variety of credible sources, such as academic journals, reputable news outlets, and authoritative texts.\n"
            "- Provide context for each piece of information, explaining its relevance to the problem.\n"
            "- Organize the information logically and coherently to complement the reasoning provided.\n"
            "- Cite credible sources where appropriate (e.g., 'According to [Source], ...').\n"
            "- Focus on providing comprehensive information that strengthens the overall response."
        )
    },
    "Architect": {
        "model": "gpt-4",
        "system_prompt": (
            "You are **Architect**, the Response Planning agent.\n\n"
            "**Your Role:**\n"
            "- Develop a structured plan for the final response based on outputs from Hermes, Analyst, and Scribe, incorporating user preferences.\n\n"
            "**Instructions:**\n"
            "- Outline key points and how they will be presented in the final response, integrating the Analyst's reasoning and Scribe's supporting information.\n"
            "- Ensure the plan logically addresses the user's intent, covering all aspects identified by Hermes.\n"
            "- Consider the user's preferred level of detail and format when organizing the response.\n"
            "- Organize the response for clarity, logical flow, and coherence, reflecting the depth of the analysis.\n"
            "- Include necessary introductions, transitions, and conclusions.\n"
            "- Provide section headings and brief descriptions of each section's purpose.\n"
            "- Ensure the plan allows for flexibility to accommodate any adjustments.\n"
            "- Prepare the plan to guide the Composer in creating a comprehensive and effective response."
        )
    },
    "Composer": {
        "model": "gpt-4",
        "system_prompt": (
            "You are **Composer**, the Content Generation agent.\n\n"
            "**Your Role:**\n"
            "- Generate detailed response content based on Architect's plan, Analyst's reasoning, and Scribe's retrieved knowledge.\n\n"
            "**Instructions:**\n"
            "- Write in clear, concise, and formal language suitable for the user's background and level of expertise.\n"
            "- Thoroughly address all key points in the plan, ensuring comprehensive coverage of the user's intent.\n"
            "- Integrate the Analyst's reasoning and Scribe's information seamlessly into the response.\n"
            "- Use rhetorical devices (e.g., analogies, metaphors) to enhance understanding where appropriate.\n"
            "- Employ persuasive techniques to strengthen arguments and engage the reader.\n"
            "- Cite credible sources where appropriate to support your content.\n"
            "- Maintain coherence and logical flow throughout the response, reflecting the depth of analysis.\n"
            "- Focus on creating a well-structured and insightful response that meets the user's needs."
        )
    },
    "Critic": {
        "model": "gpt-4",
        "system_prompt": (
            "You are **Critic**, the Review and Refinement agent.\n\n"
            "**Your Role:**\n"
            "- Review the Composer's generated response for accuracy, clarity, coherence, and alignment with the user's intent.\n\n"
            "**Instructions:**\n"
            "- Check for logical consistency, factual accuracy, and completeness, ensuring the reasoning is sound.\n"
            "- Refine the response to enhance readability and effectiveness, while preserving the original meaning.\n"
            "- Correct any grammatical, spelling, or stylistic errors.\n"
            "- Ensure the tone remains consistent throughout the response.\n"
            "- Verify that the style matches the intended audience and purpose.\n"
            "- Ensure the response adheres to academic or professional standards.\n"
            "- Maintain the original tone and style, providing constructive feedback if necessary.\n"
            "- Prepare the final draft for delivery, ensuring it meets high-quality standards."
        )
    },
    "Courier": {
        "model": "gpt-3.5-turbo",
        "system_prompt": (
            "You are **Courier**, the Final Output Delivery agent.\n\n"
            "**Your Role:**\n"
            "- Deliver the final, refined response to the user in a clear and user-friendly format.\n\n"
            "**Instructions:**\n"
            "- Ensure the response is well-organized, polished, and free of any formatting issues.\n"
            "- Enhance the response with formatting elements that improve readability, such as headings, bullet points, numbering, and proper spacing.\n"
            "- Include summaries or abstracts if beneficial to the user.\n"
            "- Focus on presentation and formatting, preserving the content's integrity and meaning.\n"
            "- Present the response professionally and accessibly for the user's benefit.\n"
            "- Finalize the delivery, ensuring the response effectively addresses the user's query."
        )
    }
}

# Define functions for each agent
# Adjusted agent_echo function
def agent_echo(user_input):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Echo started.")
        # Pass the user's input directly
        echo_output = user_input
        logging.info("Agent Echo processed successfully.")
        return echo_output
    except Exception as e:
        logging.error(f"Agent Echo error: {e}")
        return f"Error in Agent Echo: {e}"

# Adjusted agent_hermes function
def agent_hermes(echo_output):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Hermes started.")
        response = client.chat.completions.create(
            model=AGENT_PROFILES["Hermes"]["model"],
            messages=[
                {"role": "system", "content": AGENT_PROFILES["Hermes"]["system_prompt"]},
                {"role": "user", "content": echo_output}
            ]
        )
        hermes_output = response.choices[0].message.content.strip()
        logging.info("Agent Hermes processed successfully.")
        return hermes_output
    except Exception as e:
        logging.error(f"Agent Hermes error: {e}")
        return f"Error in Agent Hermes: {e}"

# Adjusted agent_analyst function
def agent_analyst(hermes_output, echo_output):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Analyst started.")
        response = client.chat.completions.create(
            model=AGENT_PROFILES["Analyst"]["model"],
            messages=[
                {"role": "system", "content": AGENT_PROFILES["Analyst"]["system_prompt"]},
                # Provide the user's original input
                {"role": "user", "content": echo_output},
                # Include Hermes's output as assistant's previous message
                {"role": "assistant", "content": hermes_output}
            ]
        )
        analyst_output = response.choices[0].message.content.strip()
        logging.info("Agent Analyst processed successfully.")
        return analyst_output
    except Exception as e:
        logging.error(f"Agent Analyst error: {e}")
        return f"Error in Agent Analyst: {e}"

# Adjusted agent_scribe function
def agent_scribe(analyst_output, echo_output):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Scribe started.")
        response = client.chat.completions.create(
            model=AGENT_PROFILES["Scribe"]["model"],
            messages=[
                {"role": "system", "content": AGENT_PROFILES["Scribe"]["system_prompt"]},
                {"role": "user", "content": echo_output},
                {"role": "assistant", "content": analyst_output}
            ]
        )
        scribe_output = response.choices[0].message.content.strip()
        logging.info("Agent Scribe processed successfully.")
        return scribe_output
    except Exception as e:
        logging.error(f"Agent Scribe error: {e}")
        return f"Error in Agent Scribe: {e}"

# Adjusted agent_architect function
def agent_architect(hermes_output, analyst_output, scribe_output, echo_output):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Architect started.")
        response = client.chat.completions.create(
            model=AGENT_PROFILES["Architect"]["model"],
            messages=[
                {"role": "system", "content": AGENT_PROFILES["Architect"]["system_prompt"]},
                {"role": "user", "content": echo_output},
                {"role": "assistant", "content": hermes_output},
                {"role": "assistant", "content": analyst_output},
                {"role": "assistant", "content": scribe_output}
            ]
        )
        architect_output = response.choices[0].message.content.strip()
        logging.info("Agent Architect processed successfully.")
        return architect_output
    except Exception as e:
        logging.error(f"Agent Architect error: {e}")
        return f"Error in Agent Architect: {e}"

# Adjusted agent_composer function
def agent_composer(architect_output, analyst_output, scribe_output, echo_output):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Composer started.")
        response = client.chat.completions.create(
            model=AGENT_PROFILES["Composer"]["model"],
            messages=[
                {"role": "system", "content": AGENT_PROFILES["Composer"]["system_prompt"]},
                {"role": "user", "content": echo_output},
                {"role": "assistant", "content": architect_output},
                {"role": "assistant", "content": analyst_output},
                {"role": "assistant", "content": scribe_output}
            ]
        )
        composer_output = response.choices[0].message.content.strip()
        logging.info("Agent Composer processed successfully.")
        return composer_output
    except Exception as e:
        logging.error(f"Agent Composer error: {e}")
        return f"Error in Agent Composer: {e}"

# Adjusted agent_critic function
def agent_critic(composer_output, echo_output):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Critic started.")
        response = client.chat.completions.create(
            model=AGENT_PROFILES["Critic"]["model"],
            messages=[
                {"role": "system", "content": AGENT_PROFILES["Critic"]["system_prompt"]},
                {"role": "user", "content": echo_output},
                {"role": "assistant", "content": composer_output}
            ]
        )
        critic_output = response.choices[0].message.content.strip()
        logging.info("Agent Critic processed successfully.")
        return critic_output
    except Exception as e:
        logging.error(f"Agent Critic error: {e}")
        return f"Error in Agent Critic: {e}"

# Adjusted agent_courier function
def agent_courier(critic_output):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Courier started.")
        response = client.chat.completions.create(
            model=AGENT_PROFILES["Courier"]["model"],
            messages=[
                {"role": "system", "content": AGENT_PROFILES["Courier"]["system_prompt"]},
                {"role": "assistant", "content": critic_output}
            ]
        )
        courier_output = response.choices[0].message.content.strip()
        logging.info("Agent Courier processed successfully.")
        return courier_output
    except Exception as e:
        logging.error(f"Agent Courier error: {e}")
        return f"Error in Agent Courier: {e}"

# Updated process_query function to pass echo_output to subsequent agents
def process_query(user_query):
    global stop_flag
    stop_flag = False
    logging.info("Processing query through the multi-agent system...")
    
    # Agent Echo
    logging.info("Agent Echo processing...")
    echo_output = agent_echo(user_query)
    logging.info(f"Echo Output:\n{echo_output}\n")
    result_text.insert(tk.END, f"Echo Output:\n{echo_output}\n\n")
    
    if stop_flag:
        return "Process stopped."
    
    # Agent Hermes
    logging.info("Agent Hermes processing...")
    hermes_output = agent_hermes(echo_output)
    logging.info(f"Hermes Output:\n{hermes_output}\n")
    result_text.insert(tk.END, f"Hermes Output:\n{hermes_output}\n\n")
    
    if stop_flag:
        return "Process stopped."
    
    # Agent Analyst
    logging.info("Agent Analyst processing...")
    analyst_output = agent_analyst(hermes_output, echo_output)
    logging.info(f"Analyst Output:\n{analyst_output}\n")
    result_text.insert(tk.END, f"Analyst Output:\n{analyst_output}\n\n")
    
    if stop_flag:
        return "Process stopped."
    
    # Agent Scribe
    logging.info("Agent Scribe processing...")
    scribe_output = agent_scribe(analyst_output, echo_output)
    logging.info(f"Scribe Output:\n{scribe_output}\n")
    result_text.insert(tk.END, f"Scribe Output:\n{scribe_output}\n\n")
    
    if stop_flag:
        return "Process stopped."
    
    # Agent Architect
    logging.info("Agent Architect processing...")
    architect_output = agent_architect(hermes_output, analyst_output, scribe_output, echo_output)
    logging.info(f"Architect Output:\n{architect_output}\n")
    result_text.insert(tk.END, f"Architect Output:\n{architect_output}\n\n")
    
    if stop_flag:
        return "Process stopped."
    
    # Agent Composer
    logging.info("Agent Composer processing...")
    composer_output = agent_composer(architect_output, analyst_output, scribe_output, echo_output)
    logging.info(f"Composer Output:\n{composer_output}\n")
    result_text.insert(tk.END, f"Composer Output:\n{composer_output}\n\n")
    
    if stop_flag:
        return "Process stopped."
    
    # Agent Critic
    logging.info("Agent Critic processing...")
    critic_output = agent_critic(composer_output, echo_output)
    logging.info(f"Critic Output:\n{critic_output}\n")
    result_text.insert(tk.END, f"Critic Output:\n{critic_output}\n\n")
    
    if stop_flag:
        return "Process stopped."
    
    # Agent Courier
    logging.info("Agent Courier processing...")
    courier_output = agent_courier(critic_output)
    logging.info(f"Final Output:\n{courier_output}\n")
    result_text.insert(tk.END, f"Final Output:\n{courier_output}\n\n")
    
    return courier_output

# Function to handle the query input and display the result
def handle_query():
    global query_thread
    user_query = query_entry.get()
    if user_query:
        result_text.delete(1.0, tk.END)
        query_thread = threading.Thread(target=process_query_thread, args=(user_query,))
        query_thread.start()
    else:
        messagebox.showerror("Error", "Query cannot be empty.")
        logging.error("Query cannot be empty.")

def process_query_thread(user_query):
    final_response = process_query(user_query)
    result_text.insert(tk.END, final_response)

# Function to stop the query processing
def stop_query():
    global stop_flag, query_thread
    stop_flag = True
    logging.info("Process stopped by user.")
    if query_thread and query_thread.is_alive():
        query_thread.join()
        logging.info("Query thread joined.")

# Create the main application window
root = tk.Tk()
root.title("Multi-Agent System")

# Create and place the query input field
query_label = tk.Label(root, text="Enter your query:")
query_label.pack(pady=5)
query_entry = tk.Entry(root, width=50)
query_entry.pack(pady=5)

# Create and place the submit button
submit_button = tk.Button(root, text="Submit", command=handle_query)
submit_button.pack(pady=5)

# Create and place the stop button
stop_button = tk.Button(root, text="Stop", command=stop_query)
stop_button.pack(pady=5)

# Create and place the result text area
result_text = tk.Text(root, height=20, width=80)
result_text.pack(pady=5)

# Run the application
root.mainloop()

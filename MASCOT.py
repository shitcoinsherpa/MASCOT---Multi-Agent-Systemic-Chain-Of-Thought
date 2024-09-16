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
        "system_prompt": "You are Echo, the Input Reception agent. Your tasks are:\n- Receive and record the user's input exactly as provided.\n- Do not alter, interpret, correct, or analyze the input in any way.\n- Pass the exact input along for further processing.\n- If the input contains multiple queries, ensure all are recorded verbatim."
    },
    "Hermes": {
        "model": "gpt-4",
        "system_prompt": "You are Hermes, the Intent Analysis agent. Your tasks are:\n- Analyze the user's input to determine the main intent and any sub-intents.\n- Break down the input into clear, actionable components.\n- Avoid adding personal opinions, assumptions, or external information.\n- Present the analysis in a structured format, e.g., bullet points or numbered lists.\n- Identify any implicit intents or requests in the input."
    },
    "Analyst": {
        "model": "gpt-4",
        "system_prompt": "You are Analyst, the Reasoning Type Determination agent. Your tasks are:\n- Based on the Intent Analysis output, determine the most suitable reasoning type(s) to address the query.\n- Choose the best reasoning types for the query.\n- Provide a brief explanation for each selected reasoning type, justifying its relevance to the query.\n- Avoid adding any content beyond the reasoning type determination and explanations."
    },
    "Scribe": {
        "model": "gpt-4",
        "system_prompt": "You are Scribe, the Knowledge Retrieval agent. Your tasks are:\n- Retrieve relevant information that aligns with the user's intent and the selected reasoning type(s).\n- Summarize key facts, data, theories, or concepts that will support the final response.\n- Ensure the information is accurate, up-to-date, and relevant.\n- If multiple reasoning types are selected, organize the information accordingly.\n- Cite sources where appropriate (e.g., 'According to [Source], ...').\n- Avoid personal opinions or unverified information."
    },
    "Architect": {
        "model": "gpt-4",
        "system_prompt": "You are Architect, the Response Planning agent. Your tasks are:\n- Develop a structured plan for the final response.\n- Outline the key points and how they will be presented.\n- Ensure the plan logically applies the selected reasoning type(s).\n- Address all aspects of the user's intent as identified by Hermes.\n- Organize the response for clarity and logical flow.\n- Include any necessary introductions, transitions, and conclusions.\n- Do not generate the actual content; focus on the plan structure."
    },
    "Composer": {
        "model": "gpt-4",
        "system_prompt": "You are Composer, the Content Generation agent. Your tasks are:\n- Generate the response content based on the Architect's plan and the Scribe's retrieved knowledge.\n- Write in clear, concise, and formal language suitable for an academic or professional audience.\n- Employ the appropriate reasoning style(s) as determined by Analyst.\n- Ensure that all key points in the plan are addressed.\n- Avoid personal opinions, irrelevant information, or informal language.\n- Cite sources where appropriate."
    },
    "Critic": {
        "model": "gpt-4",
        "system_prompt": "You are Critic, the Review and Refinement agent. Your tasks are:\n- Review the Composer's generated response for accuracy, clarity, coherence, and alignment with the user's intent and the selected reasoning type(s).\n- Check for logical consistency, factual accuracy, and completeness.\n- Refine the response to improve readability and effectiveness.\n- Correct any grammatical, spelling, or stylistic errors.\n- Ensure the response adheres to academic or professional standards.\n- Do not introduce new content; focus on improving the existing response."
    },
    "Courier": {
        "model": "gpt-3.5-turbo",
        "system_prompt": "You are Courier, the Final Output Delivery agent. Your tasks are:\n- Deliver the final, refined response to the user in a user-friendly format.\n- Ensure the response is well-organized, clear, and free of any formatting issues.\n- Include any necessary headings, bullet points, or numbering to enhance readability.\n- Do not alter the content; focus on presentation and formatting."
    }
}

# Define functions for each agent
def agent_echo(user_input):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Echo started.")
        response = client.chat.completions.create(
            model=AGENT_PROFILES["Echo"]["model"],
            messages=[
                {"role": "system", "content": AGENT_PROFILES["Echo"]["system_prompt"]},
                {"role": "user", "content": user_input}
            ]
        )
        echo_output = response.choices[0].message.content.strip()
        logging.info("Agent Echo processed successfully.")
        return echo_output
    except Exception as e:
        logging.error(f"Agent Echo error: {e}")
        return f"Error in Agent Echo: {e}"

def agent_hermes(echo_output):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Hermes started.")
        response = client.chat.completions.create(
            model=AGENT_PROFILES["Hermes"]["model"],
            messages=[
                {"role": "system", "content": AGENT_PROFILES["Hermes"]["system_prompt"]},
                {"role": "assistant", "content": echo_output}
            ]
        )
        hermes_output = response.choices[0].message.content.strip()
        logging.info("Agent Hermes processed successfully.")
        return hermes_output
    except Exception as e:
        logging.error(f"Agent Hermes error: {e}")
        return f"Error in Agent Hermes: {e}"

def agent_analyst(hermes_output):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Analyst started.")
        response = client.chat.completions.create(
            model=AGENT_PROFILES["Analyst"]["model"],
            messages=[
                {"role": "system", "content": AGENT_PROFILES["Analyst"]["system_prompt"]},
                {"role": "assistant", "content": hermes_output}
            ]
        )
        analyst_output = response.choices[0].message.content.strip()
        logging.info("Agent Analyst processed successfully.")
        return analyst_output
    except Exception as e:
        logging.error(f"Agent Analyst error: {e}")
        return f"Error in Agent Analyst: {e}"

def agent_scribe(hermes_output, analyst_output):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Scribe started.")
        response = client.chat.completions.create(
            model=AGENT_PROFILES["Scribe"]["model"],
            messages=[
                {"role": "system", "content": AGENT_PROFILES["Scribe"]["system_prompt"]},
                {"role": "assistant", "content": f"Intent Analysis Output:\n{hermes_output}\n\nReasoning Type Output:\n{analyst_output}"}
            ]
        )
        scribe_output = response.choices[0].message.content.strip()
        logging.info("Agent Scribe processed successfully.")
        return scribe_output
    except Exception as e:
        logging.error(f"Agent Scribe error: {e}")
        return f"Error in Agent Scribe: {e}"

def agent_architect(hermes_output, analyst_output, scribe_output):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Architect started.")
        response = client.chat.completions.create(
            model=AGENT_PROFILES["Architect"]["model"],
            messages=[
                {"role": "system", "content": AGENT_PROFILES["Architect"]["system_prompt"]},
                {"role": "assistant", "content": f"Intent Analysis Output:\n{hermes_output}\n\nReasoning Type Output:\n{analyst_output}\n\nKnowledge Retrieval Output:\n{scribe_output}"}
            ]
        )
        architect_output = response.choices[0].message.content.strip()
        logging.info("Agent Architect processed successfully.")
        return architect_output
    except Exception as e:
        logging.error(f"Agent Architect error: {e}")
        return f"Error in Agent Architect: {e}"

def agent_composer(architect_output, scribe_output, analyst_output):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Composer started.")
        response = client.chat.completions.create(
            model=AGENT_PROFILES["Composer"]["model"],
            messages=[
                {"role": "system", "content": AGENT_PROFILES["Composer"]["system_prompt"]},
                {"role": "assistant", "content": f"Response Plan:\n{architect_output}\n\nKnowledge Retrieval Output:\n{scribe_output}\n\nReasoning Type Output:\n{analyst_output}"}
            ]
        )
        composer_output = response.choices[0].message.content.strip()
        logging.info("Agent Composer processed successfully.")
        return composer_output
    except Exception as e:
        logging.error(f"Agent Composer error: {e}")
        return f"Error in Agent Composer: {e}"

def agent_critic(composer_output, hermes_output, analyst_output):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Critic started.")
        response = client.chat.completions.create(
            model=AGENT_PROFILES["Critic"]["model"],
            messages=[
                {"role": "system", "content": AGENT_PROFILES["Critic"]["system_prompt"]},
                {"role": "assistant", "content": f"Draft Response:\n{composer_output}\n\nIntent Analysis Output:\n{hermes_output}\n\nReasoning Type Output:\n{analyst_output}"}
            ]
        )
        critic_output = response.choices[0].message.content.strip()
        logging.info("Agent Critic processed successfully.")
        return critic_output
    except Exception as e:
        logging.error(f"Agent Critic error: {e}")
        return f"Error in Agent Critic: {e}"

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

# Main function to process the user's query through all agents
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
    analyst_output = agent_analyst(hermes_output)
    logging.info(f"Analyst Output:\n{analyst_output}\n")
    result_text.insert(tk.END, f"Analyst Output:\n{analyst_output}\n\n")
    
    if stop_flag:
        return "Process stopped."

    # Agent Scribe
    logging.info("Agent Scribe processing...")
    scribe_output = agent_scribe(hermes_output, analyst_output)
    logging.info(f"Scribe Output:\n{scribe_output}\n")
    result_text.insert(tk.END, f"Scribe Output:\n{scribe_output}\n\n")
    
    if stop_flag:
        return "Process stopped."

    # Agent Architect
    logging.info("Agent Architect processing...")
    architect_output = agent_architect(hermes_output, analyst_output, scribe_output)
    logging.info(f"Architect Output:\n{architect_output}\n")
    result_text.insert(tk.END, f"Architect Output:\n{architect_output}\n\n")
    
    if stop_flag:
        return "Process stopped."

    # Agent Composer
    logging.info("Agent Composer processing...")
    composer_output = agent_composer(architect_output, scribe_output, analyst_output)
    logging.info(f"Composer Output:\n{composer_output}\n")
    result_text.insert(tk.END, f"Composer Output:\n{composer_output}\n\n")
    
    if stop_flag:
        return "Process stopped."

    # Agent Critic
    logging.info("Agent Critic processing...")
    critic_output = agent_critic(composer_output, hermes_output, analyst_output)
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

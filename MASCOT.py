import os
from openai import OpenAI
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import threading
import json
import requests
from tkinter.scrolledtext import ScrolledText

# Set up logging
logging.basicConfig(filename="app.log", level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Global variables
stop_flag = False
query_thread = None

# Configuration functions
def save_config(key, value):
    config = {}
    if os.path.exists("config.env"):
        with open("config.env", "r") as file:
            for line in file:
                if '=' in line:
                    k, v = line.strip().split('=', 1)
                    config[k] = v
    config[key] = value
    with open("config.env", "w") as file:
        for k, v in config.items():
            file.write(f"{k}={v}\n")
    logging.info(f"{key} saved successfully.")

def load_config(key):
    if os.path.exists("config.env"):
        with open("config.env", "r") as file:
            for line in file:
                if '=' in line:
                    k, v = line.strip().split('=', 1)
                    if k == key:
                        logging.info(f"{key} loaded successfully.")
                        return v
    logging.warning(f"{key} not found.")
    return None

# Application class
class MultiAgentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Multi-Agent System")
        self.configure_ui()
        self.load_api_keys()

    def configure_ui(self):
        # Use ttk for themed widgets
        self.style = ttk.Style(self)
        self.style.theme_use('default')

        # Create menu bar
        self.create_menu()

        # Create main frames
        self.create_main_frames()

        # Create widgets
        self.create_widgets()

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

    def create_main_frames(self):
        # Frame for query input
        self.input_frame = ttk.Frame(self)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Frame for buttons
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ns")

        # Frame for progress and status
        self.status_frame = ttk.Frame(self)
        self.status_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # Frame for results
        self.result_frame = ttk.Frame(self)
        self.result_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def create_widgets(self):
        # Query label and entry
        query_label = ttk.Label(self.input_frame, text="Enter your query:")
        query_label.pack(side=tk.LEFT, padx=(0, 5))
        self.query_entry = ttk.Entry(self.input_frame, width=60)
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Submit and Stop buttons
        submit_button = ttk.Button(self.button_frame, text="Submit", command=self.handle_query)
        submit_button.pack(side=tk.TOP, pady=(0, 5), fill=tk.X)
        stop_button = ttk.Button(self.button_frame, text="Stop", command=self.stop_query)
        stop_button.pack(side=tk.TOP, fill=tk.X)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)

        # Status label
        self.status_label = ttk.Label(self.status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)

        # ScrolledText for results
        self.result_text = ScrolledText(self.result_frame, height=20)
        self.result_text.pack(fill=tk.BOTH, expand=True)

    def open_settings(self):
        SettingsDialog(self)

    def handle_query(self):
        user_query = self.query_entry.get()
        if user_query:
            self.result_text.delete(1.0, tk.END)
            self.progress_var.set(0)
            self.status_label.config(text="Processing...")
            self.query_entry.config(state=tk.DISABLED)
            self.query_thread = threading.Thread(target=self.process_query_thread, args=(user_query,))
            self.query_thread.start()
        else:
            messagebox.showerror("Error", "Query cannot be empty.")
            logging.error("Query cannot be empty.")

    def process_query_thread(self, user_query):
        final_response = process_query(user_query, self)
        self.result_text.insert(tk.END, final_response)
        self.status_label.config(text="Completed")
        self.query_entry.config(state=tk.NORMAL)

    def stop_query(self):
        global stop_flag, query_thread
        stop_flag = True
        logging.info("Process stopped by user.")
        self.status_label.config(text="Stopped")
        if self.query_thread and self.query_thread.is_alive():
            self.query_thread.join()
            logging.info("Query thread joined.")
        self.query_entry.config(state=tk.NORMAL)

    def load_api_keys(self):
        # Load OpenAI API key
        self.api_key = load_config("OPENAI_API_KEY")
        if not self.api_key:
            self.open_settings()
            self.api_key = load_config("OPENAI_API_KEY")
            if not self.api_key:
                messagebox.showerror("Error", "OpenAI API key is required to proceed.")
                logging.error("OpenAI API key is required to proceed.")
                self.quit()
            else:
                self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = OpenAI(api_key=self.api_key)

        # Load Google API key and Search Engine ID
        self.google_api_key = load_config("GOOGLE_API_KEY")
        self.search_engine_id = load_config("SEARCH_ENGINE_ID")
        if not self.google_api_key or not self.search_engine_id:
            logging.warning("Google API key or Search Engine ID not provided. Scribe agent will not perform web searches.")

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        # OpenAI API Key
        ttk.Label(self, text="OpenAI API Key:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.openai_entry = ttk.Entry(self, width=50)
        self.openai_entry.grid(row=0, column=1, padx=5, pady=5)
        self.openai_entry.insert(0, load_config("OPENAI_API_KEY") or "")

        # Google API Key
        ttk.Label(self, text="Google API Key:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.google_entry = ttk.Entry(self, width=50)
        self.google_entry.grid(row=1, column=1, padx=5, pady=5)
        self.google_entry.insert(0, load_config("GOOGLE_API_KEY") or "")

        # Search Engine ID
        ttk.Label(self, text="Search Engine ID:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.search_engine_entry = ttk.Entry(self, width=50)
        self.search_engine_entry.grid(row=2, column=1, padx=5, pady=5)
        self.search_engine_entry.insert(0, load_config("SEARCH_ENGINE_ID") or "")

        # Buttons
        save_button = ttk.Button(self, text="Save", command=self.save_settings)
        save_button.grid(row=3, column=0, padx=5, pady=10)
        cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        cancel_button.grid(row=3, column=1, padx=5, pady=10)

    def save_settings(self):
        openai_key = self.openai_entry.get().strip()
        google_key = self.google_entry.get().strip()
        search_engine_id = self.search_engine_entry.get().strip()

        if openai_key:
            save_config("OPENAI_API_KEY", openai_key)
            self.parent.api_key = openai_key
            self.parent.client = OpenAI(api_key=openai_key)
        if google_key:
            save_config("GOOGLE_API_KEY", google_key)
            self.parent.google_api_key = google_key
        if search_engine_id:
            save_config("SEARCH_ENGINE_ID", search_engine_id)
            self.parent.search_engine_id = search_engine_id

        logging.info("Settings saved.")
        self.destroy()

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
            "- You have access to a function called `get_search_result(query)` to retrieve information from Google Search.\n"
            "- Use this function to obtain up-to-date and relevant information that supports the analysis.\n"
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

# Function to get search results from Google Search API
def get_search_result(api_key, search_engine_id, query, num_results=5):
    service_url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': query,
        'num': num_results,
    }
    response = requests.get(service_url, params=params)
    if response.status_code == 200:
        results = response.json()
        search_items = results.get('items', [])
        summaries = []
        for item in search_items:
            summaries.append({
                'title': item.get('title'),
                'snippet': item.get('snippet'),
                'link': item.get('link')
            })
        logging.info(f"Search results for query '{query}': {summaries}")
        return {'results': summaries}
    else:
        logging.error(
            f"Google Search API error: {response.status_code}, {response.text}")
        return {'error': f"Google Search API error: {response.status_code}, {response.text}"}

# Define functions for each agent
def agent_echo(user_input):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Echo started.")
        echo_output = user_input
        logging.info("Agent Echo processed successfully.")
        return echo_output
    except Exception as e:
        logging.error(f"Agent Echo error: {e}")
        return f"Error in Agent Echo: {e}"

def agent_hermes(client, echo_output):
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

def agent_analyst(client, hermes_output, echo_output):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Analyst started.")
        response = client.chat.completions.create(
            model=AGENT_PROFILES["Analyst"]["model"],
            messages=[
                {"role": "system", "content": AGENT_PROFILES["Analyst"]["system_prompt"]},
                {"role": "user", "content": echo_output},
                {"role": "assistant", "content": hermes_output}
            ]
        )
        analyst_output = response.choices[0].message.content.strip()
        logging.info("Agent Analyst processed successfully.")
        return analyst_output
    except Exception as e:
        logging.error(f"Agent Analyst error: {e}")
        return f"Error in Agent Analyst: {e}"

def agent_scribe(client, analyst_output, echo_output, app):
    if stop_flag:
        return "Process stopped."
    try:
        logging.info("Agent Scribe started.")

        functions = [
            {
                "name": "get_search_result",
                "description": "Get search results from Google Search API",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        }
                    },
                    "required": ["query"],
                },
            }
        ]

        response = client.chat.completions.create(
            model=AGENT_PROFILES["Scribe"]["model"],
            messages=[
                {"role": "system", "content": AGENT_PROFILES["Scribe"]["system_prompt"]},
                {"role": "user", "content": echo_output},
                {"role": "assistant", "content": analyst_output}
            ],
            functions=functions,
            function_call="auto"
        )

        message = response.choices[0].message
        if message.function_call:
            function_name = message.function_call.name
            arguments = message.function_call.arguments
            logging.info(f"Function call requested: {function_name} with arguments {arguments}")
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error: {e}")
                return f"Error in Agent Scribe: JSON decode error: {e}"

            if function_name == "get_search_result":
                query = arguments.get("query")
                logging.info(f"Performing search with query: {query}")
                if not app.google_api_key or not app.search_engine_id:
                    logging.warning("Google API key or Search Engine ID not provided. Skipping search.")
                    search_results = {'results': []}
                else:
                    search_results = get_search_result(
                        app.google_api_key, app.search_engine_id, query)
                    logging.info(f"Search results obtained for query '{query}'")

                messages = [
                    {"role": "system", "content": AGENT_PROFILES["Scribe"]["system_prompt"]},
                    {"role": "user", "content": echo_output},
                    {"role": "assistant", "content": analyst_output},
                    message.model_dump(),
                    {"role": "function", "name": function_name, "content": json.dumps(search_results)}
                ]

                second_response = client.chat.completions.create(
                    model=AGENT_PROFILES["Scribe"]["model"],
                    messages=messages
                )
                scribe_output = second_response.choices[0].message.content.strip()
                logging.info("Agent Scribe processed successfully.")
                return scribe_output
            else:
                logging.error(f"Unknown function: {function_name}")
                return f"Error in Agent Scribe: Unknown function: {function_name}"
        else:
            scribe_output = message.content.strip()
            logging.info("Agent Scribe processed successfully.")
            return scribe_output

    except Exception as e:
        logging.error(f"Agent Scribe error: {e}")
        return f"Error in Agent Scribe: {e}"

def agent_architect(client, hermes_output, analyst_output, scribe_output, echo_output):
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

def agent_composer(client, architect_output, analyst_output, scribe_output, echo_output):
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

def agent_critic(client, composer_output, echo_output):
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

def agent_courier(client, critic_output):
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

def process_query(user_query, app):
    global stop_flag
    stop_flag = False
    logging.info("Processing query through the multi-agent system...")

    total_agents = 8  # Total number of agents
    current_agent = 0

    client = app.client  # Use the client instance from the app

    # Agent Echo
    if stop_flag:
        return "Process stopped."
    app.status_label.config(text="Agent Echo processing...")
    logging.info("Agent Echo processing...")
    echo_output = agent_echo(user_query)
    logging.info(f"Echo Output:\n{echo_output}\n")
    app.result_text.insert(tk.END, f"Echo Output:\n{echo_output}\n\n")
    current_agent += 1
    app.progress_var.set((current_agent / total_agents) * 100)

    # Agent Hermes
    if stop_flag:
        return "Process stopped."
    app.status_label.config(text="Agent Hermes processing...")
    logging.info("Agent Hermes processing...")
    hermes_output = agent_hermes(client, echo_output)
    logging.info(f"Hermes Output:\n{hermes_output}\n")
    app.result_text.insert(tk.END, f"Hermes Output:\n{hermes_output}\n\n")
    current_agent += 1
    app.progress_var.set((current_agent / total_agents) * 100)

    # Agent Analyst
    if stop_flag:
        return "Process stopped."
    app.status_label.config(text="Agent Analyst processing...")
    logging.info("Agent Analyst processing...")
    analyst_output = agent_analyst(client, hermes_output, echo_output)
    logging.info(f"Analyst Output:\n{analyst_output}\n")
    app.result_text.insert(tk.END, f"Analyst Output:\n{analyst_output}\n\n")
    current_agent += 1
    app.progress_var.set((current_agent / total_agents) * 100)

    # Agent Scribe
    if stop_flag:
        return "Process stopped."
    app.status_label.config(text="Agent Scribe processing...")
    logging.info("Agent Scribe processing...")
    scribe_output = agent_scribe(client, analyst_output, echo_output, app)
    logging.info(f"Scribe Output:\n{scribe_output}\n")
    app.result_text.insert(tk.END, f"Scribe Output:\n{scribe_output}\n\n")
    current_agent += 1
    app.progress_var.set((current_agent / total_agents) * 100)

    # Agent Architect
    if stop_flag:
        return "Process stopped."
    app.status_label.config(text="Agent Architect processing...")
    logging.info("Agent Architect processing...")
    architect_output = agent_architect(client, hermes_output, analyst_output, scribe_output, echo_output)
    logging.info(f"Architect Output:\n{architect_output}\n")
    app.result_text.insert(tk.END, f"Architect Output:\n{architect_output}\n\n")
    current_agent += 1
    app.progress_var.set((current_agent / total_agents) * 100)

    # Agent Composer
    if stop_flag:
        return "Process stopped."
    app.status_label.config(text="Agent Composer processing...")
    logging.info("Agent Composer processing...")
    composer_output = agent_composer(client, architect_output, analyst_output, scribe_output, echo_output)
    logging.info(f"Composer Output:\n{composer_output}\n")
    app.result_text.insert(tk.END, f"Composer Output:\n{composer_output}\n\n")
    current_agent += 1
    app.progress_var.set((current_agent / total_agents) * 100)

    # Agent Critic
    if stop_flag:
        return "Process stopped."
    app.status_label.config(text="Agent Critic processing...")
    logging.info("Agent Critic processing...")
    critic_output = agent_critic(client, composer_output, echo_output)
    logging.info(f"Critic Output:\n{critic_output}\n")
    app.result_text.insert(tk.END, f"Critic Output:\n{critic_output}\n\n")
    current_agent += 1
    app.progress_var.set((current_agent / total_agents) * 100)

    # Agent Courier
    if stop_flag:
        return "Process stopped."
    app.status_label.config(text="Agent Courier processing...")
    logging.info("Agent Courier processing...")
    courier_output = agent_courier(client, critic_output)
    logging.info(f"Final Output:\n{courier_output}\n")
    app.result_text.insert(tk.END, f"Final Output:\n{courier_output}\n\n")
    current_agent += 1
    app.progress_var.set((current_agent / total_agents) * 100)

    return courier_output

if __name__ == "__main__":
    app = MultiAgentApp()
    app.mainloop()

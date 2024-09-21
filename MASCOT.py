import os
import json
import logging
import threading
import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import openai

# Set up logging
logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Global variables
stop_flag = False

# Default Agent Profiles

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
            "- Confirm receipt by repeating the user's query verbatim."
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
            "- Finalize the delivery, ensuring the response effectively addresses the user's query and the work of all prior agents."
        )
    }
}

class MultiAgentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Multi-Agent Systemic Chain of Thought")
        self.geometry("1000x700")

        self.agent_profiles_file = "agent_profiles.json"
        self.chat_history_file = "chat_history.json"
        self.config_file = "config.env"

        self.agent_profiles = AGENT_PROFILES.copy()
        self.chat_sessions = {}
        self.api_key = None
        self.google_api_key = None
        self.search_engine_id = None

        self.load_config()
        self.load_agent_profiles()
        self.create_menu()
        self.create_widgets()
        self.load_chat_history()

    def load_config(self):
        # Load from config.env
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        if key == "OPENAI_API_KEY":
                            self.api_key = value
                        elif key == "GOOGLE_API_KEY":
                            self.google_api_key = value
                        elif key == "SEARCH_ENGINE_ID":
                            self.search_engine_id = value
            if self.api_key:
                # Set OpenAI API key
                openai.api_key = self.api_key
                logging.info("OpenAI API key set.")
            else:
                logging.warning("OpenAI API key not found in config.env.")
        else:
            logging.info("No config.env file found.")

    def load_agent_profiles(self):
        if os.path.exists(self.agent_profiles_file):
            with open(self.agent_profiles_file, "r") as f:
                self.agent_profiles = json.load(f)
            logging.info("Agent profiles loaded from file.")
        else:
            logging.info("No agent profiles file found. Using default profiles.")

    def save_agent_profiles(self):
        with open(self.agent_profiles_file, "w") as f:
            json.dump(self.agent_profiles, f, indent=4)
        logging.info("Agent profiles saved to file.")

    def load_chat_history(self):
        if os.path.exists(self.chat_history_file):
            with open(self.chat_history_file, "r") as f:
                self.chat_sessions = json.load(f)
            logging.info("Chat sessions loaded.")
            # Populate the chat history listbox
            self.history_listbox.delete(0, tk.END)
            for title in self.chat_sessions.keys():
                self.history_listbox.insert(tk.END, title)
        else:
            logging.info("No chat history file found.")

    def save_chat_sessions(self):
        with open(self.chat_history_file, "w") as f:
            json.dump(self.chat_sessions, f, indent=4)
        logging.info("Chat sessions saved.")

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="New Session", command=self.start_new_session)
        file_menu.add_command(label="Export Chat", command=self.export_chat_history)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Profiles menu
        profiles_menu = tk.Menu(menubar, tearoff=0)
        profiles_menu.add_command(label="Manage Profiles", command=self.manage_profiles)
        menubar.add_cascade(label="Profiles", menu=profiles_menu)

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Chat history frame
        history_frame = ttk.Frame(main_frame)
        history_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        history_label = ttk.Label(history_frame, text="Chat History:")
        history_label.pack(anchor="w")

        self.history_listbox = tk.Listbox(history_frame, width=30)
        self.history_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.history_listbox.bind('<Double-Button-1>', self.open_chat_session)

        # Conversation display frame
        conversation_frame = ttk.Frame(main_frame)
        conversation_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        conversation_label = ttk.Label(conversation_frame, text="Conversation:")
        conversation_label.pack(anchor="w")

        self.conversation_text = ScrolledText(conversation_frame, wrap=tk.WORD, state='normal')
        self.conversation_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.conversation_text.configure(state='disabled')  # Make it read-only

        # Input frame
        input_frame = ttk.Frame(self)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.user_input = ttk.Entry(input_frame)
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_input.bind('<Return>', self.submit_query)

        # Added Stop button next to the Send button
        stop_button = ttk.Button(input_frame, text="Stop", command=self.stop_processing)
        stop_button.pack(side=tk.RIGHT, padx=(0, 10))

        send_button = ttk.Button(input_frame, text="Send", command=self.submit_query)
        send_button.pack(side=tk.RIGHT)

        # Progress bar
        self.progress = ttk.Progressbar(self, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=(0, 10))

    def open_settings(self):
        SettingsDialog(self)

    def manage_profiles(self):
        ProfilesDialog(self)

    def stop_processing(self):
        global stop_flag
        stop_flag = True
        self.progress.stop()
        logging.info("Processing stopped by user.")

    def start_new_session(self):
        global stop_flag
        stop_flag = False
        self.chat_sessions = {}
        self.history_listbox.delete(0, tk.END)
        self.conversation_text.configure(state='normal')
        self.conversation_text.delete(1.0, tk.END)
        self.conversation_text.configure(state='disabled')
        self.save_chat_sessions()
        logging.info("Started a new session.")

    def export_chat_history(self):
        file_path = filedialog.asksaveasfilename(
            title="Export Chat History",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, "w") as f:
                json.dump(self.chat_sessions, f, indent=4)
            messagebox.showinfo("Export Successful", f"Chat history exported to {file_path}.")

    def submit_query(self, event=None):
        user_query = self.user_input.get().strip()
        if not user_query:
            messagebox.showwarning("No Input", "Please enter a query to submit.")
            return
        self.user_input.delete(0, tk.END)
        # Generate title
        title = ' '.join(user_query.split()[:8])
        if title not in self.chat_sessions:
            self.chat_sessions[title] = []
            self.history_listbox.insert(tk.END, title)
        # Add user message to conversation
        self.chat_sessions[title].append({"role": "User", "message": user_query})
        self.update_conversation_display(title, "User", user_query)

        # Start processing in a new thread
        global stop_flag
        stop_flag = False
        self.progress.start()
        query_thread = threading.Thread(target=self.process_query, args=(title, user_query))
        query_thread.start()

    def add_conversation(self, agent_name, content):
        self.conversation_text.configure(state='normal')
        self.conversation_text.insert(tk.END, f"{agent_name}: {content}\n\n")
        self.conversation_text.see(tk.END)
        self.conversation_text.configure(state='disabled')
        # Find current session title
        current_sessions = list(self.chat_sessions.keys())
        if not current_sessions:
            return
        current_title = current_sessions[-1]
        # Add to chat session
        self.chat_sessions[current_title].append({"role": agent_name, "message": content})
        self.save_chat_sessions()

    def update_conversation_display(self, title, role, message):
        self.conversation_text.configure(state='normal')
        self.conversation_text.insert(tk.END, f"{role}: {message}\n\n")
        self.conversation_text.configure(state='disabled')
        self.conversation_text.see(tk.END)

    def process_query(self, title, user_query):
        global stop_flag
        try:
            # Echo Agent
            if stop_flag:
                logging.info("Processing stopped before Echo agent.")
                return
            echo = self.agent_echo(user_query)
        
            # Hermes Agent
            if stop_flag:
                logging.info("Processing stopped before Hermes agent.")
                return
            hermes = self.agent_hermes(echo)
        
            # Analyst Agent
            if stop_flag:
                logging.info("Processing stopped before Analyst agent.")
                return
            analyst = self.agent_analyst(hermes)
        
            # Scribe Agent
            if stop_flag:
                logging.info("Processing stopped before Scribe agent.")
                return
            scribe = self.agent_scribe(analyst)
        
            # Architect Agent
            if stop_flag:
                logging.info("Processing stopped before Architect agent.")
                return
            architect = self.agent_architect(echo, hermes, analyst, scribe)
        
            # Composer Agent
            if stop_flag:
                logging.info("Processing stopped before Composer agent.")
                return
            composer = self.agent_composer(architect, analyst, scribe)
        
            # Critic Agent
            if stop_flag:
                logging.info("Processing stopped before Critic agent.")
                return
            critic = self.agent_critic(composer)
        
            # Courier Agent
            if stop_flag:
                logging.info("Processing stopped before Courier agent.")
                return
            courier = self.agent_courier(critic)
        
            # Add final output to the conversation
            self.add_conversation("User", courier)
            logging.info("All agents processed successfully.")
        except Exception as e:
            logging.error(f"Error processing query: {e}")
            messagebox.showerror("Processing Error", f"An error occurred: {e}")
        finally:
            self.progress.stop()

    def agent_echo(self, user_query):
        try:
            profile = self.agent_profiles["Echo"]
            response = openai.chat.completions.create(
                model=profile["model"],
                messages=[
                    {"role": "system", "content": profile["system_prompt"]},
                    {"role": "user", "content": user_query}
                ]
            )
            echo_output = response.choices[0].message.content.strip()
            self.add_conversation("Echo", echo_output)
            logging.info("Agent Echo processed successfully.")
            return echo_output
        except Exception as e:
            logging.error(f"Error in Agent Echo: {e}")
            return f"Error in Agent Echo: {e}"

    def agent_hermes(self, echo_output):
        try:
            profile = self.agent_profiles["Hermes"]
            response = openai.chat.completions.create(
                model=profile["model"],
                messages=[
                    {"role": "system", "content": profile["system_prompt"]},
                    {"role": "user", "content": echo_output}
                ]
            )
            hermes_output = response.choices[0].message.content.strip()
            self.add_conversation("Hermes", hermes_output)
            logging.info("Agent Hermes processed successfully.")
            return hermes_output
        except Exception as e:
            logging.error(f"Error in Agent Hermes: {e}")
            return f"Error in Agent Hermes: {e}"

    def agent_analyst(self, hermes_output):
        try:
            profile = self.agent_profiles["Analyst"]
            response = openai.chat.completions.create(
                model=profile["model"],
                messages=[
                    {"role": "system", "content": profile["system_prompt"]},
                    {"role": "user", "content": hermes_output}
                ]
            )
            analyst_output = response.choices[0].message.content.strip()
            self.add_conversation("Analyst", analyst_output)
            logging.info("Agent Analyst processed successfully.")
            return analyst_output
        except Exception as e:
            logging.error(f"Error in Agent Analyst: {e}")
            return f"Error in Agent Analyst: {e}"

    def agent_scribe(self, analyst_output):
        try:
            profile = self.agent_profiles["Scribe"]
            search_query = analyst_output  # Assuming this is appropriate
            search_result = get_search_result(search_query, self.google_api_key, self.search_engine_id)
            response = openai.chat.completions.create(
                model=profile["model"],
                messages=[
                    {"role": "system", "content": profile["system_prompt"]},
                    {"role": "user", "content": search_result}
                ]
            )
            scribe_output = response.choices[0].message.content.strip()
            self.add_conversation("Scribe", scribe_output)
            logging.info("Agent Scribe processed successfully.")
            return scribe_output
        except Exception as e:
            logging.error(f"Error in Agent Scribe: {e}")
            return f"Error in Agent Scribe: {e}"

    def agent_architect(self, echo_output, hermes_output, analyst_output, scribe_output):
        try:
           profile = self.agent_profiles["Architect"]
           combined_input = (
                f"Echo Output:\n{echo_output}\n\n"
                f"Hermes Output:\n{hermes_output}\n\n"
                f"Analyst Output:\n{analyst_output}\n\n"
                f"Scribe Output:\n{scribe_output}"
            )
           response = openai.chat.completions.create(
                model=profile["model"],
                messages=[
                    {"role": "system", "content": profile["system_prompt"]},
                    {"role": "user", "content": combined_input}
                ]
            )
           architect_output = response.choices[0].message.content.strip()
           self.add_conversation("Architect", architect_output)
           logging.info("Agent Architect processed successfully.")
           return architect_output
        except Exception as e:
            logging.error(f"Error in Agent Architect: {e}")
            return f"Error in Agent Architect: {e}"

    def agent_composer(self, architect_output, analyst_output, scribe_output):
        try:
            profile = self.agent_profiles["Composer"]
            combined_input = (
                f"Architect Output:\n{architect_output}\n\n"
                f"Analyst Output:\n{analyst_output}\n\n"
                f"Scribe Output:\n{scribe_output}"
            )
            response = openai.chat.completions.create(
                model=profile["model"],
                messages=[
                    {"role": "system", "content": profile["system_prompt"]},
                    {"role": "user", "content": combined_input}
                ]
            )
            composer_output = response.choices[0].message.content.strip()
            self.add_conversation("Composer", composer_output)
            logging.info("Agent Composer processed successfully.")
            return composer_output
        except Exception as e:
            logging.error(f"Error in Agent Composer: {e}")
            return f"Error in Agent Composer: {e}"

    def agent_critic(self, composer_output):
        try:
            profile = self.agent_profiles["Critic"]
            response = openai.chat.completions.create(
                model=profile["model"],
                messages=[
                    {"role": "system", "content": profile["system_prompt"]},
                    {"role": "user", "content": composer_output}
                ]
            )
            critic_output = response.choices[0].message.content.strip()
            self.add_conversation("Critic", critic_output)
            logging.info("Agent Critic processed successfully.")
            return critic_output
        except Exception as e:
            logging.error(f"Error in Agent Critic: {e}")
            return f"Error in Agent Critic: {e}"

    def agent_courier(self, critic_output):
        try:
            profile = self.agent_profiles["Courier"]
            response = openai.chat.completions.create(
                model=profile["model"],
                messages=[
                    {"role": "system", "content": profile["system_prompt"]},
                    {"role": "user", "content": critic_output}
                ]
            )
            courier_output = response.choices[0].message.content.strip()
            self.add_conversation("Courier", courier_output)
            logging.info("Agent Courier processed successfully.")
            return courier_output
        except Exception as e:
            logging.error(f"Error in Agent Courier: {e}")
            return f"Error in Agent Courier: {e}"

    def open_chat_session(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            index = selection[0]
            title = self.history_listbox.get(index)
            history = self.chat_sessions.get(title, [])
            ChatHistoryPopup(self, title, history)

def get_search_result(query, api_key, search_engine_id):
    if not api_key or not search_engine_id:
        logging.error("Google API Key or Search Engine ID not provided.")
        return "Error: Google API Key or Search Engine ID not provided."

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()
        items = results.get("items", [])
        summary = ""
        for item in items[:3]:  # Get top 3 results
            title = item.get("title")
            snippet = item.get("snippet")
            link = item.get("link")
            summary += f"Title: {title}\nSnippet: {snippet}\nLink: {link}\n\n"
        logging.info("Search results retrieved successfully.")
        return summary.strip()
    except Exception as e:
        logging.error(f"Error fetching search results: {e}")
        return f"Error fetching search results: {e}"

class ProfilesDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Manage Agent Profiles")
        self.parent = parent
        self.agent_profiles = self.parent.agent_profiles
        self.create_widgets()
        self.geometry("800x600")

    def create_widgets(self):
        # Agent selection listbox
        listbox_frame = ttk.Frame(self)
        listbox_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(listbox_frame, text="Select Agent:").pack(anchor="w")
        self.agent_listbox = tk.Listbox(listbox_frame)
        self.agent_listbox.pack(fill=tk.BOTH, expand=True)
        for agent_name in self.agent_profiles.keys():
            self.agent_listbox.insert(tk.END, agent_name)
        self.agent_listbox.bind('<<ListboxSelect>>', self.on_agent_select)

        # Profile editing frame
        edit_frame = ttk.Frame(self)
        edit_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(edit_frame, text="Model:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.model_entry = ttk.Entry(edit_frame, width=50)
        self.model_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(edit_frame, text="System Prompt:").grid(row=1, column=0, padx=5, pady=5, sticky="ne")
        self.prompt_text = ScrolledText(edit_frame, width=50, height=20)
        self.prompt_text.grid(row=1, column=1, padx=5, pady=5)

        # Save and Cancel buttons
        button_frame = ttk.Frame(edit_frame)
        button_frame.grid(row=2, column=1, padx=5, pady=10, sticky="e")

        save_button = ttk.Button(button_frame, text="Save", command=self.save_profile)
        save_button.pack(side=tk.RIGHT, padx=5)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT)

        self.current_agent = None

    def on_agent_select(self, event):
        selection = self.agent_listbox.curselection()
        if selection:
            index = selection[0]
            agent_name = self.agent_listbox.get(index)
            self.current_agent = agent_name
            profile = self.agent_profiles[agent_name]
            self.model_entry.delete(0, tk.END)
            self.model_entry.insert(0, profile.get('model', ''))
            self.prompt_text.delete(1.0, tk.END)
            self.prompt_text.insert(tk.END, profile.get('system_prompt', ''))

    def save_profile(self):
        if self.current_agent:
            model = self.model_entry.get().strip()
            system_prompt = self.prompt_text.get(1.0, tk.END).strip()
            self.agent_profiles[self.current_agent]['model'] = model
            self.agent_profiles[self.current_agent]['system_prompt'] = system_prompt
            self.parent.save_agent_profiles()
            logging.info(f"Agent profile for {self.current_agent} saved.")
            messagebox.showinfo("Profile Saved", f"Profile for {self.current_agent} has been saved.")
        else:
            messagebox.showwarning("No Agent Selected", "Please select an agent to save.")

class ChatHistoryPopup(tk.Toplevel):
    def __init__(self, parent, title, history):
        super().__init__(parent)
        self.title(title)
        self.geometry("800x600")
        self.configure_ui(history)

    def configure_ui(self, history):
        history_text = ScrolledText(self, font=("Helvetica", 12), state='disabled', wrap='word')
        history_text.pack(fill=tk.BOTH, expand=True, pady=5)
        history_text.configure(state='normal')
        for entry in history:
            history_text.insert(tk.END, f"{entry['role']}: {entry['message']}\n\n")
        history_text.configure(state='disabled')

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.parent = parent
        self.create_widgets()
        self.geometry("600x400")

    def create_widgets(self):
        # OpenAI API Key
        ttk.Label(self, text="OpenAI API Key:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.openai_entry = ttk.Entry(self, width=50, show="*")
        self.openai_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.openai_entry.insert(0, self.parent.api_key or "")

        # Google API Key
        ttk.Label(self, text="Google API Key:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.google_entry = ttk.Entry(self, width=50, show="*")
        self.google_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.google_entry.insert(0, self.parent.google_api_key or "")

        # Search Engine ID
        ttk.Label(self, text="Search Engine ID:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.se_id_entry = ttk.Entry(self, width=50)
        self.se_id_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.se_id_entry.insert(0, self.parent.search_engine_id or "")

        # Save and Cancel buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=1, padx=10, pady=20, sticky="e")

        save_button = ttk.Button(button_frame, text="Save", command=self.save_settings)
        save_button.pack(side=tk.RIGHT, padx=5)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT)

    def save_settings(self):
        openai_key = self.openai_entry.get().strip()
        google_key = self.google_entry.get().strip()
        search_engine_id = self.se_id_entry.get().strip()

        if openai_key:
            self.parent.api_key = openai_key
            openai.api_key = openai_key
            self.parent.save_config("OPENAI_API_KEY", openai_key)
            logging.info("OpenAI API key updated.")
        if google_key:
            self.parent.google_api_key = google_key
            self.parent.save_config("GOOGLE_API_KEY", google_key)
            logging.info("Google API key updated.")
        if search_engine_id:
            self.parent.search_engine_id = search_engine_id
            self.parent.save_config("SEARCH_ENGINE_ID", search_engine_id)
            logging.info("Search Engine ID updated.")

        messagebox.showinfo("Settings Saved", "API keys and settings have been saved successfully.")
        self.destroy()

    def save_config(self, key, value):
        config_path = self.parent.config_file
        config = {}
        if os.path.exists(config_path):
            with open(config_path, "r") as file:
                for line in file:
                    if '=' in line:
                        k, v = line.strip().split('=', 1)
                        config[k] = v
        config[key] = value
        with open(config_path, "w") as file:
            for k, v in config.items():
                file.write(f"{k}={v}\n")
        logging.info(f"{key} saved successfully.")

def get_search_result(query, api_key, search_engine_id):
    if not api_key or not search_engine_id:
        logging.error("Google API Key or Search Engine ID not provided.")
        return "Error: Google API Key or Search Engine ID not provided."

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()
        items = results.get("items", [])
        summary = ""
        for item in items[:3]:  # Get top 3 results
            title = item.get("title")
            snippet = item.get("snippet")
            link = item.get("link")
            summary += f"Title: {title}\nSnippet: {snippet}\nLink: {link}\n\n"
        logging.info("Search results retrieved successfully.")
        return summary.strip()
    except Exception as e:
        logging.error(f"Error fetching search results: {e}")
        return f"Error fetching search results: {e}"

class ProfilesDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Manage Agent Profiles")
        self.parent = parent
        self.agent_profiles = self.parent.agent_profiles
        self.create_widgets()
        self.geometry("800x600")

    def create_widgets(self):
        # Agent selection listbox
        listbox_frame = ttk.Frame(self)
        listbox_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(listbox_frame, text="Select Agent:").pack(anchor="w")
        self.agent_listbox = tk.Listbox(listbox_frame)
        self.agent_listbox.pack(fill=tk.BOTH, expand=True)
        for agent_name in self.agent_profiles.keys():
            self.agent_listbox.insert(tk.END, agent_name)
        self.agent_listbox.bind('<<ListboxSelect>>', self.on_agent_select)

        # Profile editing frame
        edit_frame = ttk.Frame(self)
        edit_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(edit_frame, text="Model:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.model_entry = ttk.Entry(edit_frame, width=50)
        self.model_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(edit_frame, text="System Prompt:").grid(row=1, column=0, padx=5, pady=5, sticky="ne")
        self.prompt_text = ScrolledText(edit_frame, width=50, height=20)
        self.prompt_text.grid(row=1, column=1, padx=5, pady=5)

        # Save and Cancel buttons
        button_frame = ttk.Frame(edit_frame)
        button_frame.grid(row=2, column=1, padx=5, pady=10, sticky="e")

        save_button = ttk.Button(button_frame, text="Save", command=self.save_profile)
        save_button.pack(side=tk.RIGHT, padx=5)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT)

        self.current_agent = None

    def on_agent_select(self, event):
        selection = self.agent_listbox.curselection()
        if selection:
            index = selection[0]
            agent_name = self.agent_listbox.get(index)
            self.current_agent = agent_name
            profile = self.agent_profiles[agent_name]
            self.model_entry.delete(0, tk.END)
            self.model_entry.insert(0, profile.get('model', ''))
            self.prompt_text.delete(1.0, tk.END)
            self.prompt_text.insert(tk.END, profile.get('system_prompt', ''))

    def save_profile(self):
        if self.current_agent:
            model = self.model_entry.get().strip()
            system_prompt = self.prompt_text.get(1.0, tk.END).strip()
            self.agent_profiles[self.current_agent]['model'] = model
            self.agent_profiles[self.current_agent]['system_prompt'] = system_prompt
            self.parent.save_agent_profiles()
            logging.info(f"Agent profile for {self.current_agent} saved.")
            messagebox.showinfo("Profile Saved", f"Profile for {self.current_agent} has been saved.")
        else:
            messagebox.showwarning("No Agent Selected", "Please select an agent to save.")

class ChatHistoryPopup(tk.Toplevel):
    def __init__(self, parent, title, history):
        super().__init__(parent)
        self.title(title)
        self.geometry("800x600")
        self.configure_ui(history)

    def configure_ui(self, history):
        history_text = ScrolledText(self, font=("Helvetica", 12), state='disabled', wrap='word')
        history_text.pack(fill=tk.BOTH, expand=True, pady=5)
        history_text.configure(state='normal')
        for entry in history:
            history_text.insert(tk.END, f"{entry['role']}: {entry['message']}\n\n")
        history_text.configure(state='disabled')

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.parent = parent
        self.create_widgets()
        self.geometry("600x400")

    def create_widgets(self):
        # OpenAI API Key
        ttk.Label(self, text="OpenAI API Key:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.openai_entry = ttk.Entry(self, width=50, show="*")
        self.openai_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.openai_entry.insert(0, self.parent.api_key or "")

        # Google API Key
        ttk.Label(self, text="Google API Key:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.google_entry = ttk.Entry(self, width=50, show="*")
        self.google_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.google_entry.insert(0, self.parent.google_api_key or "")

        # Search Engine ID
        ttk.Label(self, text="Search Engine ID:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.se_id_entry = ttk.Entry(self, width=50)
        self.se_id_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.se_id_entry.insert(0, self.parent.search_engine_id or "")

        # Save and Cancel buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=1, padx=10, pady=20, sticky="e")

        save_button = ttk.Button(button_frame, text="Save", command=self.save_settings)
        save_button.pack(side=tk.RIGHT, padx=5)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT)

    def save_settings(self):
        openai_key = self.openai_entry.get().strip()
        google_key = self.google_entry.get().strip()
        search_engine_id = self.se_id_entry.get().strip()

        if openai_key:
            self.parent.api_key = openai_key
            openai.api_key = openai_key
            self.parent.save_config("OPENAI_API_KEY", openai_key)
            logging.info("OpenAI API key updated.")
        if google_key:
            self.parent.google_api_key = google_key
            self.parent.save_config("GOOGLE_API_KEY", google_key)
            logging.info("Google API key updated.")
        if search_engine_id:
            self.parent.search_engine_id = search_engine_id
            self.parent.save_config("SEARCH_ENGINE_ID", search_engine_id)
            logging.info("Search Engine ID updated.")

        messagebox.showinfo("Settings Saved", "API keys and settings have been saved successfully.")
        self.destroy()

    def save_config(self, key, value):
        config_path = self.parent.config_file
        config = {}
        if os.path.exists(config_path):
            with open(config_path, "r") as file:
                for line in file:
                    if '=' in line:
                        k, v = line.strip().split('=', 1)
                        config[k] = v
        config[key] = value
        with open(config_path, "w") as file:
            for k, v in config.items():
                file.write(f"{k}={v}\n")
        logging.info(f"{key} saved successfully.")

def get_search_result(query, api_key, search_engine_id):
    if not api_key or not search_engine_id:
        logging.error("Google API Key or Search Engine ID not provided.")
        return "Error: Google API Key or Search Engine ID not provided."

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()
        items = results.get("items", [])
        summary = ""
        for item in items[:3]:  # Get top 3 results
            title = item.get("title")
            snippet = item.get("snippet")
            link = item.get("link")
            summary += f"Title: {title}\nSnippet: {snippet}\nLink: {link}\n\n"
        logging.info("Search results retrieved successfully.")
        return summary.strip()
    except Exception as e:
        logging.error(f"Error fetching search results: {e}")
        return f"Error fetching search results: {e}"

if __name__ == "__main__":
    app = MultiAgentApp()
    app.mainloop()

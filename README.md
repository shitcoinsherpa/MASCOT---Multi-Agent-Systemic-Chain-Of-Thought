"""
# MASCOT: Multi-Agent Systemic Chain Of Thought

MASCOT is a sophisticated multi-agent system that leverages OpenAI's GPT models to process user queries through a series of specialized agents. Each agent performs a specific role in understanding, analyzing, researching, and generating comprehensive responses to user inputs. The system is designed to provide detailed, accurate, and well-structured answers by simulating a collaborative workflow among virtual agents.



https://github.com/user-attachments/assets/818d0224-6322-4972-8a01-297c91ed5552

## Features

- **Multi-Agent Architecture**: Simulates a team of agents, each with a unique role, working together to process queries.
- **Integration with OpenAI GPT Models**: Utilizes both GPT-4 and GPT-3.5-turbo models for different agents.
- **Knowledge Retrieval**: Incorporates Google Search API for real-time data retrieval.
- **User-Friendly Interface**: Provides a graphical user interface (GUI) built with Tkinter for ease of use.
- **Progress Tracking**: Displays real-time progress and detailed outputs from each agent.
- **Customizable Settings**: Allows users to input their API keys and configure settings within the application.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Agents Overview](#agents-overview)
- [API Configuration](#api-configuration)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before running MASCOT, ensure you have the following:

- **Python 3.7 or higher** installed on your Windows system.
- **OpenAI API Key**: Sign up at [OpenAI](https://platform.openai.com/) to obtain your API key.
- **Google API Key and Search Engine ID** (optional but recommended for full functionality):
  - Obtain a Google API Key from the [Google Cloud Console](https://console.cloud.google.com/).
  - Create a Custom Search Engine ID via the [Programmable Search Engine](https://cse.google.com/cse/all).

## Installation

Follow these steps to install and run MASCOT on Windows:

### 1. Clone the Repository

\`\`\`bash
git clone https://github.com/yourusername/mascot.git
cd mascot
\`\`\`

### 2. Install Python Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

**Note:** If you don't have \`pip\` added to your PATH, you might need to specify the full path to \`pip\`.

### 3. Create a \`config.env\` File

You can create a \`config.env\` file to store your API keys, or you can enter them via the application's settings interface.

### 4. Run the Application

\`\`\`bash
python MASCOT.py
\`\`\`

## Usage

1. **Launch the Application**: Run \`MASCOT.py\` as described above.
2. **Enter API Keys**: Upon first run, go to \`File\` > \`Settings\` and input your OpenAI API key, and optionally your Google API key and Search Engine ID.
3. **Enter a Query**: Type your question or prompt into the input field.
4. **Submit**: Click the \`Submit\` button to start the multi-agent processing.
5. **Monitor Progress**: View the progress bar and status updates for each agent.
6. **View Results**: The output from each agent will be displayed in the results area.

**Example Query:**

\`\`\`
What are the latest advancements in renewable energy technologies?
\`\`\`

## Agents Overview

MASCOT processes queries through a series of specialized agents:

1. **Echo**: Records the user's input verbatim.
2. **Hermes**: Analyzes the intent of the query.
3. **Analyst**: Applies reasoning to solve the problem.
4. **Scribe**: Retrieves relevant information using the Google Search API.
5. **Architect**: Plans the structure of the final response.
6. **Composer**: Generates detailed content.
7. **Critic**: Reviews and refines the content.
8. **Courier**: Delivers the final, formatted response.

## API Configuration

### OpenAI API Key

- Required for the application to function.
- **How to Obtain**: Sign up at [OpenAI](https://platform.openai.com/) and generate an API key.

### Google API Key and Search Engine ID

- Optional but necessary for the Scribe agent to perform web searches.
- **Google API Key**:
  - Go to the [Google Cloud Console](https://console.cloud.google.com/).
  - Create a new project if you don't have one.
  - Navigate to \`APIs & Services\` > \`Credentials\`.
  - Click \`Create credentials\` > \`API key\`.
- **Search Engine ID**:
  - Visit [Programmable Search Engine](https://cse.google.com/cse/all).
  - Create a new search engine and note the Search Engine ID.

**Entering API Keys in MASCOT:**

1. Open the application.
2. Go to \`File\` > \`Settings\`.
3. Enter your API keys in the respective fields.
4. Click \`Save\`.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes with clear messages.
4. Submit a pull request to the \`main\` branch.

## License

This project is licensed under the [MIT License](LICENSE).

---

*Disclaimer: This software is provided "as is", without warranty of any kind.*
"""

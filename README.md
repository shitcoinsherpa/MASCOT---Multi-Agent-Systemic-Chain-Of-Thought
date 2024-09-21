# MASCOT: Multi-Agent Systemic Chain Of Thought

MASCOT is a sophisticated multi-agent system that leverages OpenAI's GPT models to process user queries through a series of specialized agents. Each agent performs a specific role in understanding, analyzing, researching, and generating comprehensive responses to user inputs. The system is designed to provide detailed, accurate, and well-structured answers by simulating a collaborative workflow among virtual agents.

## Features

- **Multi-Agent Architecture**: Utilizes a team of agents, each with a unique role, using the OpenAI api.
- **Integration with OpenAI GPT Models**: Utilizes both GPT-4 and GPT-3.5-turbo models for different agents.
- **Knowledge Retrieval**: Incorporates Google Search API for real-time data retrieval.
- **User-Friendly Interface**: Provides a graphical user interface (GUI) built with Tkinter for ease of use.
- **Progress Tracking**: Displays real-time progress and detailed outputs from each agent.
- **Customizable Settings**: Allows users to input their API keys and configure settings within the application.
- **Customizable Agent profiles and GPT models to use.

https://github.com/user-attachments/assets/818d0224-6322-4972-8a01-297c91ed5552

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Windows Installation](#windows-installation)
    - [Option 1: Use Pre-built Executable](#option-1-use-pre-built-executable)
    - [Option 2: Build Executable Yourself](#option-2-build-executable-yourself)
  - [Other Operating Systems](#other-operating-systems)
- [Usage](#usage)
- [Agents Overview](#agents-overview)
- [API Configuration](#api-configuration)
  - [OpenAI API Key](#openai-api-key)
  - [Google API Key and Search Engine ID](#google-api-key-and-search-engine-id)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before running MASCOT, ensure you have the following:

- **Python 3.7 or higher** installed on your system.
- **OpenAI API Key**: Sign up at [OpenAI](https://platform.openai.com/signup/) to obtain your API key.
- **Google API Key** and **Search Engine ID** (optional but recommended for full functionality):
  - Obtain a Google API Key from the [Google Cloud Console](https://console.cloud.google.com/).
  - Create a Custom Search Engine ID via the [Programmable Search Engine](https://cse.google.com/cse/all).

## Installation

### Windows Installation

#### Option 1: Use Pre-built Executable

Download the latest release from the [Releases](https://github.com/shitcoinsherpa/MASCOT---Multi-Agent-Systemic-Chain-Of-Thought/releases) page, which includes a pre-built executable for Windows users.

1. **Download the Installer**: Navigate to the [Releases](https://github.com/shitcoinsherpa/MASCOT---Multi-Agent-Systemic-Chain-Of-Thought/releases) page and download the `mascot.exe` file.
2. **Run the Installer**: Double-click the downloaded `mascot.exe` file and follow the on-screen instructions to install MASCOT on your system.

#### Option 2: Build Executable Yourself

If you prefer to build the executable yourself, follow these steps:

1. **Install Python 3.7 or Higher**

   Download and install Python from the [official website](https://www.python.org/downloads/windows/). Ensure that you check the option **"Add Python to PATH"** during installation.

2. **Clone the Repository**

   Open Command Prompt and execute:

   ```bash
   git clone https://github.com/yourusername/mascot.git
   cd mascot
   ```

3. **Install Required Dependencies**

   Install the necessary Python packages:

   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `config.env` File**

   - In the `mascot` directory, create a new file named `config.env`.
   - Open `config.env` with a text editor (e.g., Notepad).
   - Add the following lines, replacing `your_openai_api_key`, `your_google_api_key`, and `your_search_engine_id` with your actual keys:

     ```
     OPENAI_API_KEY=your_openai_api_key
     GOOGLE_API_KEY=your_google_api_key
     SEARCH_ENGINE_ID=your_search_engine_id
     ```

   - Save and close the file.

   **Note**: The `GOOGLE_API_KEY` and `SEARCH_ENGINE_ID` are optional but recommended for full functionality. If you prefer, you can skip this step and enter your API keys through the application's settings interface after launching.

5. **Install PyInstaller**

   Install PyInstaller to build the executable:

   ```bash
   pip install pyinstaller
   ```

6. **Create the Executable**

   Run the following command to build the executable without a console window:

   ```bash
   pyinstaller --noconsole --onefile mascot.py
   ```

   - PyInstaller will generate an executable file in the `dist` folder named `mascot.exe`.

7. **Run the Application**

   - Navigate to the `dist` folder:

     ```bash
     cd dist
     ```

   - Double-click the `mascot.exe` file to launch the application.

### Other Operating Systems

For users on **macOS** or **Linux**, follow these steps to run MASCOT:

1. **Ensure Python 3.7 or Higher is Installed**

   - **macOS**: Python 3 can be installed via [Homebrew](https://brew.sh/):

     ```bash
     brew install python
     ```

   - **Linux**: Use your distribution's package manager. For example, on Ubuntu:

     ```bash
     sudo apt-get update
     sudo apt-get install python3 python3-pip
     ```

2. **Clone the Repository**

   Open Terminal and execute:

   ```bash
   git clone https://github.com/yourusername/mascot.git
   cd mascot
   ```

3. **Install Required Dependencies**

   Install the necessary Python packages:

   ```bash
   pip3 install -r requirements.txt
   ```

4. **Create a `config.env` File**

   - In the `mascot` directory, create a new file named `config.env`:

     ```bash
     touch config.env
     ```

   - Open `config.env` with a text editor (e.g., `nano`, `vim`).

   - Add the following lines, replacing `your_openai_api_key`, `your_google_api_key`, and `your_search_engine_id` with your actual keys:

     ```
     OPENAI_API_KEY=your_openai_api_key
     GOOGLE_API_KEY=your_google_api_key
     SEARCH_ENGINE_ID=your_search_engine_id
     ```

   - Save and close the file.

   **Note**: The `GOOGLE_API_KEY` and `SEARCH_ENGINE_ID` are optional. You can enter your API keys through the application's settings interface after launching.

5. **Run the Application**

   ```bash
   python3 mascot.py
   ```

## Usage

1. **Launch the Application**

   - **Windows**:
     - If you used **Option 1**, launch MASCOT from the Start Menu or desktop shortcut.
     - If you used **Option 2**, navigate to the `dist` folder and double-click `mascot.exe`.
   - **macOS/Linux**:
     - Run `python3 mascot.py` in the terminal from the `mascot` directory.

2. **Enter API Keys (If Not Using `config.env`)**

   - Upon first run, go to **File** > **Settings**.
   - Enter your **OpenAI API Key**. This is required for MASCOT to function.
   - Optionally, enter your **Google API Key** and **Search Engine ID** to enable the Scribe agent's web search capabilities.
   - Click **Save**.

3. **Enter a Query**

   - Type your question or prompt into the input field at the bottom of the application window.

4. **Submit the Query**

   - Click the **Send** button or press **Enter** to start the multi-agent processing.

5. **Monitor Progress**

   - A progress bar will indicate the processing status.
   - Outputs from each agent will be displayed in the conversation area.

6. **View Results**

   - The final, formatted response will be delivered by the **Courier** agent.
   - Previous conversations can be accessed from the **Chat History** panel on the left.

**Example Query:**

What are the latest advancements in renewable energy technologies?


## Agents Overview

MASCOT processes queries through a series of specialized agents:

1. **Echo**

   - **Role**: Records the user's input verbatim.
   - **Function**: Ensures the original query is captured accurately.

2. **Hermes**

   - **Role**: Analyzes the intent of the query.
   - **Function**: Breaks down the input to understand the main intent and any sub-intents.

3. **Analyst**

   - **Role**: Applies reasoning to solve the problem.
   - **Function**: Uses appropriate reasoning approaches to work through the problem.

4. **Scribe**

   - **Role**: Retrieves relevant information using the Google Search API.
   - **Function**: Gathers up-to-date information to support the analysis.

5. **Architect**

   - **Role**: Plans the structure of the final response.
   - **Function**: Develops a structured plan based on the outputs of previous agents.

6. **Composer**

   - **Role**: Generates detailed content.
   - **Function**: Creates the comprehensive response content.

7. **Critic**

   - **Role**: Reviews and refines the content.
   - **Function**: Ensures accuracy, clarity, and coherence in the response.

8. **Courier**

   - **Role**: Delivers the final, formatted response.
   - **Function**: Presents the response to the user in a clear and user-friendly format.

Each agent builds upon the outputs of the previous agents to provide a comprehensive and accurate response.

## API Configuration

### OpenAI API Key

- **Required** for the application to function.

#### How to Obtain

1. **Sign Up**: Create an account at [OpenAI](https://platform.openai.com/signup/).
2. **Navigate to API Keys**: Go to the [API Keys](https://platform.openai.com/account/api-keys) section.
3. **Create a New Secret Key**: Click **Create new secret key**.
4. **Copy Your API Key**: Save this key securely; you won't be able to view it again.

### Google API Key and Search Engine ID

- **Optional**, but necessary for the **Scribe** agent to perform web searches.

#### Google API Key

1. **Go to Google Cloud Console**: [Google Cloud Console](https://console.cloud.google.com/).
2. **Create a New Project** (if necessary):
   - Click on the project dropdown and select **New Project**.
   - Enter a project name and click **Create**.
3. **Enable Custom Search API**:
   - Navigate to **APIs & Services** > **Library**.
   - Search for **Custom Search API** and click **Enable**.
4. **Create Credentials**:
   - Go to **APIs & Services** > **Credentials**.
   - Click **Create credentials** > **API key**.
   - Copy the generated API key.

#### Search Engine ID

1. **Visit Programmable Search Engine**: [Programmable Search Engine](https://cse.google.com/cse/all).
2. **Create a New Search Engine**:
   - Click **Add**.
   - In **Sites to search**, enter `www.google.com` to search the entire web.
   - Click **Create**.
3. **Retrieve the Search Engine ID**:
   - Under your new search engine, click **Control Panel**.
   - Your **Search Engine ID** is displayed at the top.

### Entering API Keys in MASCOT

You can provide your API keys in two ways:

#### Option 1: Using `config.env` File

- As described in the [Installation](#installation) section, add your API keys to the `config.env` file in the application directory.

#### Option 2: Through the Application Settings

1. **Open MASCOT**.
2. **Go to**: **File** > **Settings**.
3. **Enter Your API Keys**:
   - **OpenAI API Key**: Paste your key into the corresponding field.
   - **Google API Key** and **Search Engine ID**: Enter these if you wish to enable web search functionality.
4. **Save**: Click **Save** to store your configuration.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**

   - Navigate to the [MASCOT repository](https://github.com/shitcoinsherpa/MASCOT---Multi-Agent-Systemic-Chain-Of-Thought) on GitHub.
   - Click on the **Fork** button to create a copy of the repository under your GitHub account.

2. **Clone Your Fork**

   ```bash
   git clone https://github.com/yourusername/mascot.git
   cd mascot
   ```

3. **Create a New Branch**

   ```bash
   git checkout -b your-feature-branch
   ```

4. **Make Your Changes**

   - Implement your feature or fix.
   - Ensure your code follows the existing style and conventions.

5. **Commit Your Changes**

   ```bash
   git add .
   git commit -m "Add your commit message here"
   ```

6. **Push Changes to Your Fork**

   ```bash
   git push origin your-feature-branch
   ```

7. **Submit a Pull Request**

   - Go to the original repository on GitHub.
   - Click on **Pull Requests**.
   - Click **New Pull Request**.
   - Select your branch and submit the pull request with a detailed description.

## License

This project is licensed under the [MIT License](LICENSE).

---

**Disclaimer**: This software is provided "as is", without warranty of any kind.

---

**Note**: If you encounter any issues or have questions, please open an [issue](https://github.com/shitcoinsherpa/MASCOT---Multi-Agent-Systemic-Chain-Of-Thought/issues) on GitHub.

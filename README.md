# CIwA: Collective Intelligence with Agents
🚧 _WORK IN PROGRESS_ 🚧

## Overview
CIwA is a general-use collective intelligence framework that allows AI agents to deliberate in a way to utilize and demonstrate collective intelligence, with entry points for collective intelligence from a community of human participants.

The key components of a CIwA Process are:
- **Sessions**: A single "round" of Participants reviewing Topics, creating Submissions for each Topic, and voting on Submissions
- **Topics**: A question or prompt instructing what the Submissions are for or responding to. (Ex: "What is the meaning of life?")
- **Submissions**: A response to a particular Topic created by a Participant
- **Votes**: A reaction by a Participant to a Submission according to some criteria
- **Participants**: Human or an LLM Agent participating in the process by creating submissions and voting
- **VotingMethods**: The methodology used to collect and aggregate votes on submissions

A **Process** runs one or more **Sessions**, synchronously.

A **Session** asks for feedback on one or more **Topics**, asynchronously.

Each **Topic** has a **VotingManager** that implements a particular **VotingMethod** to gather a particular kind of **Vote** on each **Submission** and process the aggregate result of all **Votes**.

In a **Session**, **Participants** are prompted to _produce_ and submit up to _N_ **Submissions **per . (**LLMAgentParticipants** generate _N_ submissions concurrently.)

**Submissions** are added to a **Topic’s** submission queue.

**Participants** review **Submissions** in a **Topic’s** submission queue, producing **Votes** for each **Submission** concurrently as they come into the queue.

A **VotingManager** handles the processing of **Votes** based on the particular **VotingMethod** assigned to the **Topic**.

**VotingResults** for all **Topics** are saved to a file or returned to the **Session**. The Process concludes or continues with any pending sessions.


## Key Components

### Configuration
- **ConfigManager**: Handles the loading and management of configuration settings from a YAML file.

### Participants
- **Participant**: Abstract base class for all participants, providing the interface for generating submissions and votes.
- **LLMAgentParticipant**: Base class for all LLM participants. Produces dummy data for testing if instantiated.
- **ConversableAgentParticipant**: Concrete implementation of an LLMAgentParticipant that uses [Microsoft's AutoGen framework]([url](https://microsoft.github.io/autogen/)) to instantiate an LLM agent.

### Submissions
- **Submission**: Represents a submission made by a participant on a particular topic.

### Voting
- **VotingMethod**: Abstract base class for all voting methods.
- **LabelVotingMethod**: Abstract base class for voting methods for "labeling" individual submissions with some kind of "label" vote without comparison to any other submisison.
- **CompareVotingMethod**: Abstract base class for voting methods that handle votes comparing all submissions.
- **VotingManager**: Manages the voting process, interacts with participants to collect votes according to the VotingMethod assigned to the Topic.

### Factories
- **ParticipantFactory**: Creates participants based on configuration.
- **SessionFactory**: Creates sessions based on configuration.
- **ProcessFactory**: Creates processes based on configuration.


# Getting Started

Follow these steps to set up and run the CIwA module.

### Prerequisites

- Ensure you have Python 3.7+ installed. You can download Python from [python.org](https://www.python.org/downloads/).

### Clone the Repository

First, clone the repository to your local machine using git:

```bash
git clone https://github.com/collect-intel/ciwa.git
cd ciwa
```

### Install Requirements

Next, install the required Python packages from the `requirements.txt` file. It's recommended to use a virtual environment:

1. **Create a virtual environment** (optional but recommended):

    ```bash
    python -m venv venv
    ```

2. **Activate the virtual environment**:

    ```bash
    source venv/bin/activate
    ```

3. **Install the required packages**:

    ```bash
    pip install -r requirements.txt
    ```

### Configure the API Key

You need to configure your OpenAI API key or add your own model configurations.

1. **Copy the example configuration file**:

    ```bash
    cp ciwa/config/OAI_CONFIG_LIST.example.json ciwa/config/OAI_CONFIG_LIST.json
    ```

2. **Edit the `OAI_CONFIG_LIST.json` file** and replace `{YOUR_API_KEY}` with your OpenAI API key, or add your own model configurations. The file should look something like this:

    ```json
    [
        {
            "model": "gpt-4",
            "api_key": "sk-your-openai-api-key",
            "tags": ["gpt-4", "openai"]
        },
        {
            "model": "gpt-3.5-turbo",
            "api_key": "sk-your-openai-api-key",
            "tags": ["gpt-3.5", "openai"]
        }
    ]
    ```

### Adjust Settings

You can tweak any settings in the `settings.yaml` file located in the `ciwa/config/` directory. Open the file in a text editor and adjust the configurations as needed.

### Run the Process

Finally, run the process using the following command:

```bash
python -m ciwa.models.process
```

This will start and run the CIwA process using the configurations and models specified.

### Results
Results are saved for each Session in a file: `Session_<session.uuid>.json`.
Logging output is saved by default to `output.log`.


## Usage
1. **Configuration**: Define your settings in `settings.yaml`.
2. **Initialize Process**: Create a process using the `ProcessFactory`.
3. **Run Sessions**: Use the `Session` class to manage and run discussion sessions.

Alternatively, explore using CIwA in a Python Notebook by going through any of the examples in `notebooks`.

### Using Jupyter Notebooks
Use Jupyter to run any of the example notebooks provided.

1. **Install Jupyter Notebook**:

    ```bash
    pip install jupyter
    ```

2. **Run Jupyter Notebook**:

    ```bash
    jupyter notebook
    ```

3. **Open the Notebook**:

    This will open a new tab in your default web browser. Open the `notebooks` folder where the `.ipynb` files are located and click on the notebook you want to open.


## Code Example

Here is a basic usage example:

```python
import asyncio
from ciwa.config.config_manager import ConfigManager
from ciwa.models.process import ProcessFactory

async def main():
    config_manager = ConfigManager.get_instance("ciwa/config/settings.yaml")
    process = ProcessFactory.create_process()
    await process.init_process()
    await process.run_all_sessions()
    process.conclude_process()

if __name__ == "__main__":
    asyncio.run(main())

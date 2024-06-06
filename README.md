# CIwA (Collaborative Intelligence with Agents)
(WORK IN PROGRESS)

## Overview

CIwA is a collaborative intelligence system designed to facilitate discussions and decision-making processes using both human and AI participants. The architecture supports flexible voting strategies.

## Key Components

### Configuration
- **ConfigManager**: Handles the loading and management of configuration settings from a YAML file.

### Participants
- **Participant**: Abstract base class for all participants, providing the interface for generating submissions and votes.
- **LLMAgentParticipant**: Concrete implementation of a participant using a language model to generate submissions and votes.

### Submissions
- **Submission**: Represents a submission made by a participant on a particular topic.

### Voting
- **Vote**: Abstract base class representing a general vote.
- **IndependentVote**: Abstract class for votes on individual submissions.
- **ComparativeVote**: Abstract class for votes comparing multiple submissions.
- **BinaryVote**: Concrete implementation of an independent vote (e.g., approve/disapprove).
- **RankedVote**: Concrete implementation of a comparative vote (e.g., ranked order).

### Voting Strategies
- **VotingStrategy**: Abstract base class for all voting strategies.
- **IndependentVotingStrategy**: Abstract base class for strategies that handle votes on individual submissions.
- **ComparativeVotingStrategy**: Abstract base class for strategies that handle votes comparing multiple submissions.
- **SimpleMajority**: Concrete implementation of an independent voting strategy using a simple majority rule.

### Voting Management
- **VotingManager**: Manages the voting process, interacts with participants to collect votes according to the strategy.

### Factories
- **ParticipantFactory**: Creates participants based on configuration.
- **VoteFactory**: Creates votes based on the specified type.
- **SessionFactory**: Creates sessions based on configuration.
- **ProcessFactory**: Creates processes based on configuration.

## Usage

1. **Configuration**: Define your settings in `settings.yaml`.
2. **Initialize Process**: Create a process using the `ProcessFactory`.
3. **Run Sessions**: Use the `Session` class to manage and run discussion sessions.

Run using
```shell
python -m ciwa.models.process
```

## Example

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

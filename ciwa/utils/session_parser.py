# utils/session_parser.py

"""
This script provides a robust way to parse the Session JSON data into pandas DataFrames,
which are ideal for data analysis and manipulation in a Python notebook. 
"""
from typing import Dict, Union
from pathlib import Path
import argparse
import glob
import os
import json
import pandas as pd


def parse_session_json(json_data: Union[str, Path, Dict]) -> Dict[str, pd.DataFrame]:
    """
    Parse a Session JSON file or dictionary and create pandas DataFrames for participants,
    topics, submissions, and votes.

    Args:
        json_data (Union[str, Path, Dict]): Path to the JSON file, or a dictionary containing
        the JSON data.

    Returns:
        Dict[str, pd.DataFrame]: A dictionary containing DataFrames for 'participants', 'topics',
                                 'submissions', and 'votes'.
    """
    # Load JSON data if a file path is provided
    if isinstance(json_data, (str, Path)):
        with open(json_data, "r") as f:
            data = json.load(f)
    elif isinstance(json_data, dict):
        data = json_data
    else:
        raise ValueError("Invalid input type. Expected string, Path, or dictionary.")

    # Extract session data
    session = data["session"]
    session_id = session["uuid"]

    # Create participants DataFrame
    participants_df = pd.DataFrame(data["participants"])

    # Create topics DataFrame
    topics = []
    for topic in data["topics"]:
        topic_data = {
            "uuid": topic["uuid"],
            "session_uuid": session_id,
            "title": topic["title"],
            "description": topic["description"],
            "voting_method": topic["voting_method"],
        }
        topics.append(topic_data)
    topics_df = pd.DataFrame(topics)

    # Create submissions DataFrame
    submissions = []
    votes = []
    for topic in data["topics"]:
        topic_id = topic["uuid"]
        for submission in topic["submissions"]:
            submission_data = {
                "uuid": submission["uuid"],
                "topic_uuid": topic_id,
                "participant_uuid": submission["participant_uuid"],
                "content": submission["content"],
                "created_at": submission["created_at"],
            }
            submissions.append(submission_data)

            # Add aggregated results if available
            if (
                "voting_results" in topic
                and "aggregated_results" in topic["voting_results"]
            ):
                for result in topic["voting_results"]["aggregated_results"][
                    "submissions"
                ]:
                    if result["uuid"] == submission["uuid"]:
                        submission_data["aggregated_result"] = result["result"]
                        break

        # Extract votes
        if (
            "voting_results" in topic
            and "voting_participants" in topic["voting_results"]
        ):
            for vote in topic["voting_results"]["voting_participants"]:
                vote_data = {
                    "participant_uuid": vote["uuid"],
                    "topic_uuid": topic_id,
                    "created_at": vote["vote"]["created_at"],
                    "vote": json.dumps(
                        vote["vote"]["vote"]
                    ),  # Store vote as JSON string
                }
                votes.append(vote_data)

    submissions_df = pd.DataFrame(submissions)
    votes_df = pd.DataFrame(votes)

    return {
        "participants": participants_df,
        "topics": topics_df,
        "submissions": submissions_df,
        "votes": votes_df,
    }


def get_most_recent_session_file() -> str:
    """
    Find the most recently created file matching the pattern 'Session_*_results.json'
    in the current directory.

    Returns:
        str: Path to the most recent session file.
    """
    files = glob.glob("Session_*_results.json")
    if not files:
        raise FileNotFoundError("No session files found in the current directory.")
    return max(files, key=os.path.getctime)


# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a Session JSON file.")
    parser.add_argument(
        "file_path", nargs="?", help="Path to the Session JSON file (optional)"
    )
    args = parser.parse_args()

    if args.file_path:
        file_path = args.file_path
    else:
        try:
            file_path = get_most_recent_session_file()
            print(f"Using the most recent session file: {file_path}")
        except FileNotFoundError as e:
            print(e)
            exit(1)

    tables = parse_session_json(file_path)

    for name, df in tables.items():
        print(f"\n{name.capitalize()} Table:")
        print(df.head())
        print(f"\nColumns: {df.columns.tolist()}")
        print(f"Shape: {df.shape}")

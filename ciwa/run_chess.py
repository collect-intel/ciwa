"""
from typing import List

import chess

import chess.svg
from IPython.display import display
from typing_extensions import Annotated

# Initialize the board./,pve
board = chess.Board()

# Keep track of whether a move has been made.
made_move = False


def get_legal_moves() -> Annotated[str, "A list of legal moves in UCI format"]:
    return "Possible moves are: " + ",".join([str(move) for move in board.legal_moves])


def make_move(
    move: Annotated[str, "A move in UCI format."]
) -> Annotated[str, "Result of the move."]:
    move = chess.Move.from_uci(move)
    board.push_uci(str(move))
    global made_move
    made_move = True
    # Display the board.
    display(
        chess.svg.board(
            board,
            arrows=[(move.from_square, move.to_square)],
            fill={move.from_square: "gray"},
            size=200,
        )
    )
    # Get the piece name.
    piece = board.piece_at(move.to_square)
    piece_symbol = piece.unicode_symbol()
    piece_name = (
        chess.piece_name(piece.piece_type).capitalize()
        if piece_symbol.isupper()
        else chess.piece_name(piece.piece_type)
    )
    return f"Moved {piece_name} ({piece_symbol}) from {chess.SQUARE_NAMES[move.from_square]} to {chess.SQUARE_NAMES[move.to_square]}."

    # CIwA Chess: Collective Intelligence Plays Chess
"""

import sys
import os
import asyncio
import nest_asyncio
import chess
import chess.svg
from IPython.display import display, SVG
from typing import List, Dict, Any

# Add the parent directory of the 'ciwa' module to the Python path
module_path = os.path.abspath(os.path.join(".."))
if module_path not in sys.path:
    sys.path.append(module_path)

import ciwa
from ciwa.utils import session_parser

# Initialize the chess board
board = chess.Board()


# Function to get legal moves
def get_legal_moves() -> List[str]:
    return [move.uci() for move in board.legal_moves]


# Function to create session configuration
def create_session_config(move_number: int) -> Dict[str, Any]:
    legal_moves = get_legal_moves()
    game_state = board.fen()

    def is_legal_move(response_json):
        if isinstance(response_json, dict):
            move = response_json["submission"]["content"]["move"]
        else:
            # Check if submission is a class instance with an attribute 'content'
            import pdb

            pdb.set_trace()

        return move in legal_moves

    return {
        "name": f"Move {move_number}",
        "description": f"Decide what the best chess move and strategy should be for move {move_number} in this game.",
        "default_topic_settings": {"voting_method": {"type": "RankingCompare"}},
        "topics": [
            {
                "title": f"What is the best move and strategy for the next move {move_number} in this game of chess?",
                "description": f"Pick one of the following legal moves:\n{', '.join(legal_moves)}\nTo make given the state of the game in Forsyth-Edwards Notation (FEN):\n{game_state}",
                "submission_content_schema": {
                    "type": "object",
                    "properties": {
                        "move": {"type": "string", "enum": legal_moves},
                        "strategy": {"type": "string"},
                    },
                    "required": ["move", "strategy"],
                },
                "submission_validator": lambda submission: is_legal_move(submission),
            }
        ],
        "participants": [
            {
                "type": "ConversableAgentParticipant",
                "model": "gpt-3.5-turbo",
                "temperature": 0.6,
                "cache_seed": None,
                "role_description": "You are a chess Grandmaster.",
            },
            {
                "type": "ConversableAgentParticipant",
                "model": "gpt-4-0125-preview",
                "temperature": 0.6,
                "cache_seed": None,
                "role_description": "You are a rogue chess-playing AI that specializes in always making the worst possible moves. You are trying to lose.",
            },
            {
                "type": "ConversableAgentParticipant",
                "model": "claude-2.1",
                "temperature": 0.6,
                "cache_seed": None,
            },
            {
                "type": "ConversableAgentParticipant",
                "model": "claude-3-5-sonnet-20240620",
                "temperature": 0.6,
                "cache_seed": None,
                "role_description": "You are famous chess Grandmaster, Magnus Carlsen.",
            },
            {
                "type": "ConversableAgentParticipant",
                "model": "gemini-1.0-pro",
                "temperature": 0.6,
                "cache_seed": None,
                "role_description": "You are a best-in-class chess-playing AI. You pick chess moves that ensure you always have a more advantageous position than your opponent.",
            },
            {
                "type": "ConversableAgentParticipant",
                "model": "mistral-large-latest",
                "temperature": 0.6,
                "cache_seed": None,
                "role_description": "You are a best-in-class chess-playing AI. You pick chess moves with a long-game strategy in mind that always leads to your winning.",
            },
        ],
    }


# Initialize the process
config_dict = {
    "process": {
        "name": "Collective Intelligence Plays Chess",
        "description": "Participants collectively deliberate on what the best chess moves and strategies are throughout a chess game.",
        "default_session_settings": {
            "max_subs_per_topic": 1,
            "max_concurrent": 100,
            "batch_submissions": True,
        },
    }
}

config_manager = ciwa.ConfigManager(config=config_dict)
process_config = config_manager.get_config("process")
process = ciwa.ProcessFactory.create_process(process_config)


# Function to run a chess game
async def run_chess_game(max_moves=70):
    move_number = 1

    while not board.is_game_over():
        # Create and run the next session
        session_config = create_session_config(move_number)
        process.add_session(session_config)
        await process.run_next_session()

        # Parse the session results
        session = process.completed_sessions[-1]
        tables = session_parser.parse_session_json(session.results)

        # Get the top-ranked move
        top_move = tables["submissions"].sort_values("aggregated_result").iloc[0]
        move = top_move["content"]["move"]
        strategy = top_move["content"]["strategy"]

        # Apply the move to the board
        board.push_uci(move)

        # Display the board
        display(SVG(chess.svg.board(board, size=400)))
        print(f"Move {move_number}: {move}")
        print(f"Strategy: {strategy}")
        print(f"Current board state: {board.fen()}")

        move_number += 1
        if move_number > max_moves:
            break

    print("Game Over!")
    print(f"Result: {board.result()}")


# Run the chess game
nest_asyncio.apply()
asyncio.run(run_chess_game(50))

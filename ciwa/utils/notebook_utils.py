# utils/notebook_utils.py

from ciwa.models.session import Session
from IPython.display import display, JSON
import matplotlib.pyplot as plt
import networkx as nx


def visualize_session(session: Session) -> None:
    """
    Visualize the session's topics and submissions using a network graph.

    Args:
        session (Session): The session to visualize.
    """
    G = nx.DiGraph()

    for topic in session.topics:
        G.add_node(topic.title, label=topic.title)
        for submission in topic.submissions:
            G.add_edge(topic.title, submission.content[:30])

    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=3000,
        node_color="skyblue",
        font_size=10,
        font_weight="bold",
    )
    plt.title("Session Topics and Submissions")
    plt.show()


def display_results(session: Session) -> None:
    """
    Display the session results in a JSON format in the Jupyter notebook.

    Args:
        session (Session): The session whose results are to be displayed.
    """
    display(JSON(session.results))

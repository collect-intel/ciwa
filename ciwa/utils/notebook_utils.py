from ciwa.models.session import Session
from IPython.display import display, JSON, display_markdown
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
            char_limit = 100
            submission_content = (
                f"{submission.content[:char_limit]}..."
                if len(submission.content) > char_limit
                else f"{submission.content}"
            )
            G.add_edge(topic.title, submission_content)

    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=1000,
        node_color="skyblue",
        font_size=9,
        font_weight="bold",
    )
    plt.title("Session Topics and Submissions")
    plt.show()


def display_results(session: Session, aggregated_only: bool = False) -> None:
    """
    Display the session results in a JSON format in the Jupyter notebook.

    Args:
        session (Session): The session whose results are to be displayed.
        aggregated_only (bool): If True, display only the text of submissions and their aggregated_results 'result' value.
    """
    if aggregated_only:
        for topic in session.results["topics"]:
            display_markdown(
                f"### **Topic**: {topic['title']}\n\n**Description**: {topic['description']}",
                raw=True,
            )
            submissions = {sub["uuid"]: sub["content"] for sub in topic["submissions"]}

            for submission_result in topic["voting_results"]["aggregated_results"][
                "submissions"
            ]:
                submission_uuid = submission_result["uuid"]
                display_markdown(
                    f"- **Submission UUID**: {submission_uuid}\n   - **Submission**: {submissions[submission_uuid]}\n   - **{topic["voting_method"]} Result**: {submission_result['result']}",
                    raw=True,
                )
    else:
        display(JSON(session.results))

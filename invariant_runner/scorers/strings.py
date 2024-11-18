import openai
import re
from nltk.metrics.distance import edit_distance
from invariant_runner.scorers.utils.embeddings import cosine_similarity, _get_embedding


def levenshtein(str1: str, str2: str) -> int:
    """Compute the normalized score using Levenshtein (edit) distance between two strings
    as 1 - distance / max(len(str1), len(str2)).
    """
    if len(str1) == 0 or len(str2) == 0:
        return 1.0 if str1 == str2 else 0.0
    edit_dist = edit_distance(str1, str2)
    return 1 - edit_dist / max(len(str1), len(str2))


def embedding_similarity(str1: str, str2: str) -> float:
    """Compute cosine similarity between two text strings."""
    v1 = _get_embedding(str1)
    v2 = _get_embedding(str2)
    return cosine_similarity(v1, v2)


def contains(text: str, pattern: str) -> bool:
    """Check if a text contains a regex pattern."""
    return re.search(pattern, text) is not None


def llm(prompt: str, options: list[str]) -> str:
    """Ask a LLM to select the best option from a list of options."""
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content
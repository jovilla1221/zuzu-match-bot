from typing import List, Set
import numpy as np


def compute_cosine_similarity(tags1: List[str], tags2: List[str]) -> float:
    """
    Computes cosine similarity between two sets of interest tags (0.0 to 1.0).
    """
    if not tags1 or not tags2:
        return 0.0

    set1, set2 = set(tags1), set(tags2)
    all_tags = sorted(list(set1.union(set2)))
    if not all_tags:
        return 0.0

    v1 = np.array([1.0 if t in set1 else 0.0 for t in all_tags])
    v2 = np.array([1.0 if t in set2 else 0.0 for t in all_tags])

    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    dot_product = np.dot(v1, v2)
    return float(dot_product / (norm1 * norm2))


def calculate_compatibility_score(
    user_tags: List[str],
    candidate_tags: List[str],
    user_age: int,
    candidate_age: int,
    w_rule: float = 0.4,
    w_content: float = 0.6,
) -> float:
    """
    Calculates overall compatibility score percentage (0.0% to 100.0%).
    - Hard rule score (0 or 1 based on age difference < 15 years)
    - Content score (cosine similarity of interests)
    """
    age_diff = abs(user_age - candidate_age) if (user_age and candidate_age) else 5
    rule_score = 1.0 if age_diff <= 15 else 0.5

    content_score = compute_cosine_similarity(user_tags, candidate_tags)
    
    total_score = (w_rule * rule_score + w_content * content_score) * 100.0
    return round(total_score, 1)

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import silhouette_score
from scipy.stats import entropy

# ----------------------------
# 1. Normalized Learning Gain
# ----------------------------
def normalized_learning_gain(pre, post):
    pre = np.array(list(pre.values()))
    post = np.array(list(post.values()))
    return np.mean((post - pre) / (1 - pre + 1e-9))


# ----------------------------
# 2. Entropy Reduction
# ----------------------------
def entropy_reduction(pre, post):
    pre_vals = np.array(list(pre.values()))
    post_vals = np.array(list(post.values()))

    return entropy(pre_vals) - entropy(post_vals)


# ----------------------------
# 3. Cosine Similarity (Stability)
# ----------------------------
def mastery_similarity(pre, post):
    pre_vec = np.array(list(pre.values())).reshape(1, -1)
    post_vec = np.array(list(post.values())).reshape(1, -1)

    return cosine_similarity(pre_vec, post_vec)[0][0]


# ----------------------------
# 4. Variance (Stability)
# ----------------------------
def mastery_variance(history):
    # history = list of mastery dicts
    matrix = np.array([list(h.values()) for h in history])
    return np.mean(np.var(matrix, axis=0))


# ----------------------------
# 5. MRR (Recommendation Quality)
# ----------------------------
def mean_reciprocal_rank(recommendations, actual):
    ranks = []
    for rec, act in zip(recommendations, actual):
        if act in rec:
            rank = rec.index(act) + 1
            ranks.append(1 / rank)
        else:
            ranks.append(0)
    return np.mean(ranks)


# ----------------------------
# 6. Graph Coverage
# ----------------------------
def graph_coverage(visited_nodes, total_nodes):
    return len(set(visited_nodes)) / len(set(total_nodes))


# ----------------------------
# 7. Convergence Rate
# ----------------------------
def convergence_rate(history):
    diffs = []
    for i in range(1, len(history)):
        prev = np.array(list(history[i-1].values()))
        curr = np.array(list(history[i].values()))
        diffs.append(np.linalg.norm(curr - prev))
    return np.mean(diffs)


# ----------------------------
# 8. Clustering Quality (Optional)
# ----------------------------
def evaluate_clustering(embeddings, labels):
    return silhouette_score(embeddings, labels)
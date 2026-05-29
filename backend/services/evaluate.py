import json
import numpy as np
from scipy.stats import entropy
from collections import defaultdict
import time

LOG_FILE = "logs.jsonl"


# ----------------------------
# Load Logs
# ----------------------------
def load_logs(file_path):
    logs = []
    with open(file_path, "r") as f:
        for line in f:
            logs.append(json.loads(line))
    return logs


# ----------------------------
# Metric 1: Normalized Learning Gain
# ----------------------------
def normalized_learning_gain(pre, post):
    pre = np.array(list(pre.values()))
    post = np.array(list(post.values()))
    return np.mean((post - pre) / (1 - pre + 1e-9))


# ----------------------------
# Metric 2: Entropy Reduction
# ----------------------------
def entropy_reduction(pre, post):
    pre_vals = np.array(list(pre.values()))
    post_vals = np.array(list(post.values()))
    return entropy(pre_vals + 1e-9) - entropy(post_vals + 1e-9)


# ----------------------------
# Metric 3: MRR
# ----------------------------
def mean_reciprocal_rank(recommendations, actuals):
    scores = []
    for rec, act in zip(recommendations, actuals):
        if act in rec:
            rank = rec.index(act) + 1
            scores.append(1 / rank)
        else:
            scores.append(0)
    return np.mean(scores)


# ----------------------------
# Metric 4: Hit@K
# ----------------------------
def hit_at_k(recommendations, actuals, k=3):
    hits = 0
    for rec, act in zip(recommendations, actuals):
        if act in rec[:k]:
            hits += 1
    return hits / len(actuals)


# ----------------------------
# Metric 5: Convergence Rate
# ----------------------------
def convergence_rate(history):
    diffs = []
    for i in range(1, len(history)):
        prev = np.array(list(history[i - 1].values()))
        curr = np.array(list(history[i].values()))
        diffs.append(np.linalg.norm(curr - prev))
    return np.mean(diffs)


# ----------------------------
# Metric 6: Mastery Variance
# ----------------------------
def mastery_variance(history):
    matrix = np.array([list(h.values()) for h in history])
    return np.mean(np.var(matrix, axis=0))


# ----------------------------
# Metric 7: Graph Coverage
# ----------------------------
def graph_coverage(visited_nodes):
    return len(set(visited_nodes))


# ----------------------------
# Metric 8: Path Optimality (basic)
# ----------------------------
def path_efficiency(paths, shortest_paths):
    scores = []
    for actual, optimal in zip(paths, shortest_paths):
        if optimal == 0:
            continue
        scores.append(optimal / (len(actual) + 1e-9))
    return np.mean(scores) if scores else 0


# ----------------------------
# Metric 9: Cosine Similarity
# ----------------------------
def cosine_similarity(a, b):
    a = np.array(list(a.values()))
    b = np.array(list(b.values()))
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)


# ----------------------------
# Metric 10: Latency (if timestamps exist)
# ----------------------------
def avg_latency(logs):
    latencies = []
    for log in logs:
        if "start_time" in log and "end_time" in log:
            latencies.append(log["end_time"] - log["start_time"])
    return np.mean(latencies) if latencies else None


# ----------------------------
# MAIN EVALUATION
# ----------------------------
def evaluate():
    logs = load_logs(LOG_FILE)

    gains = []
    entropy_changes = []
    similarities = []

    recommendations = []
    actuals = []
    visited_nodes = []

    mastery_history = []

    for log in logs:
        pre = log["pre_mastery"]
        post = log["post_mastery"]

        gains.append(normalized_learning_gain(pre, post))
        entropy_changes.append(entropy_reduction(pre, post))
        similarities.append(cosine_similarity(pre, post))

        recommendations.append(log.get("recommended_topics", []))
        actuals.append(log.get("actual_next_topic"))

        visited_nodes.append(log.get("actual_next_topic"))

        mastery_history.append(post)

    # ----------------------------
    # Compute metrics
    # ----------------------------
    results = {
        "Learning Gain (NLG)": np.mean(gains),
        "Entropy Reduction": np.mean(entropy_changes),
        "MRR": mean_reciprocal_rank(recommendations, actuals),
        "Hit@3": hit_at_k(recommendations, actuals, k=3),
        "Convergence Rate": convergence_rate(mastery_history),
        "Mastery Variance": mastery_variance(mastery_history),
        "Graph Coverage": graph_coverage(visited_nodes),
        "State Similarity": np.mean(similarities),
        "Latency": avg_latency(logs),
    }

    return results


# ----------------------------
# Pretty Print
# ----------------------------
def print_results(results):
    print("\n" + "=" * 50)
    print("📊 MODEL EVALUATION REPORT")
    print("=" * 50)

    for key, value in results.items():
        print(f"{key:25s}: {value:.4f}" if value is not None else f"{key:25s}: N/A")

    print("=" * 50 + "\n")


# ----------------------------
# Run
# ----------------------------
# if __name__ == "__main__":
start = time.time()
results = evaluate()
print_results(results)
print(f"⏱ Evaluation Time: {time.time() - start:.2f}s")
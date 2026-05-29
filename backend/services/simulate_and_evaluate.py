import json
import random
import numpy as np
from scipy.stats import entropy

# ---------------------------
# SIMULATE DATA
# ---------------------------
def generate_mastery(num_concepts=5):
    return {f"c{i}": random.uniform(0.1, 0.5) for i in range(num_concepts)}

def update_mastery(pre):
    post = {}
    for k, v in pre.items():
        improvement = random.uniform(0.05, 0.2)
        post[k] = min(1.0, v + improvement)
    return post

def simulate_logs(n=100):
    logs = []

    for _ in range(n):
        pre = generate_mastery()
        post = update_mastery(pre)

        concepts = list(pre.keys())
        random.shuffle(concepts)

        logs.append({
            "pre_mastery": pre,
            "post_mastery": post,
            "recommended_topics": concepts[:3],
            "actual_next_topic": random.choice(concepts)
        })

    return logs


# ----------------------------
# METRICS
# ----------------------------
def normalized_learning_gain(pre, post):
    pre = np.array(list(pre.values()))
    post = np.array(list(post.values()))
    return np.mean((post - pre) / (1 - pre + 1e-9))


def entropy_reduction(pre, post):
    return entropy(list(pre.values())) - entropy(list(post.values()))


def mrr(recs, actuals):
    scores = []
    for r, a in zip(recs, actuals):
        if a in r:
            scores.append(1 / (r.index(a) + 1))
        else:
            scores.append(0)
    return np.mean(scores)


def hit_at_k(recs, actuals, k=3):
    hits = 0
    for r, a in zip(recs, actuals):
        if a in r[:k]:
            hits += 1
    return hits / len(actuals)


def convergence(history):
    diffs = []
    for i in range(1, len(history)):
        prev = np.array(list(history[i-1].values()))
        curr = np.array(list(history[i].values()))
        diffs.append(np.linalg.norm(curr - prev))
    return np.mean(diffs)


# ----------------------------
# RUN EVERYTHING
# ----------------------------
def main():
    logs = simulate_logs(200)

    gains = []
    entropies = []
    recs = []
    actuals = []
    history = []

    for log in logs:
        gains.append(normalized_learning_gain(log["pre_mastery"], log["post_mastery"]))
        entropies.append(entropy_reduction(log["pre_mastery"], log["post_mastery"]))
        recs.append(log["recommended_topics"])
        actuals.append(log["actual_next_topic"])
        history.append(log["post_mastery"])

    print("\n===== EVALUATION REPORT =====")
    print("Learning Gain:", np.mean(gains))
    print("Entropy Reduction:", np.mean(entropies))
    print("MRR:", mrr(recs, actuals))
    print("Hit@3:", hit_at_k(recs, actuals))
    print("Convergence:", convergence(history))
    print("=============================\n")


# if __name__ == "__main__":
main()
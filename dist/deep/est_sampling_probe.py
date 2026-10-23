"""Tutorial only: EST index sampling and WAR/UAR, no dataset or torch needed."""
import argparse
import json
import random


def sample(seed=8, start=15):
    rng = random.Random(seed)
    train = [sorted(rng.sample(range(start + 10 * i, start + 10 * i + 15), 5)) for i in range(7)]
    test = [[start + 10 * i + j for j in (0, 3, 6, 9, 12)] for i in range(7)]
    for group in train + test:
        assert len(group) == 5 and group == sorted(group)
        assert min(group) >= 0 and max(group) < 105
    permutation = [2, 4, 0, 6, 1, 5, 3]
    shuffled = [train[i] for i in permutation]
    assert shuffled[0] == train[2]
    # The same original snippet keeps its original positional identity.
    positional_ids = [i for i in permutation]
    recalls = [8 / 10, 1 / 2]
    war = (8 + 1) / (10 + 2)
    uar = sum(recalls) / len(recalls)
    assert abs(war - 0.75) < 1e-12
    assert abs(uar - 0.65) < 1e-12
    return dict(seed=seed, start=start, train_indices=train, test_indices=test,
                permutation=permutation, shuffled_indices=shuffled,
                original_position_ids=positional_ids, frame_slots=35,
                unique_train_frames=len(set(sum(train, []))),
                tutorial_war=war, tutorial_uar=uar, assertions="passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=8)
    parser.add_argument("--start", type=int, default=15, choices=range(30))
    args = parser.parse_args()
    print(json.dumps(sample(args.seed, args.start), indent=2))

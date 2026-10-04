from hitl_energy_cps import (
    ObjectiveWeights,
    all_cases,
    score_action,
    should_request_human,
)


def main() -> None:
    weights = ObjectiveWeights(energy=0.45, safety=0.40, service=0.15)

    for domain, (state, actions) in all_cases().items():
        ranked = sorted(
            [score_action(state, action, weights=weights) for action in actions],
            key=lambda item: item.total_score,
            reverse=True,
        )
        review = should_request_human(state, ranked)

        print(f"\n{domain}")
        print(f"  proposed action: {ranked[0].action.name}")
        print(f"  score: {ranked[0].total_score:.3f}")
        print(f"  human review: {review.required}")
        print(f"  reasons: {', '.join(review.reasons) if review.reasons else 'none'}")


if __name__ == "__main__":
    main()

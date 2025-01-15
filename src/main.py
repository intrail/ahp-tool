import numpy as np
import pandas as pd

from hierarchy import parse_hierarchy, display_hierarchy
from ahp import perform_ahp, recursive_ahp, build_global_alternative_table
from alternatives import (
    input_alternatives,
    select_scale_param_method,
    get_local_alternative_weights
)


def main():
    print("""
    ┌─────────────────────────────────────────────────────────────────┐
    │                      _     _  _    ___  _  _                    │
    │                  ___| |__ | || |  / _ \| || |                   │
    │                 |_  / '_ \| || |_| | | | || |_                  │
    │                  / /| | | |__   _| |_| |__   _|                 │
    │                 /___|_| |_|  |_|  \___/   |_|                   │
    │                                                                 │
    │                          AHP Tool v1.0                          │
    │                                                                 │
    │ Developed as part of the module 'ESD200 Sustainability Methods  │
    │ and Metrics" at the Centre for Sustainable Development.         │
    │                                                                 │
    │ Special thanks to Dr André Cabrera Serrenho for his inspiring   │
    │ lectures and knowledge shared in the module.                    │
    │                                                                 │
    │ With sincere gratitude to Dr Dai Morgan for his invaluable      │
    │ guidance and academic support.                                  │
    │                                                                 │
    │ Any errors or inaccuracies are solely my responsibility.        │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘
    """)
    print("=" * 70)
    print("WELCOME to the AHP Tool! This programme will guide you step by step.")
    print("=" * 70)

    # Step 1: Hierarchy
    while True:
        print("\nPlease input your hierarchy structure using commas to separate criteria at the same level.")
        print("If a criterion has sub-criteria, enclose them in curly braces.")
        print("Example: 'A, B{a, b{i, ii}}, C'.")
        input_string = input("Enter hierarchy: ").strip()
        try:
            hierarchy = parse_hierarchy(input_string)
            break
        except ValueError as e:
            print(f"Error: {e}. Please try again.\n")

    # Confirm hierarchy
    while True:
        print("\nHere is the parsed hierarchy:")
        display_hierarchy(hierarchy)
        confirm = input("Does this hierarchy look correct? (yes/no): ").strip().lower()
        if confirm in ['y', 'yes']:
            break
        elif confirm in ['n', 'no']:
            print("Please re-enter the hierarchy.")
        else:
            print("Invalid input. Please type 'yes' or 'no'.")

    # Step 2: AHP for top-level
    top_criteria = list(hierarchy.keys())
    if len(top_criteria) == 1:
        top_weights = [1.0]
    else:
        print("\nPerforming AHP for top-level criteria...")
        top_weights = perform_ahp(top_criteria)

    parent_weights = {c: w for c, w in zip(top_criteria, top_weights)}

    # Recursively compute all leaf criteria
    print("\nComputing global weights for all leaf criteria...")
    global_results = recursive_ahp(hierarchy, parent_weights)

    leaf_criteria_paths = list(global_results.keys())
    leaf_criteria_weights = {k: global_results[k] for k in leaf_criteria_paths}

    sum_leaf = sum(leaf_criteria_weights.values())
    df_leaf = pd.DataFrame(
        sorted(leaf_criteria_weights.items(), key=lambda x: x[1], reverse=True),
        columns=["Leaf Criterion (Path)", "Global Weight"]
    )
    print("\nLeaf Criteria and Their Global Weights:")
    print(df_leaf.to_string(index=False))
    print(f"Sum of leaf criteria global weights = {sum_leaf:.4f}")
    if not np.isclose(sum_leaf, 1.0, atol=1e-5):
        print("WARNING: The leaf criteria weights do NOT sum up to 1. Please check the hierarchy or pairwise inputs.")

    # Step 3: Input alternatives
    alternatives = input_alternatives()

    # Step 4: Ask user for a global numeric scaling method among (1/2/3)
    print("\nNote: For each numerical leaf, you may override this method.")
    global_method_choice = select_scale_param_method()

    # Step 5: For each leaf, do local AHP
    alt_local_weights = {}
    for leaf_path in leaf_criteria_paths:
        alt_w = get_local_alternative_weights(alternatives, leaf_path, global_method_choice)
        alt_local_weights[leaf_path] = alt_w

    # Step 6: Build final table
    df_final = build_global_alternative_table(alternatives, leaf_criteria_paths, leaf_criteria_weights, alt_local_weights)
    print("\n================ FINAL GLOBAL ALTERNATIVE WEIGHTS TABLE ================\n")
    print(df_final.to_string(index=False))

    # Present the best alternative
    sorted_alts = df_final.iloc[:-1].sort_values(by="Total", ascending=False)
    best_alt = sorted_alts.iloc[0]
    if len(sorted_alts) > 1:
        second_best = sorted_alts.iloc[1]
        diff = (best_alt["Total"] - second_best["Total"]) / second_best["Total"] * 100
        print(f"\nThe best alternative is '{best_alt['Alternative']}' with a global weight of {best_alt['Total']:.4f}.")
        print(f"It is {diff:.2f}% better than the second best alternative '{second_best['Alternative']}'.")
    else:
        print(f"\nThe best (and only) alternative is '{best_alt['Alternative']}' with a global weight of {best_alt['Total']:.4f}.")

    # Final consistency check
    last_row = df_final.iloc[-1]
    last_col_sum = last_row.iloc[-1]
    total_leaf_sum = df_final.iloc[-1, 1:-1].sum()
    if not np.isclose(last_col_sum, 1.0, atol=1e-5) or not np.isclose(total_leaf_sum, 1.0, atol=1e-5):
        print("\nWARNING: The sums do not equal 1, so something must be incorrect!")
        print("Please check the input pairwise comparisons or the hierarchy structure.")
    else:
        print("\n" + "=" * 70)
        print("All done! Thank you for using the AHP Tool. Goodbye.")
        print("=" * 70)


if __name__ == "__main__":
    main()

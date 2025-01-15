import numpy as np
import pandas as pd

# ----------------------------------------------------
#               HELPER FUNCTIONS
# ----------------------------------------------------

def calculate_eigen_weights(matrix):
    """
    Calculate principal eigenvector and normalised weights from a pairwise comparison matrix.
    """
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    max_index = np.argmax(eigenvalues)
    principal_eigenvector = eigenvectors[:, max_index].real
    normalised_weights = principal_eigenvector / np.sum(principal_eigenvector)
    return principal_eigenvector, normalised_weights


def calculate_consistency_ratio(matrix, weights):
    """
    Calculate the consistency ratio (CR) of a pairwise comparison matrix.
    If n = 2, CR is not defined and will return None.
    For n > 30, use random_index = 1.6687 * (1 - exp(-0.2069 * n)).
    """
    n = len(matrix)
    random_index_dict = {
        1: 0.0000, 2: 0.0000, 3: 0.5799, 4: 0.8921, 5: 1.1159,
        6: 1.2358, 7: 1.3322, 8: 1.3952, 9: 1.4537, 10: 1.4882,
        11: 1.5117, 12: 1.5356, 13: 1.5571, 14: 1.5714, 15: 1.5861,
        16: 1.5943, 17: 1.6064, 18: 1.6133, 19: 1.6207, 20: 1.6292,
        21: 1.6358, 22: 1.6403, 23: 1.6462, 24: 1.6497, 25: 1.6556,
        26: 1.6587, 27: 1.6631, 28: 1.6670, 29: 1.6693, 30: 1.6724
    }

    if n == 2:
        lam_max = np.mean(np.dot(matrix, weights) / weights)
        return lam_max, 0, None  # CR not defined for n=2

    lam_max = np.mean(np.dot(matrix, weights) / weights)
    ci = (lam_max - n) / (n - 1)

    if n <= 30:
        ri = random_index_dict.get(n, 1.6724)
    else:
        ri = 1.6687 * (1 - np.exp(-0.2069 * n))

    cr = ci / ri if ri != 0 else None
    return lam_max, ci, cr


def format_pairwise_matrix(matrix):
    """
    Convert numerical matrix to strings like '1', '5', '1/3', for better display.
    """
    df_str = []
    for row in matrix:
        row_str = []
        for val in row:
            if abs(val - 1.0) < 1e-9:
                row_str.append("1")
            elif val > 1:
                ival = int(round(val))
                row_str.append(f"{ival}")
            else:
                inv = int(round(1.0 / val))
                row_str.append(f"1/{inv}")
        df_str.append(row_str)
    return df_str


# ----------------------------------------------------
#          CRITERIA PAIRWISE COMPARISON
# ----------------------------------------------------

def input_comparison(criteria):
    n = len(criteria)
    matrix = np.ones((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            print(f"\nCompare: {criteria[i]} vs. {criteria[j]}")
            print("Options:")
            print(f"1. {criteria[i]} is more important")
            print(f"2. {criteria[j]} is more important")
            print("3. Both are equally important")
            choice = input("Select an option (1/2/3): ").strip()

            if choice == "3":
                matrix[i, j] = 1
                matrix[j, i] = 1
            elif choice == "1":
                while True:
                    importance = input(
                        f"On a scale of 1-8, how much more important is '{criteria[i]}' than '{criteria[j]}'?\n"
                        f"(1 = slightly more important, 8 = extremely more important): "
                    ).strip()
                    try:
                        value = int(importance) + 1
                        if 1 <= value <= 9:
                            matrix[i, j] = value
                            matrix[j, i] = 1 / value
                            break
                        else:
                            print("Invalid input. Please enter a number between 1 and 8.")
                    except ValueError:
                        print("Invalid input. Please enter a valid integer.")
            elif choice == "2":
                while True:
                    importance = input(
                        f"On a scale of 1-8, how much more important is '{criteria[j]}' than '{criteria[i]}'?\n"
                        f"(1 = slightly more important, 8 = extremely more important): "
                    ).strip()
                    try:
                        value = int(importance) + 1
                        if 1 <= value <= 9:
                            matrix[j, i] = value
                            matrix[i, j] = 1 / value
                            break
                        else:
                            print("Invalid input. Please enter a number between 1 and 8.")
                    except ValueError:
                        print("Invalid input. Please enter a valid integer.")
            else:
                print("Invalid choice. Please select 1, 2, or 3.")
                j -= 1
                break
    return matrix


def perform_ahp(criteria):
    while True:
        pairwise_matrix = input_comparison(criteria)
        principal_eigenvector, weights = calculate_eigen_weights(pairwise_matrix)
        lam_max, ci, cr = calculate_consistency_ratio(pairwise_matrix, weights)

        from ahp import format_pairwise_matrix
        df_matrix_str = format_pairwise_matrix(pairwise_matrix)
        df_matrix = pd.DataFrame(df_matrix_str, index=criteria, columns=criteria)
        print("\n" + "=" * 60)
        print("Pairwise Comparison Matrix (Criteria)")
        print("=" * 60)
        print(df_matrix.to_string(index=True))

        df_weights = pd.DataFrame({
            "Criteria": criteria,
            "Principal Eigenvector": principal_eigenvector,
            "Normalised Weights": weights
        })
        print("\n" + "=" * 60)
        print("Principal Eigenvector & Normalised Weights")
        print("=" * 60)
        print(df_weights.to_string(index=False))

        print(f"\nPrincipal Eigenvalue (λ_max): {lam_max:.4f}")
        if len(criteria) > 2:
            print(f"Consistency Index (CI): {ci:.4f}")
            print(f"Consistency Ratio (CR): {cr:.4f}")
            if cr and cr >= 0.1:
                print("WARNING: Consistency check failed! CR >= 0.1.")
        else:
            print("CR not defined for n = 2 (skipping consistency check).")

        ans = input("\nWould you like to re-enter the pairwise comparisons for these criteria? (yes/no): ").strip().lower()
        if ans in ['y', 'yes']:
            continue
        else:
            return weights


def recursive_ahp(hierarchy, parent_weights, parent_path=""):
    results = {}
    for criterion, sub_criteria in hierarchy.items():
        current_path = criterion if not parent_path else f"{parent_path} - {criterion}"

        if sub_criteria:  # has children
            print(f"\nPerforming AHP for sub-criteria of '{criterion}'...")
            children = list(sub_criteria.keys())
            local_weights = perform_ahp(children)

            parent_weight = parent_weights.get(current_path.split(" - ")[-1], 1.0)
            child_global_weights = {
                child: parent_weight * local_weights[i]
                for i, child in enumerate(children)
            }
            for child in children:
                sub_results = recursive_ahp(
                    {child: sub_criteria[child]},
                    {child: child_global_weights[child]},
                    current_path
                )
                results.update(sub_results)
        else:
            leaf_name = current_path
            if parent_path == "":
                parent_weight = parent_weights.get(criterion, 1.0)
            else:
                parent_weight = list(parent_weights.values())[0]

            results[leaf_name] = parent_weight
    return results


# ----------------------------------------------------
#        STEP 3: BUILD THE GLOBAL ALTERNATIVE RANK
# ----------------------------------------------------

def build_global_alternative_table(alternatives, leaf_criteria_paths, leaf_criteria_weights, alt_local_weights):
    data = []
    for alt in alternatives:
        row_values = []
        for crit_path in leaf_criteria_paths:
            lw = alt_local_weights[crit_path].get(alt, 0.0)
            gw_leaf = leaf_criteria_weights[crit_path]
            row_values.append(lw * gw_leaf)
        total_alt = sum(row_values)
        row_data = [alt] + row_values + [total_alt]
        data.append(row_data)

    total_row = ["Total"]
    col_sums = []
    for crit_path in leaf_criteria_paths:
        s = sum(alt_local_weights[crit_path][alt] * leaf_criteria_weights[crit_path] for alt in alternatives)
        col_sums.append(s)
    total_sum = sum(col_sums)
    total_row.extend(col_sums)
    total_row.append(total_sum)
    data.append(total_row)

    columns = ["Alternative"] + leaf_criteria_paths + ["Total"]
    df = pd.DataFrame(data, columns=columns)

    df_no_total = df.iloc[:-1, :]
    df_total = df.iloc[-1:, :]
    df_no_total_sorted = df_no_total.sort_values("Total", ascending=False)
    df_final = pd.concat([df_no_total_sorted, df_total], ignore_index=True)
    return df_final

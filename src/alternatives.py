import numpy as np
import pandas as pd

from ahp import (
    calculate_eigen_weights,
    calculate_consistency_ratio,
    format_pairwise_matrix
)

# ----------------------------------------------------
#         STEP 2: ALTERNATIVES & LOCAL WEIGHTS
# ----------------------------------------------------

def input_alternatives():
    while True:
        alts_str = input("\nEnter all alternatives (comma-separated): ").strip()
        if not alts_str:
            print("Invalid input. Please enter at least one alternative.")
            continue
        alternatives = [x.strip() for x in alts_str.split(",") if x.strip()]
        if alternatives:
            return alternatives
        else:
            print("Invalid input. Please try again.")


def select_scale_param_method():
    """
    Three options:
      1) use max_ratio
      2) use k * max_ratio
      3) user custom scale parameter
    """
    print("\nSelect how to compute the scaling parameter for numerical criteria:")
    print("1. Use the maximum ratio of all values (max_ratio).")
    print("2. Use a factor k times max_ratio.")
    print("3. Enter a custom scale parameter manually.")

    while True:
        choice = input("Enter '1', '2', or '3': ").strip()
        if choice in ['1', '2', '3']:
            return choice
        else:
            print("Invalid choice. Please select 1, 2, or 3.")


def calculate_max_ratio(values):
    # Ensure the largest better_by_ratio maps to 9
    max_better_by_ratio = max(
        max(values) / min(values[i], values[j])
        for i in range(len(values))
        for j in range(i + 1, len(values))
    )
    return max_better_by_ratio  # Directly use the max better_by_ratio as max_ratio


def compute_scale_param(values, method_choice):
    """
    Given numeric values and the method_choice (1/2/3), compute the scale_param.
      1 -> scale_param = max_ratio
      2 -> scale_param = k * max_ratio
      3 -> user custom
    Also clamp scale_param to [0.5, 100].
    """
    max_r = calculate_max_ratio(values)

    if method_choice == '1':
        scale_param = max_r
    elif method_choice == '2':
        while True:
            k_str = input("\nEnter your factor k (> 0) for scaling the max_ratio: ").strip()
            try:
                k_val = float(k_str)
                if k_val > 0:
                    scale_param = k_val * max_r
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Invalid input. Please enter a valid float.")
    else:  # '3'
        while True:
            custom_str = input("Enter your custom scale parameter (positive float): ").strip()
            try:
                custom_val = float(custom_str)
                if custom_val > 0:
                    scale_param = custom_val
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Invalid input. Please try again.")

    # clamp
    if scale_param < 0.5:
        scale_param = 0.5
    elif scale_param > 100:
        scale_param = 100

    return scale_param


def input_numerical_values(alternatives):
    """
    Ask user to input numeric values for each alternative,
    then confirm correctness.
    """
    while True:
        values = []
        for alt in alternatives:
            while True:
                val_str = input(f"Value for '{alt}': ").strip()
                try:
                    val = float(val_str)
                    values.append(val)
                    break
                except ValueError:
                    print("Invalid number. Please try again.")

        df_temp = pd.DataFrame({"Alternative": alternatives, "Value": values})
        print("\nHere are your inputs for this criterion:")
        print(df_temp.to_string(index=False, justify="center"))
        confirm_data = input("Are these values correct? (yes/no): ").strip().lower()
        if confirm_data in ['y', 'yes']:
            return values
        else:
            print("Let's re-enter the values...\n")


def build_numerical_matrix(alternatives, values, direction, scale_param):
    """
    Build pairwise matrix automatically from numeric values & scale_param.
    Print out each pair's ratio & intensity.
    """
    n = len(alternatives)
    matrix = np.ones((n, n))

    for i in range(n):
        for j in range(i+1, n):
            if abs(values[i] - values[j]) < 1e-9:
                better_by_ratio = 1
                intensity = 1
                better = "Neither"
                matrix[i, j] = 1
                matrix[j, i] = 1
            else:
                if values[i] == 0 or values[j] == 0:
                    better_by_ratio = 9
                else:
                    better_by_ratio = max(values[i], values[j]) / min(values[i], values[j])

                raw_intensity = 9 * (better_by_ratio / scale_param)
                if raw_intensity < 1:
                    intensity = 1
                elif raw_intensity > 9:
                    intensity = 9
                else:
                    intensity = int(round(raw_intensity))

                if direction == "larger":
                    if values[i] >= values[j]:
                        better = alternatives[i]
                        matrix[i, j] = intensity
                        matrix[j, i] = 1 / intensity
                    else:
                        better = alternatives[j]
                        matrix[j, i] = intensity
                        matrix[i, j] = 1 / intensity
                else:  # 'smaller'
                    if values[i] <= values[j]:
                        better = alternatives[i]
                        matrix[i, j] = intensity
                        matrix[j, i] = 1 / intensity
                    else:
                        better = alternatives[j]
                        matrix[j, i] = intensity
                        matrix[i, j] = 1 / intensity

            print(f"{alternatives[i]} vs. {alternatives[j]} => {better} is better. Ratio = {better_by_ratio:.2f}, Intensity = {intensity}")

    return matrix


def input_categorical_comparisons(alternatives):
    n = len(alternatives)
    matrix = np.ones((n, n))
    for i in range(n):
        for j in range(i+1, n):
            print(f"\nCompare: {alternatives[i]} vs. {alternatives[j]}")
            print("Options:")
            print(f"1. {alternatives[i]} is better")
            print(f"2. {alternatives[j]} is better")
            print("3. Both are equally good")
            choice = input("Select an option (1/2/3): ").strip()
            if choice == "3":
                matrix[i, j] = 1
                matrix[j, i] = 1
            elif choice == "1":
                while True:
                    val_str = input(
                        f"On a scale of 1-8, how much better is '{alternatives[i]}' than '{alternatives[j]}'?\n"
                        f"(1 = slightly better, 8 = extremely better): "
                    ).strip()
                    try:
                        val = int(val_str) + 1
                        if 1 <= val <= 9:
                            matrix[i, j] = val
                            matrix[j, i] = 1 / val
                            break
                        else:
                            print("Please enter an integer between 1 and 8.")
                    except ValueError:
                        print("Invalid integer. Please try again.")
            elif choice == "2":
                while True:
                    val_str = input(
                        f"On a scale of 1-8, how much better is '{alternatives[j]}' than '{alternatives[i]}'?\n"
                        f"(1 = slightly better, 8 = extremely better): "
                    ).strip()
                    try:
                        val = int(val_str) + 1
                        if 1 <= val <= 9:
                            matrix[j, i] = val
                            matrix[i, j] = 1 / val
                            break
                        else:
                            print("Please enter an integer between 1 and 8.")
                    except ValueError:
                        print("Invalid integer. Please try again.")
            else:
                print("Invalid choice. Please select 1, 2, or 3.")
                j -= 1
                break
    return matrix


def get_local_alternative_weights(alternatives, leaf_criterion_name, global_method_choice):
    """
    After user chooses numerical vs. categorical, do pairwise comparisons.
    If numerical:
      - input numeric values once
      - ask 'larger or smaller?'
      - choose scale param method => build matrix => compute CR => show results
      - user can (1) re-enter data, (2) re-set scale param, (3) continue
    """
    while True:
        print(f"\nFor leaf criterion '{leaf_criterion_name}', is it numerical/ordinal or categorical/nominal?")
        print("Options:")
        print("1. Numerical / Ordinal")
        print("2. Categorical / Nominal")
        ans = input("Choose (1/2): ").strip()
        if ans not in ["1", "2"]:
            print("Invalid choice. Please try again.")
            continue

        if ans == "2":
            # Categorical path
            while True:
                matrix = input_categorical_comparisons(alternatives)
                eigvec, local_weights = calculate_eigen_weights(matrix)
                lam_max, ci, cr = calculate_consistency_ratio(matrix, local_weights)

                df_matrix_str = format_pairwise_matrix(matrix)
                df_matrix = pd.DataFrame(df_matrix_str, index=alternatives, columns=alternatives)
                print("\n" + "=" * 60)
                print(f"Pairwise Comparison Matrix for '{leaf_criterion_name}' (Categorical)")
                print("=" * 60)
                print(df_matrix.to_string(index=True))

                df_local = pd.DataFrame({
                    "Alternative": alternatives,
                    "Principal Eigenvector": eigvec,
                    "Normalised Weights": local_weights
                })
                print("\n" + "=" * 60)
                print(f"Local Weights for '{leaf_criterion_name}'")
                print("=" * 60)
                print(df_local.to_string(index=False))

                print(f"\nPrincipal Eigenvalue (λ_max): {lam_max:.4f}")
                if len(alternatives) > 2 and cr is not None:
                    print(f"Consistency Index (CI): {ci:.4f}")
                    print(f"Consistency Ratio (CR): {cr:.4f}")
                    if cr >= 0.1:
                        print(f"WARNING: CR >= 0.1 for '{leaf_criterion_name}'.")

                next_action = input("\nOptions:\n1. Re-compare\n2. Continue\nSelect an option (1/2): ").strip()
                if next_action == "1":
                    continue
                else:
                    alt_dict = {alt: w for alt, w in zip(alternatives, local_weights)}
                    return alt_dict

        else:
            # Numerical path
            # Step 1: input numeric values & confirm
            values = input_numerical_values(alternatives)

            # Step 2: choose direction
            while True:
                print("\nFor this criterion, is a larger value better or a smaller value better?")
                print("1. A larger value is better")
                print("2. A smaller value is better")
                direction_choice = input("Choose (1/2): ").strip()
                if direction_choice == "1":
                    direction = "larger"
                    break
                elif direction_choice == "2":
                    direction = "smaller"
                    break
                else:
                    print("Invalid choice. Please try again.")

            # We'll store local_method_choice = global_method_choice initially
            local_method_choice = global_method_choice

            # A loop for constructing the matrix, computing weights, and letting user re-set scale param
            while True:
                # Compute scale param based on local_method_choice
                scale_param = compute_scale_param(values, local_method_choice)
                print(f"\nComputed Scale Parameter = {scale_param:.4f} (method='{local_method_choice}')")

                matrix = build_numerical_matrix(alternatives, values, direction, scale_param)
                eigvec, local_weights = calculate_eigen_weights(matrix)
                lam_max, ci, cr = calculate_consistency_ratio(matrix, local_weights)

                df_matrix_str = format_pairwise_matrix(matrix)
                df_matrix = pd.DataFrame(df_matrix_str, index=alternatives, columns=alternatives)
                print("\n" + "=" * 60)
                print(f"Pairwise Comparison Matrix for '{leaf_criterion_name}' (Numerical)")
                print("=" * 60)
                print(df_matrix.to_string(index=True))

                df_local = pd.DataFrame({
                    "Alternative": alternatives,
                    "Principal Eigenvector": eigvec,
                    "Normalised Weights": local_weights
                })
                print("\n" + "=" * 60)
                print(f"Local Weights for '{leaf_criterion_name}'")
                print("=" * 60)
                print(df_local.to_string(index=False))

                print(f"\nPrincipal Eigenvalue (λ_max): {lam_max:.4f}")
                if len(alternatives) > 2 and cr is not None:
                    print(f"Consistency Index (CI): {ci:.4f}")
                    print(f"Consistency Ratio (CR): {cr:.4f}")
                    if cr >= 0.1:
                        print(f"WARNING: CR >= 0.1 for '{leaf_criterion_name}'.")
                else:
                    print("CR not defined for n=2 (skipping).")

                print("\nOptions:")
                print("1. Re-enter values")
                print("2. Re-set scale parameter (this leaf only)")
                print("3. Continue")
                choice_num = input("Select an option (1/2/3): ").strip()
                if choice_num == "1":
                    # re-enter data entirely (and direction)
                    values = input_numerical_values(alternatives)
                    while True:
                        print("Is a larger value better or a smaller value better?")
                        print("1. A larger value is better")
                        print("2. A smaller value is better")
                        dch = input("Choose (1/2): ").strip()
                        if dch == "1":
                            direction = "larger"
                            break
                        elif dch == "2":
                            direction = "smaller"
                            break
                        else:
                            print("Invalid choice. Please try again.")
                    local_method_choice = global_method_choice
                    continue
                elif choice_num == "2":
                    # re-set scale param => let user pick method again
                    print("\nRe-set scale parameter for this leaf only:")
                    local_method_choice = select_scale_param_method()
                    continue
                else:
                    alt_dict = {alt: w for alt, w in zip(alternatives, local_weights)}
                    return alt_dict

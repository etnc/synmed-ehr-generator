# import statistics
# from locale import normalize
#
# import pandas as pd
# from matplotlib import pyplot as plt
#
# from sklearn.preprocessing import MinMaxScaler, StandardScaler
#
# from data.icd_diagnoses_antecedents import icd_diagnoses_antecedents
# from service.medical_service import get_antecedent_diagnose
#
# # alphas = [0.4, 0.3]  # Weight for support
# # betas = [0.6, 0.7]  # Weight for lift
# alpha = 0.4
# beta = 0.6
# threshold = 0.2
#
# all_lifts = []
# all_scores = []
# scaler = StandardScaler()
# for diagnoses in icd_diagnoses_antecedents.values():
#     for rule in diagnoses:
#         all_lifts.append(rule['lift'])
#
# all_lifts = [[lift] for lift in all_lifts]
# standardized_lifts = scaler.fit_transform(all_lifts)
# valid_rules = []
# # std_lift = statistics.stdev(all_lifts)
# # mean = statistics.mean(all_lifts)
# # max_lift = max(all_lifts)
# # min_lift = min(all_lifts)
# for rules in icd_diagnoses_antecedents.values():
#     results = []
#     for rule, std_lift in zip(rules, standardized_lifts):
#         score = alpha * rule['support'] + beta * std_lift[0]
#         all_scores.append(score)
#         if score > threshold:
#             valid_rules.append(rule)
#
# # results.append({
# #     "support": rule['support'],
# #     "lift": rule['lift'],
# #     "alpha": alpha,
# #     "beta": beta,
# #     "score": score,
# #     "rule": rule['antecedents'],
# #     "selected": score > threshold
# # })
#
# scores_df = pd.DataFrame(all_scores, columns=['Score'])
# # print(f"Number of selected rules: {len(valid_rules)}")
# print(f"Number of  rules: {sum(len(rule) for rule in icd_diagnoses_antecedents.values())}")
#
# plt.figure(figsize=(10, 6))
# plt.hist(all_scores, bins=20, edgecolor='black', alpha=0.7)
# plt.title('Distribution of Rule Scores')
# plt.xlabel('Score')
# plt.ylabel('Frequency')
# plt.show()
#
# pd.set_option('display.max_rows', None)
#
from data.icd_diagnoses_antecedents import icd_diagnoses_antecedents
from service.medical_service import get_antecedent_diagnose

rule = get_antecedent_diagnose(icd_diagnoses_antecedents['Q61'])
print(rule)
# score = alpha * rule['support'] + beta * rule['lift']
# print(score)

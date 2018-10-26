from sklearn.metrics import cohen_kappa_score
import matplotlib.pyplot as plt

q1_j1 = [1,0,0,1,1,0,1,0,0,0]
q1_j2 = [1,0,0,1,0,0,0,0,0,0]

q2_j1 = [1,1,1,1,0,0,1,1,0,1]
q2_j2 = [1,1,1,1,0,0,1,1,0,1]

q3_j1 = [1,1,1,1,1,1,0,1,1,1]
q3_j2 = [1,1,1,1,1,0,0,1,1,0]

q4_j1 = [1,1,1,1,1,1,1,1,1,1]
q4_j2 = [1,1,1,1,1,1,1,1,1,1]

q5_j1 = [0,1,0,0,0,0,0,0,0,0]
q5_j2 = [0,1,0,0,0,1,0,0,0,0]

j1_total = q1_j1 + q2_j1 + q3_j1 + q4_j1 + q5_j1
j2_total = q1_j2 + q2_j2 + q3_j2 + q4_j2 + q5_j2
j1_average = [sum(q1_j1)/10, sum(q2_j1)/10, sum(q3_j1)/10, sum(q4_j1)/10, sum(q5_j1)/10]
j2_average = [sum(q1_j2)/10, sum(q2_j2)/10, sum(q3_j2)/10, sum(q4_j2)/10, sum(q5_j2)/10]

print("Cohens kappa", cohen_kappa_score(j1_total, j2_total))
print("Average precision", sum(j1_total+j2_total)/len(j1_total+j2_total))
plt.plot(["q1", "q2", "q3", "q4", "q5"], j1_average, label='Judge 1')
plt.plot(["q1", "q2", "q3", "q4", "q5"], j2_average, label='Judge 2')
plt.title("Precision for Queries")
plt.xlabel("Query Number")
plt.ylabel("P@10")
plt.legend()
plt.show()

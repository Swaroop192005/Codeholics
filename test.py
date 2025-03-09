# import requests

# url = "http://127.0.0.1:5000/recommend?course_title=java"
# response = requests.get(url)

# print("Response Status Code:", response.status_code)
# print("Response JSON:", response.json())


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Load dataset
df = pd.read_csv("data/cleaned_udemy_course_dataset.csv")

# Drop non-numeric columns that are not useful for clustering
df = df.drop(columns=['course_id', 'course_title', 'url', 'published_timestamp'])

# Convert categorical features to numerical
df['is_paid'] = df['is_paid'].map({True: 1, False: 0})  # Convert boolean to 1/0
df['level'] = LabelEncoder().fit_transform(df['level'])  # Encode course level

# Fill missing values (if any)
df = df.dropna()

# Scale numerical data for better clustering
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df.drop(columns=['subject']))  # Drop 'subject' before scaling

# Find optimal k using Elbow Method
inertia = []
k_range = range(1, 11)  # Testing k from 1 to 10
for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(df_scaled)
    inertia.append(kmeans.inertia_)

# Plot the Elbow Method graph
plt.figure(figsize=(8, 5))
plt.plot(k_range, inertia, marker='o', linestyle='-')
plt.xlabel("Number of Clusters (k)")
plt.ylabel("Inertia (WCSS)")
plt.title("Elbow Method for Optimal k")
plt.show()

# Apply K-Means with chosen k (Assuming k=4 based on the Elbow Method)
optimal_k = 4
kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(df_scaled)

# Print first few rows with clusters
print(df.head())

# Visualizing Clusters (using price and number of subscribers)
plt.figure(figsize=(10, 6))
sns.scatterplot(x=df['price'], y=df['num_subscribers'], hue=df['Cluster'], palette='viridis', alpha=0.7)
plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=300, c='red', marker='X', label="Centroids")
plt.xlabel('Price')
plt.ylabel('Number of Subscribers')
plt.title('Course Clustering')
plt.legend()
plt.show()

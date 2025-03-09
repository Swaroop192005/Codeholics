import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

def prepare_data_for_clustering(df):
    """
    Prepare the dataset for clustering by cleaning and transforming features
    """
    # Create a copy to avoid modifying the original
    df_cluster = df.copy()
    
    # Drop non-numeric columns that are not useful for clustering
    df_cluster = df_cluster.drop(columns=['course_id', 'course_title', 'url', 'published_timestamp'], errors='ignore')
    
    # Convert categorical features to numerical
    df_cluster['is_paid'] = df_cluster['is_paid'].map({True: 1, False: 0})  # Convert boolean to 1/0
    
    # Handle level if it exists
    if 'level' in df_cluster.columns:
        df_cluster['level'] = LabelEncoder().fit_transform(df_cluster['level'])  # Encode course level
    
    # Fill missing values (if any)
    df_cluster = df_cluster.dropna()
    
    return df_cluster

def perform_clustering(df, n_clusters=4):
    """
    Perform K-means clustering on the dataset
    """
    # Prepare data
    df_cluster = prepare_data_for_clustering(df)
    
    # Store subject column if it exists
    subject_column = None
    if 'subject' in df_cluster.columns:
        subject_column = df_cluster['subject'].copy()
        df_cluster = df_cluster.drop(columns=['subject'])
    
    # Scale numerical data for better clustering
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df_cluster)
    
    # Apply K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(df_scaled)
    
    # Add clusters back to original dataframe
    result_df = df.copy()
    result_df['cluster'] = clusters
    
    # Return the clustered dataframe and the k-means model
    return result_df, kmeans, scaler

def get_cluster_descriptions(df_with_clusters):
    """
    Generate descriptions for each cluster based on their characteristics
    """
    cluster_descriptions = {}
    
    # Select only the numeric columns for the mean calculation
    numeric_columns = df_with_clusters.select_dtypes(include=['number']).columns
    
    # Make sure 'cluster' is included for groupby
    if 'cluster' not in numeric_columns:
        numeric_df = df_with_clusters[list(numeric_columns) + ['cluster']]
    else:
        numeric_df = df_with_clusters[numeric_columns]
    
    # Get mean values for each cluster (only on numeric columns)
    cluster_means = numeric_df.groupby('cluster').mean()
    
    # Define cluster descriptions based on price and subscribers
    for cluster in cluster_means.index:
        price = cluster_means.loc[cluster, 'price']
        subscribers = cluster_means.loc[cluster, 'num_subscribers']
        
        # Determine price category
        if price < 20:
            price_cat = "Low-priced"
        elif price < 80:
            price_cat = "Medium-priced"
        else:
            price_cat = "High-priced"
            
        # Determine popularity category
        if subscribers < 10000:
            pop_cat = "niche"
        elif subscribers < 50000:
            pop_cat = "moderately popular"
        else:
            pop_cat = "highly popular"
            
        # Create description
        cluster_descriptions[cluster] = f"{price_cat}, {pop_cat} courses"
    
    return cluster_descriptions

def generate_cluster_plot(df_with_clusters, kmeans_model):
    """
    Generate a scatter plot of the clusters
    """
    plt.figure(figsize=(10, 6))
    
    # Create a custom colormap
    colors = ["#4e79a7", "#f28e2c", "#e15759", "#76b7b2", "#59a14f", "#edc949"]
    custom_cmap = LinearSegmentedColormap.from_list("custom", colors[:len(df_with_clusters['cluster'].unique())])
    
    # Create the scatter plot
    sns.scatterplot(
        x=df_with_clusters['price'], 
        y=df_with_clusters['num_subscribers'], 
        hue=df_with_clusters['cluster'], 
        palette=custom_cmap, 
        alpha=0.7,
        s=100
    )
    
    # Plot cluster centers if kmeans_model is provided
    if kmeans_model is not None:
        # Select only numeric columns for the mean calculation
        numeric_columns = df_with_clusters.select_dtypes(include=['number']).columns
        
        # Make sure 'cluster' is included for groupby
        if 'cluster' not in numeric_columns:
            numeric_df = df_with_clusters[list(numeric_columns) + ['cluster']]
        else:
            numeric_df = df_with_clusters[numeric_columns]
        
        # Get mean values for each cluster (only on numeric columns)
        cluster_means = numeric_df.groupby('cluster').mean()
        
        # Check if 'price' and 'num_subscribers' are in the result
        if 'price' in cluster_means.columns and 'num_subscribers' in cluster_means.columns:
            plt.scatter(
                cluster_means['price'], 
                cluster_means['num_subscribers'], 
                s=200, 
                c='red', 
                marker='X', 
                label="Cluster Centers"
            )
    
    plt.xlabel('Price ($)', fontsize=12)
    plt.ylabel('Number of Subscribers', fontsize=12)
    plt.title('Course Clusters by Price and Popularity', fontsize=14)
    plt.legend(title="Cluster")
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Convert plot to base64 image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    return image_base64

def get_course_recommendations_by_cluster(df_with_clusters, user_cluster, n=5):
    """
    Get course recommendations from the user's preferred cluster
    """
    # Filter courses from the user's cluster
    cluster_courses = df_with_clusters[df_with_clusters['cluster'] == user_cluster]
    
    # Sort by number of subscribers (popularity)
    top_courses = cluster_courses.nlargest(n, 'num_subscribers')
    
    # Select relevant columns
    recommended_courses = top_courses[['course_title', 'url', 'is_paid', 'price', 'num_subscribers', 'cluster']]
    
    return recommended_courses

def predict_cluster_for_preferences(price_preference, popularity_preference, kmeans_model, scaler):
    """
    Predict which cluster a user might prefer based on their preferences
    """
    # Create a sample with user preferences
    # Assuming the features are [price, num_subscribers, ...other features...]
    # We'll set other features to their mean values for simplicity
    sample = np.zeros(scaler.mean_.shape)
    sample[0] = price_preference  # Assuming price is the first feature
    sample[1] = popularity_preference  # Assuming num_subscribers is the second feature
    
    # Scale the sample
    scaled_sample = scaler.transform([sample])
    
    # Predict the cluster
    predicted_cluster = kmeans_model.predict(scaled_sample)[0]
    
    return predicted_cluster
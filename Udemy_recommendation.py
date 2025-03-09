from flask import Flask, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load and preprocess dataset
df = pd.read_csv("data/cleaned_udemy_course_dataset.csv")
df.drop_duplicates(inplace=True)
df.dropna(inplace=True)

print("Dataset loaded with shape:", df.shape)  # Debugging

# Convert course titles to numerical vectors
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(df["course_title"])
cosine_sim = cosine_similarity(tfidf_matrix)

# Function to recommend similar courses
def recommend_courses(course_title, n=5):
    print(f"Searching for: {course_title}")  # Debugging

    matched_courses = df[df["course_title"].str.contains(course_title, case=False, na=False, regex=False)]
    
    if matched_courses.empty:
        print("No exact matches found. Returning top recommendations.")  # Debugging
        # Return top n courses based on overall similarity
        similar_indices = cosine_sim.mean(axis=0).argsort()[-n:][::-1]
        recommendations = df.iloc[similar_indices][["course_title", "subject"]].to_dict(orient="records")
    else:
        idx = matched_courses.index[0]  # First matched course
        similar_indices = cosine_sim[idx].argsort()[-(n+1):-1][::-1]
        recommendations = df.iloc[similar_indices][["course_title", "subject"]].to_dict(orient="records")
    
    print("Recommendations:", recommendations)  # Debugging
    return recommendations

# Flask app
app = Flask(__name__)

@app.route('/recommend', methods=['GET'])
def recommend():
    course = request.args.get('course_title')
    print("Received request for:", course)  # Debugging

    recommendations = recommend_courses(course)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)


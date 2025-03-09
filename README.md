# Codeholics Project

## Description
This project is a Udemy course recommendation system built with Python and Streamlit. It utilizes an SQLite database to store and manage course data, applying machine learning techniques to provide personalized course recommendations. The web-based interface allows users to explore courses, filter options, and receive recommendations based on their preferences.

## Features
- Udemy course recommendation system using data analysis and ML techniques.
- Interactive Web UI built with Streamlit.
- SQLite database for efficient data storage and retrieval.
- CRUD operations for managing course data.
- Modular code structure following best software development practices.
- CSV dataset of Udemy courses included for testing.
- Test cases implemented for validating system functionality.

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.x
- pip (Python package manager)

### Steps
1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd Codeholics-updated
   ```
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Project Structure
```
Codeholics-updated/
│-- app.py                      # Main application script
│-- Udemy_recommendation.py     # Recommendation system logic
│-- test.py                     # Testing script
│-- data/
│   └── cleaned_udemy_course_dataset.csv   # Udemy dataset
│-- database/
│   │-- __init__.py              # Database package initializer
│   │-- database.db              # SQLite database
│   │-- db_functions.py          # Database functions
│   │-- models.py                # Database models
│   └── __pycache__/             # Compiled Python files
│-- requirements.txt             # Dependencies
└── README.md                    # Project documentation
```

## Usage
1. Run the Streamlit app to interact with the recommendation system.
2. Input course preferences to receive personalized recommendations.
3. Manage course data via CRUD operations.
4. Use test cases (`test.py`) to validate functionality.

## Technologies Used
- **Python**: Core programming language.
- **Streamlit**: Web framework for building the UI.
- **SQLite**: Lightweight database for storing course data.
- **Pandas**: Data analysis and manipulation.
- **Scikit-learn**: Machine learning algorithms for recommendations.

## Contributors
- **Codeholics Team**

## License
This project is licensed under the MIT License.


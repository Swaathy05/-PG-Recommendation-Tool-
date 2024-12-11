import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

# Load the dataset
def load_data():
    """
    Load PG dataset from the CSV file.
    """
    file_path = 'pg_data_tamilnadu_colleges_updated_10000.csv'
    try:
        pg_data = pd.read_csv(file_path)
        return pg_data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None

# Function to recommend PGs based on user input
def recommend_pgs(pg_data, city="", nearby_college="", max_rent=None, room_type="", amenities=None, max_distance=None, min_rating=None):
    """
    Recommend PGs based on user preferences, including related matches if no exact matches.
    """
    if pg_data is None:
        return None, "Dataset not loaded."

    # Start with the entire dataset
    filtered_pgs = pg_data.copy()

    # Apply filters based on user preferences
    if city:
        filtered_pgs = filtered_pgs[filtered_pgs['City'].str.contains(city, case=False, na=False)]
    if nearby_college:
        filtered_pgs = filtered_pgs[filtered_pgs['Nearby College'].str.contains(nearby_college, case=False, na=False)]
    if max_rent:
        filtered_pgs = filtered_pgs[filtered_pgs['Rent (INR/Month)'] <= int(max_rent)]
    if max_distance:
        filtered_pgs = filtered_pgs[filtered_pgs['Distance to College (km)'] <= float(max_distance)]
    if min_rating:
        filtered_pgs = filtered_pgs[filtered_pgs['Rating'] >= float(min_rating)]
    if room_type:
        filtered_pgs = filtered_pgs[filtered_pgs['Room Type'].str.contains(room_type, case=False, na=False)]
    if amenities:
        for amenity in amenities:
            amenity = amenity.strip()  # Remove extra spaces
            filtered_pgs = filtered_pgs[filtered_pgs['Amenities'].str.contains(amenity, case=False, na=False)]

    # If no exact match found, show related PGs
    if filtered_pgs.empty:
        related_pgs = pg_data.copy()
        
        # Allow partial matching by reducing the number of filters applied
        if city:
            related_pgs = related_pgs[related_pgs['City'].str.contains(city, case=False, na=False)]
        if nearby_college:
            related_pgs = related_pgs[related_pgs['Nearby College'].str.contains(nearby_college, case=False, na=False)]
        if max_rent:
            related_pgs = related_pgs[related_pgs['Rent (INR/Month)'] <= int(max_rent)]
        
        # Sort the related PGs by rating and rent for better suggestions
        related_pgs = related_pgs.sort_values(by=['Rating', 'Rent (INR/Month)'], ascending=[False, True])
        
        return related_pgs.to_dict(orient='records'), "No exact matches found. Here are some related PGs."

    # If matches are found, sort by rating and rent
    filtered_pgs = filtered_pgs.sort_values(by=['Rating', 'Rent (INR/Month)'], ascending=[False, True])

    return filtered_pgs.to_dict(orient='records'), None

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main route for the application.
    """
    if request.method == 'POST':
        # Get user input from the form
        city = request.form.get('city', "").strip()
        nearby_college = request.form.get('nearby_college', "").strip()
        max_rent = request.form.get('max_rent', None)
        room_type = request.form.get('room_type', "").strip()
        amenities = request.form.get('amenities', "").split(',')
        max_distance = request.form.get('max_distance', None)
        min_rating = request.form.get('min_rating', None)

        # Load the dataset
        pg_data = load_data()
        if pg_data is None:
            return render_template('index.html', error="Dataset not found. Please check the CSV file.")

        # Get recommendations based on user input
        recommended_pgs, error_message = recommend_pgs(
            pg_data=pg_data,
            city=city,
            nearby_college=nearby_college,
            max_rent=max_rent,
            room_type=room_type,
            amenities=amenities,
            max_distance=max_distance,
            min_rating=min_rating
        )

        # Render results or error message
        if error_message:
            return render_template('index.html', error=error_message)
        return render_template('index.html', recommended_pgs=recommended_pgs)

    # For GET requests, render the empty form
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)

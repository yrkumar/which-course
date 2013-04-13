from flask import Flask, render_template, request, flash
import pickle
import os

app = Flask(__name__)
app.secret_key = "asdfghjkl"	

@app.route('/')
def index():
	return render_template('index.html')

def get_ratings(filename):	
	# Unpickle course ratings from file "filename" 
	file_handler = open(filename, 'rb')
	ratings = pickle.load(file_handler)
	file_handler.close()
	return ratings	

def not_found_handler(course_terms, course_ratings):
	not_found = []
	for course in course_terms:
		# Handle malformed search queries 
		if course not in course_ratings.keys():
			not_found.append(course)
	if len(not_found) == 1:
		message = not_found[0] + " was not found."
	elif len(not_found) > 1:
		not_found = ", ".join(not_found)
		message = not_found + " were not found."
	# Display error template when search results in errors
	return render_template('error.html', ratings=course_ratings, message=message)

@app.route('/', methods=['GET', 'POST'])
def post():
	# Parse search query, set up ratings
	search_terms = str(request.form['search'])
	search_terms = search_terms.replace("-", "")
	course_terms = search_terms.split(", ")
	ratings = get_ratings('ratings')
	course_ratings = {} # Dict to render resulting reviews
	for course in ratings:
		# add dict key to course_ratings if it's a search term
		if course in course_terms:
			course_ratings[course] = ratings[course]
	# Handle empty search
	if len(course_ratings.keys()) == 0:
		message = "Your search returned no results."
		return render_template('blank.html', message=message)
	# Handle partially empty search
	elif len(course_terms) != len(course_ratings.keys()):
		return not_found_handler(course_terms, course_ratings)
	else: 
		return render_template('search.html', ratings=course_ratings)
	
if __name__ == "__main__":
	# Bind to PORT if defined, otherwise default to 5000.
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)


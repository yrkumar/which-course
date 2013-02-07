from flask import Flask, render_template, request, flash
import pickle
import os

app = Flask(__name__)
app.secret_key = "asdfghjkl"	

@app.route('/')
def index():
	return render_template('index.html')

def get_ratings(filename):	
	file_handler = open(filename, 'rb')
	ratings = pickle.load(file_handler)
	file_handler.close()
	return ratings	

def not_found_handler(course_terms, course_ratings):
	not_found = []
	for course in course_terms:
		if course not in course_ratings.keys():
			not_found.append(course)
	if len(not_found) == 1:
		message = not_found[0] + " was not found."
	elif len(not_found) > 1:
		not_found = ", ".join(not_found)
		message = not_found + " were not found."
	return render_template('error.html', ratings=course_ratings, message=message)

@app.route('/', methods=['GET', 'POST'])
def post():
	search_terms = str(request.form['search'])
	course_terms = search_terms.split(", ")
	ratings = get_ratings('ratings')
	course_ratings = {}
	for course in ratings:
		if course in course_terms:
			course_ratings[course] = ratings[course]
	if len(course_ratings.keys()) == 0:
		message = "Your search returned no results."
		return render_template('blank.html', message=message)
	elif len(course_terms) != len(course_ratings.keys()):
		return not_found_handler(course_terms, course_ratings)
	else:
		return render_template('search.html', ratings=course_ratings)
	
if __name__ == "__main__":
	# Bind to PORT if defined, otherwise default to 5000.
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)


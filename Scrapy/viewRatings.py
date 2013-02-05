import pickle

file_handler = open('ratings', 'r')
ratings = pickle.load(file_handler)
file_handler.close()
for course in ratings:
	print repr(course)
	print ratings[course]
	print "\n"

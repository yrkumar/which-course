which-course
============

Interface to aggregate and display course reviews scraped from [Carnegie Mellon's official faculty evaluation site](http://www.cmu.edu/hub/fce/) (FCE) in a manner that lets students easily compare multiple courses at once. 

Usage
-----

The main use students have for FCE is to compare courses so that they can decide which ones to take in the future. However, FCE is unintuitive for that purpose. Course ratings are displayed by semester and it is not possible to compare different courses side by side. WhichCourse solves this problem. Users can enter multiple course ID's as a search query which will be parsed and split. The aggregated course ratings for the professors who have taught each of the courses will be displayed accordingly in a table, where they can be easily compared.  

See the app in action at [http://whichcourse.herokuapp.com/](http://whichcourse.herokuapp.com). Here is the interface:

<p align="center">
<img src="/static/img/whichcourse.png">
</p> 

Setup & Installation
--------------------

Requirements: Flask 0.9 (install with `pip install Flask`)

To run the application on localhost (using course ratings data from January 2013 - when I last ran the crawler to get new ratings):
```bash
$ git clone git@github.com:yrkumar/which-course.git localDir/
$ cd localDir/
$ python routes.py
```

Contribution
------------

Requirements: 

1. Selenium Chromedriver (see [https://code.google.com/p/selenium/wiki/ChromeDriver](https://code.google.com/p/selenium/wiki/ChromeDriver) to install)
2. Scrapy 0.16 (install with `pip install Scrapy`)

The crawler uses XPath selectors to pull data from the course evaluation pages. Drastic changes to the HTML tags on these pages will cause the crawler to overlook some data on the evaluations site. Reinspection of the HTML tags on the evaluations site and changes to the crawler may be necessary.

If new ratings data is necessary, then:

- Navigate to `Scrapy/whichCourse/spiders/`
- Within `courseSpider.py`, add the path for the chromedriver and a valid CMU Andrew ID/password combination:

```python        
def setup(self):
	# Start Selenium for user authentication and interacting with 
	# JavaScript elements on the page 
	driver = "/path/to/chromedriver/"
	self.driver = webdriver.Chrome(driver)
	self.driver.implicitly_wait(30)
	base_url = "https://cmuandrew.onlinecourseevaluations.com"
	self.driver.get(base_url)
	usr, pwd = "j_username", "j_password"
	usr_text, pwd_text = "*****", "*******"
```

- Make the necessary changes to `courseSpider.py` based on your reinspection of the FCE site
- Navigate back to `Scrapy/` and run `scrapy crawl courseSpider`
- The crawler will start and generate a [pickled](http://docs.python.org/2/library/pickle.html) ratings file when it is complete
- Move the ratings file up a directory and run the app on localhost for testing.

About
-----

Visit [my personal webpage](http://yrkumar.github.io) to learn more.


from scrapy. selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from scrapy.http import HtmlResponse

from selenium import webdriver

import pickle

#from whichCourse.items import Rating

class CourseSpider(BaseSpider):
	name = 'onlinecourseevaluations.com'
	start_urls = [ 'https://cmuandrew.onlinecourseevaluations.com' ]

	def parse(self, response):
		self.init_urls()
		self.setup()
		# Dictionary to store course ratings
		#	{ 'course1' : { 'Instructor1' : ratingDict, 
		#					'Instructor2' : ratingDict }, 
		#	  'course2' : { 'Instructor1' : ratingDict, 
		#					'Instructor2' : ratingDict } }
		self.ratings = {}
		for url in self.urls:
			self.get_ratings(url)
		self.driver.close()	
		self.round_ratings()
		self.normalize_format()	
		self.pickle_ratings()

	def init_urls(self):
		self.urls = self.load_text_list("urls.txt")
		self.format_urls()
	
	def load_text_list(self, file_name):
		file_handler = open(file_name, "rt")
		text = file_handler.readlines() 
		file_handler.close() 
		return text
	
	def format_urls(self):
		for url in self.urls:
			self.urls[self.urls.index(url)] = url[:-1]

	def setup(self):
		driver = "/Users/yashaskumar/Desktop/TechProjects/whichCourse/Scrapy/chromedriver"
		self.driver = webdriver.Chrome(driver)
		self.driver.implicitly_wait(30)
		base_url = "https://cmuandrew.onlinecourseevaluations.com"
		self.driver.get(base_url)
		usr, pwd = "j_username", "j_password"
		usr_text, pwd_text = "yrkumar", "Rvaatmdm_1"
		self.driver.find_element_by_name(usr).clear()
		self.driver.find_element_by_name(usr).send_keys(usr_text)
		self.driver.find_element_by_name(pwd).clear()
		self.driver.find_element_by_name(pwd).send_keys(pwd_text)
		self.driver.find_element_by_name("submit").click()
		past_yrs_id = "_ctl0_See Results From Past Years"
		self.driver.find_element_by_id(past_yrs_id).click()

	def get_ratings(self, url):
		self.driver.get(url)
		d_id = "_ctl0_cphContent_rddset_sfexporter_drp_FileType"
		dropdown = self.driver.find_element_by_id(d_id)
		for option in dropdown.find_elements_by_tag_name("option"):
			if option.text == "HTML: Web Page":
				option.click()
				break
		sub_id = "_ctl0_cphContent_rddset_sfexporter_btnSubmit"
		self.driver.find_element_by_id(sub_id).click()
		self.driver.refresh()
		body = str(self.driver.page_source)
		self.parse_page(url, body)
		
	def parse_page(self, url, body):
		response = HtmlResponse(url = url, body = body)
		hxs = HtmlXPathSelector(response)	
		ratings = hxs.select("//tr")
		self.parse_ratings(ratings)

	def parse_ratings(self, ratings):	
		rating_num = 0
		for rating in ratings:
			rating_num += 1
			if rating_num > 6:
				try:
					year = int(rating.select("td[2]/text()").extract()[0])
					if year < 2010: continue
					ID = str(rating.select("td[5]/text()").extract()[0])
					num_ratings = int(rating.select("td[9]/text()").extract()[0])
					if num_ratings < 10: continue
					teacher = str(rating.select("td[3]/text()").extract()[0])
					teacher = teacher.strip()
					teacher = teacher.replace("  (co-taught)", "")
					self.add_rating(rating, ID, teacher)
				except:
					continue

	def add_rating(self, rating, ID, teacher):	
		if ID in self.ratings:
			self.add_to_course(rating, ID, teacher)
		else:
			self.new_course(rating, ID, teacher)

	def add_to_course(self, rating, ID, teacher):
		if teacher in self.ratings[ID]:
			self.add_to_instructor(rating, ID, teacher)
		else:
			self.new_instructor(rating, ID, teacher)
	
	def add_to_instructor(self, rating, ID, teacher):
		addition = {}	
		self.get_rating_values(rating, addition)
		for key in addition:
			if key not in ['course_name', 'num_ratings']:
				addition[key] *= addition['num_ratings']
		exist_eval = self.ratings[ID][teacher]
		for key in exist_eval:
			if key not in ['course_name', 'num_ratings']:
				exist_eval[key] = (exist_eval[key] *
				exist_eval['num_ratings'] + 
				addition[key])/(exist_eval['num_ratings'] + 
				addition['num_ratings'])
		exist_eval['num_ratings'] += addition['num_ratings']
		self.ratings[ID][teacher] = exist_eval
	
	def get_rating_values(self, rating, addition):	
		addition['course_name'] = str(
		rating.select("td[6]/text()").extract()[0])
		addition['num_ratings'] = int(
		rating.select("td[9]/text()").extract()[0])
		addition['hours'] = float(
		rating.select("td[12]/text()").extract()[0])
		addition['importance'] = float(
		rating.select("td[17]/text()").extract()[0])
		addition['explain'] = float(
		rating.select("td[18]/text()").extract()[0])
		addition['teaching'] = float(
		rating.select("td[20]/text()").extract()[0])
		addition['overall'] = float(
		rating.select("td[21]/text()").extract()[0])

	def new_instructor(self, rating, ID, teacher): 
		addition = {}
		self.get_rating_values(rating, addition)
		self.ratings[ID][teacher] = addition 			

	def new_course(self, rating, ID, teacher):
		self.ratings[ID] = {}
		addition = {}
		self.get_rating_values(rating, addition)
		self.ratings[ID][teacher] = addition
		
	def round_ratings(self):	
		for course in self.ratings:
			for instructor in self.ratings[course]:
				self.ratings[course][instructor]['course'] = course 
				for key in self.ratings[course][instructor]:
					if key not in ['course', 'course_name', 'num_ratings']:
						self.ratings[course][instructor][key] = float("%.1f" % 
						self.ratings[course][instructor][key])
						
	def normalize_format(self):
		for course in self.ratings:
			for instructor in self.ratings[course]:
				for key in self.ratings[course][instructor]:
					if key not in ['course', 'course_name', 'num_ratings', 'hours']:
						self.ratings[course][instructor][key] = int(
						self.ratings[course][instructor][key] * 20)


	def pickle_ratings(self):
		file_handler = open('ratings', 'w')
		pickle.dump(self.ratings, file_handler)
		file_handler.close()		


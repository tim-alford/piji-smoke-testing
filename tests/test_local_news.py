# vim: ts=2
import os
import re
import json
from time import sleep
import unittest
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from pandas import read_excel
import openpyxl

class TestLocalNews(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.options = ChromeOptions()
		cls.options.add_experimental_option("prefs", {
			"download.default_directory": ".",
			"download.prompt_for_download": False,
			"download.directory_upgrade": True,
			"safebrowsing.enabled": True
		})
		cls.driver = webdriver.Chrome(options=cls.options)
		cls.driver.maximize_window()
		website = "LOCAL_NEWS_WEBSITE"
		if website not in os.environ.keys():
			raise Exception(f"Please set the {website} variable before running the suite")
		cls.website = os.environ[website]
		if "TEST_ENV" not in os.environ.keys():
			raise Exception("Please set the TEST_ENV variable before running the suite")
		cls.env = os.environ["TEST_ENV"]
		
	@classmethod
	def tearDownClass(cls):
		cls.driver.quit()
	
	def wait_until_map_is_ready(self):
		cls = self.__class__
		cls.driver.get(cls.website)
		ready = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.ID, "mapReady"))
	
	def test_scale_filter_options(self):
		cls = self.__class__
		driver = cls.driver
		self.wait_until_map_is_ready()
		scale = WebDriverWait(driver, timeout=60).until(lambda x: x.find_element(By.ID, "scaleFilter"))
		scale.click()
		local = WebDriverWait(driver, timeout=60).until(lambda x: x.find_element(By.ID, "scaleOptions_local"))
		metro = WebDriverWait(driver, timeout=60).until(lambda x: x.find_element(By.ID, "scaleOptions_metro"))
		community = WebDriverWait(driver, timeout=60).until(lambda x: x.find_element(By.ID, "scaleOptions_community"))
		
	def test_primary_format_filter_options(self):
		cls = self.__class__
		driver = cls.driver
		self.wait_until_map_is_ready()
		pf = WebDriverWait(driver, timeout=60).until(lambda x: x.find_element(By.ID, "primaryFormatFilter"))
		pf.click()
		_print = WebDriverWait(driver, timeout=60).until(lambda x: x.find_element(By.ID, "primaryFormatOptions_print"))
		digital = WebDriverWait(driver, timeout=60).until(lambda x: x.find_element(By.ID, "primaryFormatOptions_digital"))
	
	def test_local_news_current_date(self):
		cls = self.__class__
		driver = cls.driver
		self.wait_until_map_is_ready()
		one = driver.find_element(By.ID, "legend_one")
		two = driver.find_element(By.ID, "legend_two")
		three = driver.find_element(By.ID, "legend_three")
		four = driver.find_element(By.ID, "legend_four")
		five = driver.find_element(By.ID, "legend_five")
		legends = [one, two, three, four, five]
		colours = [x.value_of_css_property("background-color") for x in legends]
		codes = {}
		r = re.compile("rgba\(([0-9]+), ([0-9]+), ([0-9]+), [0-9]+\)")
		for i in range(0, len(colours)):
			c = colours[i]
			result = r.match(c)
			if result is None:
				raise Exception(f"RGBA colour failed to match regex {c}")
			red = int(result.group(1))
			green = int(result.group(2))
			blue = int(result.group(3))
			hexCode = "#{r:02x}{g:02x}{b:02x}".format(r=red, g=green, b=blue)
			codes[hexCode.upper()] = i+1 # map colour to expected outlet count
		self.assertEqual(codes["#243B4C"], 1)
		self.assertEqual(codes["#2D6186"], 2)
		self.assertEqual(codes["#6396AB"], 3)
		self.assertEqual(codes["#91B6B2"], 4)
		self.assertEqual(codes["#C3DFCA"], 5)
		style = WebDriverWait(driver, timeout=60).until(lambda x: x.find_element(By.ID, "currentStyle"))
		lgas = style.get_attribute("value")
		lgas = json.loads(lgas)
		fills = lgas["fill"]
		# determine counts for each lga
		# test one of each count, 1, 2, 3, 4, 5+
		eastGippslandShire = codes[fills[fills.index("22110")+1]]
		southernGrampiansShire = codes[fills[fills.index("26260")+1]]
		hindmarshShire = codes[fills[fills.index("22980")+1]]
		walgettShireCouncil = codes[fills[fills.index("17900")+1]]
		douglasShire = codes[fills[fills.index("32810")+1]]
		# use lga code in URL to navigate to that LGA
		currentUrl = driver.current_url
		gippsland = "{url}/22110".format(url=currentUrl)
		driver.get(gippsland)
		outlets = WebDriverWait(driver, timeout=60).until(lambda x: x.find_element(By.ID, "lgaOutlets"))
		outlets = WebDriverWait(driver, timeout=60).until(lambda x: x.find_elements(By.CSS_SELECTOR, "div[name='outletName']"))
		# assert outlet counts
		self.assertEqual(len(outlets), eastGippslandShire, f"East gippsland shire should have {eastGippslandShire} linked to it.")
		# repeat this check for the other lgas too
		# grampians
		grampians = "{url}/26260".format(url=currentUrl)
		driver.get(grampians)
		outlets = WebDriverWait(driver, timeout=60).until(lambda x: x.find_elements(By.CSS_SELECTOR, "div[name='outletName']"))
		self.assertEqual(len(outlets), southernGrampiansShire, f"Southern grampians shire should have {southernGrampiansShire} linked to it.")
		# hindmarsh, 7 outlets
		# need to test for >= as bracket is 5+ outlets
		hindmarsh = "{url}/22980".format(url=currentUrl)
		driver.get(hindmarsh)
		outlets = WebDriverWait(driver, timeout=60).until(lambda x: x.find_elements(By.CSS_SELECTOR, "div[name='outletName']"))
		self.assertGreaterEqual(len(outlets), hindmarshShire, f"Hindmarsh shire should have {hindmarshShire} linked to it.")
		# walgett
		walgett = "{url}/17900".format(url=currentUrl)
		driver.get(walgett)
		outlets = WebDriverWait(driver, timeout=60).until(lambda x: x.find_elements(By.CSS_SELECTOR, "div[name='outletName']"))
		self.assertEqual(len(outlets), walgettShireCouncil, f"Walgett shire council should have {walgettShireCouncil} linked to it.")
		# douglas
		douglas = "{url}/32810".format(url=currentUrl)
		driver.get(douglas)
		outlets = WebDriverWait(driver, timeout=60).until(lambda x: x.find_elements(By.CSS_SELECTOR, "div[name='outletName']"))
		self.assertEqual(len(outlets), douglasShire, f"Douglas shire should have {douglasShire} linked to it.")

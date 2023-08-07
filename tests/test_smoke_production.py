# vim: ts=2
import os
import json
from time import sleep
import unittest
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from pandas import read_excel
import openpyxl

class SmokeTestProduction(unittest.TestCase):
		
	@classmethod
	def loadTerms(cls):
		with open("./data/terms.json", "r") as f:
			return json.load(f)
			
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
		if "WEBSITE_FOR_TESTING" not in os.environ.keys():
			raise Exception("Please set the WEBSITE_FOR_TESTING variable before running the suite")
		cls.website = os.environ["WEBSITE_FOR_TESTING"]
		cls.businessWebsite = f"{os.environ['WEBSITE_FOR_TESTING']}/businesses"
		if "TEST_ENV" not in os.environ.keys():
			raise Exception("Please set the TEST_ENV variable before running the suite")
		cls.env = os.environ["TEST_ENV"]
		cls.terms = cls.loadTerms()[cls.env]
		
	@classmethod
	def tearDownClass(cls):
		cls.driver.quit()
	
	def does_download_exist(self, fileName):
		user = os.environ["USER"]
		downloadPath = f"/home/{user}/Downloads/{fileName}"
		print(f"Checking path {downloadPath}")
		return (os.path.exists(downloadPath), downloadPath)

	def test_outlet_export_is_working(self):
		cls = self.__class__
		cls.driver.get(cls.website)
		outlets = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.ID, "OutletTable"))
		cls.driver.find_element(By.ID, "DataMenu").click()
		cls.driver.find_element(By.ID, "downloadExport").click()
		download = "Australian News Index (PIJI).xlsx"
		destination = None
		timeout = 60
		while True:
			(result, path) = self.does_download_exist(download)
			if result:
					destination = path
					break
			sleep(1)
			timeout -= 1
			if timeout <= 0:
				self.fail("Failed to find export within 60 seconds")
				break
		self.assertTrue(destination is not None, "Failed to find XLSX export.")
		cls.driver.save_screenshot("./screenshots/test_outlet_export_is_working.png")
		try:
			book = openpyxl.load_workbook(destination)
			self.assertEqual(len(book.sheetnames), 2)
			self.assertTrue("News producers" in book.sheetnames)
			self.assertTrue("News entities" in book.sheetnames)
			outlets = book["News producers"]
			entities = book["News entities"]
			self.assertTrue(outlets.max_row > 1, "Number of outlets in export should be non zero")
			self.assertTrue(entities.max_row > 1, "Number of entities in export should be non zero")
		finally:
			os.remove(destination)
	
	def get_business_ids(self, table):
		rows = table.find_elements(By.TAG_NAME, "tr")
		self.assertTrue(len(rows) > 0, "Business count should be non zero")
		ids = []
		# find all outlet ids on this page
		for row in rows:
			id = row.get_attribute("id")
			if id is not None and id != "":
				tokens = id.split("_")
				entityId = tokens[-1]
				firstPart = tokens[0]
				if firstPart != "GenericTableRow":
					continue
				ids.append(entityId)
		return ids

	def get_outlet_ids(self, table):
		rows = table.find_elements(By.TAG_NAME, "tr")
		self.assertTrue(len(rows) > 0, "Outlet count should be non zero")
		ids = []
		# find all outlet ids on this page
		for row in rows:
			id = row.get_attribute("id")
			if id is not None and id != "":
				tokens = id.split("_")
				outletId = tokens[-1]
				ids.append(outletId)
		return ids

	def test_outlets_view(self):
		cls = self.__class__
		cls.driver.get(cls.website)
		outlets = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.ID, "OutletTable"))
		ids = self.get_outlet_ids(outlets)
		records = {}
		cls.driver.save_screenshot("./screenshots/test_outlets_view.png")
		# check attributes for each outlet are visible
		# name, format, scale, state all are required
		for i in ids:
			name = f"Outlet_{i}_name"
			scale = f"Outlet_{i}_scale"
			fmt = f"Outlet_{i}_format"
			state = f"Outlet_{i}_state"
			name = cls.driver.find_element(By.ID, name)
			scale = cls.driver.find_element(By.ID, scale)
			fmt = cls.driver.find_element(By.ID, fmt)
			state = cls.driver.find_element(By.ID, state)
			self.assertTrue(name is not None, "Failed to find name cell")
			self.assertTrue(scale is not None, "Failed to find scale cell")
			self.assertTrue(state is not None, "Failed to find state cell")
			self.assertTrue(fmt is not None, "Failed to find format cell")
			name = name.text
			state = state.text
			scale = scale.text
			fmt = fmt.text
			self.assertTrue(name is not None and name != "")
			self.assertTrue(scale is not None and scale != "")
			self.assertTrue(fmt is not None and fmt != "")
			self.assertTrue(state is not None and state != "")

	def test_business_view(self):
		cls = self.__class__
		cls.driver.get(cls.website)
		outlets = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.ID, "OutletTable"))
		businesses = cls.driver.find_element(By.ID, "businessPage")
		self.assertTrue(businesses is not None)
		businesses.click()
		entities = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.ID, "BusinessTable"))
		self.assertTrue(entities is not None)
		cls.driver.save_screenshot("./screenshots/test_business_view.png")
		rows = entities.find_elements(By.TAG_NAME, "tr")
		self.assertTrue(len(rows) > 0, "Business entity count should be greater than zero")
		ids = []
		for r in rows:
			rowId = r.get_attribute("id")
			if rowId is not None and rowId != "":
				tokens = rowId.split("_")
				entityId = tokens[-1]
				ids.append(entityId)
		for i in ids:
			entityType = f"GenericTableCell_Entity type_{i}"
			name = f"GenericTableCell_Name_{i}"
			name = cls.driver.find_element(By.ID, name)
			entityType = cls.driver.find_element(By.ID, entityType)
			self.assertTrue(name is not None)
			self.assertTrue(entityType is not None)
			name = name.text
			entityType = entityType.text
			self.assertTrue(name is not None and name != "")
			self.assertTrue(entityType is not None and entityType != "")

	def test_filter_outlets_primary_format(self):
		cls = self.__class__
		cls.driver.get(cls.website)
		outlets = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.ID, "OutletTable"))
		cls.driver.find_element(By.ID, "primaryFormat").click()
		cls.driver.find_element(By.ID, "primaryFormat_Print").click()
		outlets = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.ID, "OutletTable"))
		ids = self.get_outlet_ids(outlets)
		cls.driver.save_screenshot("screenshots/test_filter_outlets_primary_format.png")
		for i in ids:
			fmt = f"Outlet_{i}_format"
			fmt = cls.driver.find_element(By.ID, fmt)
			self.assertTrue(fmt is not None, "Failed to find format cell")
			fmt = fmt.text.strip()
			self.assertEqual(fmt, "Print", "All outlets should a primary format of print")
			
	def test_filter_outlets_scale(self):
		cls = self.__class__
		cls.driver.get(cls.website)
		outlets = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.ID, "OutletTable"))
		cls.driver.find_element(By.ID, "scale").click()
		cls.driver.find_element(By.ID, "scale_National").click()
		outlets = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.ID, "OutletTable"))
		ids = self.get_outlet_ids(outlets)
		cls.driver.save_screenshot("screenshots/test_filter_outlets_scale.png")
		for i in ids:
			scale = f"Outlet_{i}_scale"
			scale = cls.driver.find_element(By.ID, scale)
			self.assertTrue(scale is not None, "Failed to find format cell")
			scale = scale.text.strip()
			self.assertEqual(scale, "National", "All outlets should a primary format of print")
	
	def test_filter_outlets_subservice(self):
		pass
	
	def test_filter_outlets_broadcast_area(self):
		pass
	
	def test_filter_outlets_coverage(self):
		cls = self.__class__
		cls.driver.get(cls.website)
		outlets = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.ID, "OutletTable"))
		cls.driver.find_element(By.ID, "coverage").click()
		autocomplete = cls.driver.find_element(By.ID, "coverage_text_filter")
		term = cls.terms["lga"]
		autocomplete.send_keys(term)
		popper = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.CLASS_NAME, "MuiAutocomplete-popper"))
		option = cls.driver.find_element(By.ID, "coverage_text_filter-option-0")
		lga = option.text.lower()
		option.click()
		outlets = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.ID, "OutletTable"))
		ids = self.get_outlet_ids(outlets)
		results = []
		for i in ids:
			coverage = cls.driver.find_element(By.ID, f"Outlet_{i}_coverage")
			lgas = coverage.text.strip().lower()
			results.append(lga in lgas)
		self.assertTrue(any(results), "Failed to find any outlet where LGA string {lga} is in coverage")
		cls.driver.save_screenshot("screenshots/test_filter_outlets_coverage.png")
		
	def test_filter_entities_entity_type(self):
		cls = self.__class__
		cls.driver.get(cls.businessWebsite)
		businesses = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.ID, "BusinessTable"))
		entityType = cls.driver.find_element(By.ID, "entityType")
		entityType.click()
		option = cls.terms["entityType"]
		checkbox = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.ID, f"entityType_{option}"))
		checkbox.click()
		businesses = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.ID, "BusinessTable"))
		ids = self.get_business_ids(businesses)
		self.assertTrue(len(ids) > 0, "There should be at least one business entity")
		option = option.lower()
		for i in ids:
			entityType = f"GenericTableCell_Entity type_{i}"
			entityType = cls.driver.find_element(By.ID, entityType)
			entityType = entityType.text.strip().lower()
			self.assertEqual(entityType, option, f"All visible business entities should be of entity type {option}")
	
	def test_filter_outlets_news_entity(self):
		cls = self.__class__
		cls.driver.get(cls.website)
		outlets = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.ID, "OutletTable"))
		cls.driver.find_element(By.ID, "business_accordion").click()
		autocomplete = cls.driver.find_element(By.ID, "news_business_text_filter")
		term = cls.terms["news_entity"]
		autocomplete.send_keys(term)
		popper = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.CLASS_NAME, "MuiAutocomplete-popper"))
		option = cls.driver.find_element(By.ID, "news_business_text_filter-option-0")
		business = option.text.lower()
		option.click()
		outlets = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.ID, "OutletTable"))
		ids = self.get_outlet_ids(outlets)
		for i in ids:
			entity = cls.driver.find_element(By.ID, f"Outlet_{i}_news_entity")
			entityName = entity.text.strip().lower()
			self.assertEqual(entityName, business, f"Outlets should have a news entity of {business}, found {entityName}")

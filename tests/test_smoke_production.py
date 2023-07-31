# vim: ts=2
import os
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
class SmokeTestProduction(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.driver = webdriver.Chrome()
		cls.website = os.environ["WEBSITE_FOR_TESTING"]

	@classmethod
	def tearDownClass(cls):
		cls.driver.quit()

	def test_export_is_working(self):
		pass

	def test_outlets_view(self):
		cls = self.__class__
		cls.driver.get(cls.website)
		outlets = WebDriverWait(cls.driver, timeout=60).until(lambda x: x.find_element(By.ID, "OutletTable"))
		rows = outlets.find_elements(By.TAG_NAME, "tr")
		self.assertTrue(len(rows) > 0, "Some rows should exist")
		cls.driver.save_screenshot("./screenshots/test_outlets_view.png")
		ids = []
		records = {}
		# find all outlet ids on this page
		for row in rows:
			id = row.get_attribute("id")
			if id is not None and id != "":
				tokens = id.split("_")
				outletId = tokens[-1]
				ids.append(outletId)
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
		pass

	def test_filter_outlets_primary_format(self):
		pass

	def test_filter_outlets_scale(self):
		pass

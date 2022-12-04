from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import bs4 as bs
import requests
import time
import sys
import os


# Opens a headless selenium browser and defaults to the manganato site.
# The inputed manga title will be searched in the search bar, and the first option will be chosen
def get_link(manga):
	manga_site = "https://manganato.com/"
	drivers = "/drivers/chromedriver.exe"
	options = webdriver.ChromeOptions()
	options.add_argument('--ignore-certificate-errors-spki-list') # blocks errors that may appear from chrome related things
	options.add_argument('--ignore-ssl-errors')
	options.add_argument('--log-level=3')
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.add_argument('headless')

	# Opens the browser and goes to the manga site
	print("Connecting to site...")
	browser = webdriver.Chrome(drivers, options=options)
	browser.get(manga_site)

	# full xpath for the searchbar that will be inputed into
	searchbar = browser.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/form/input[1]').send_keys(manga)
	print("--- CONNECTION SUCCESSFUL ---")

	# Tries to keep collecting the search results as some connections may be
	# slower than others. This will deal with connection times
	while True:
		try:
			search_result = browser.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/form/div/ul/a')
			break
		except:
			pass

	# Gets the link of the manga found in search bar and goes to it
	print("--- FOUND MANGA ---")
	link = search_result.get_attribute("href")
	browser.get(link)

	# Once again, tries to collect the name of the manga. Will deal with different speeds of connections
	print("--- LOADING DATA ---")
	while True:
		try:
			name = browser.find_element_by_xpath('/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1').text
			break
		except:
			pass
	
	return name, link


# This will use the link and name retrieved from the get_link method, along with the pathname of the manga
# to download the chapters.
def download_manga(parentName, name, link):
	os.system('cls')
	print("=======================================================================")
	print("		        DOWNLOADING " + name)
	print("=======================================================================")
	# Headers that allow searches and requests to be made without being redirected
	headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Accept-Language": "en-US,en;q=0.9",
           "Referer": link}

    # Gets the page contents at the manga link and gets it into a beautiful soup object
	source = requests.get(link).text
	soup = bs.BeautifulSoup(source, 'lxml')

	# Collects the chapters list box that holds the links to every chapter
	content = chapters = soup.find('ul', class_='row-content-chapter')
	# The actual individual chapters collected into an array
	chapters = content.find_all('li')
	# Tries to create parente directory, "Material/'manga_name'"
	# In the event a download retry of a manga happens, a directory can be
	# accounted for, either created or already existing
	try:
		os.mkdir(parentName + "/" + name)
	except:
		pass
	# Reverses the chapters array as collected in descending order
	# Gets link to each chapter in the list and requests the html
	for chapter in reversed(chapters):
		current_chapter_source = requests.get(chapter.find('a').get('href')).text
		current_chapter = bs.BeautifulSoup(current_chapter_source, 'lxml')

		# Container that houses the information for the current chapter link
		container = current_chapter.find('div', class_='container-chapter-reader')
		# This contains all of the panels in the chapter being parsed
		img_links_container = container.find_all('img')

		# Some manga's have a chapter naming including a space, "Chapter 1 : A Chapter"
		# And some do not have this space, this portion deals with these cases
		file_counter = 1
		title = chapter.find('a').text.split(':')
		title_string = ""
		if title[0][-1] == " ":
			title_string = title[0][:-1]
		else:
			title_string = title[0]

		# The directory name of the current chapter
		# EXAMPLE: "Material/'manga_name'/Chapter 1"
		dir_name = parentName + "/" + name + "/" + title_string

		# Tries to create the directory with this name, in event a download retry
		try:
			os.mkdir(dir_name)
		except:
			pass

		# The request and saving of image file in each chapter
		# Naming method: Each panel will be incremented starting at 10 up to 19
		# Then restarts at the next tens digit. This allows os.listdir() to
		# return an ordered array for parsing
		# Example: 10.jpg, 11.jpg, 12.jpg ... 20.jpg, 21.jpg, 22.jpgs
		# file_counter1 is tens digit
		# file_counter2 is one's digit
		size = len(img_links_container)
		file_counter1 = 1
		file_counter2 = 0
		counter = 1
		print(title[0] + "/" + str(len(chapters)))
		for item in img_links_container:
			img_link = item.get('src')
			img_data = requests.get(img_link, headers=headers).content
			with open(dir_name + "/" + (str(file_counter1) + str(file_counter2)) + '.jpg', 'wb') as writer:
				writer.write(img_data)
			# Printing percentages to show progress
			sys.stdout.write("\r" + str( int(counter/size * 100)) + "%")
			sys.stdout.flush()
			counter += 1
			if file_counter2 == 9:
				file_counter1 += 1
				file_counter2 = 0
			else:
				file_counter2 += 1
		print()

	print("-- DOWNLOAD COMPLETED --")


def main():
	find_manga = input("Search manga: ")

	name, link = get_link(find_manga)

	print("--- RESULTS ---")
	print(name + ": " + link)\

	success = input("Is this right(y/n)?: ")
	if success == "y":
		# Tries to create parent directory. Will be made if not existing
		# If does not exist, 'Material' directory will be made
		print("Creating parent directory...")
		try:
			os.mkdir("Material")
		except:
			print("'Material' directory already exists.")
			print("--- PREPARING TO DOWNLOAD ---")

		# RUNS THE DOWNLOAD METHOD
		download_manga("Material", name, link)
	else:
		print("--- QUITTING ---")

main()
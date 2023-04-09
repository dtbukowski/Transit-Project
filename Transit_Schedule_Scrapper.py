from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
import re

def parse_time_range(time_range):
    print(time_range)
    times = re.findall(r"(\d+:\d+[apm]+)", time_range)
    return times[0], times[1]

# Initialize a WebDriver instance
driver = webdriver.Chrome()

# Navigate to the schedules page
driver.get("https://www.transitchicago.com/schedules/")


# Find the bus route dropdown menu and get its HTML
route_dropdown = driver.find_element(By.ID, "CT_Main_1_drpBusRouteSelection")
print(route_dropdown)
route_dropdown_html = route_dropdown.get_attribute("innerHTML")

# Use BeautifulSoup to parse the dropdown menu HTML and extract the value attribute of each option element
soup = BeautifulSoup(route_dropdown_html, "html.parser")
option_tags = soup.find_all("option")
route_numbers = [option.text.split(" ")[0] for option in option_tags]
route_numbers.pop(0)
results = []


# Construct the URL for each bus route page using the route numbers
for route_num in route_numbers:
    try:
        route_url = f"https://www.transitchicago.com/bus/{route_num}/"
        # Do something with the URL, like navigate to the route page or save it to a list
        driver.get(route_url)

        # Find the dropdown element containing the route options
        route_dropdown = driver.find_element(By.ID, "CT_Main_0_pnBusRoute")

        # Get the HTML code for the dropdown element
        dropdown_html = route_dropdown.get_attribute("innerHTML")

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(dropdown_html, "html.parser")

        
        # Find the elements containing the schedule information
        schedule_divs = soup.find_all("div", {"class": "service-notes-line"})
        #print(len(schedule_divs))


        northbound_info = schedule_divs[0].find_all("div")[1].text.strip()
        southbound_info = schedule_divs[0].find_all("div")[3].text.strip()

        time_pattern = r'(\d{1,2}:\d{2}[ap]-\d{1,2}:\d{2}[ap])'
        northbound_times = re.findall(time_pattern, northbound_info)
        southbound_times = re.findall(time_pattern, southbound_info)
        while len(northbound_times) < 3:
            northbound_times.append("NA")
        while len(southbound_times) < 3:
            southbound_times.append("NA")

        times = [route_num] + northbound_times + southbound_times
        print(northbound_info)
        print(southbound_info)
        print(times)
        results.append(times)
         
        

        #schedule = soup.find("div", class_="service-notes-line").get_text(strip=True)
        #print(schedule)
        #northbound_weekdays, northbound_saturday, northbound_sunday = schedule.split(", ")
        #results.append((route, northbound_weekdays, northbound_saturday, northbound_sunday))

    except Exception as e:
        print("ERROR : "+str(e))
        print(route_url)

with open("bus_routes.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Route", "Northbound Weekdays", "Northbound Saturday", "Northbound Sunday", "Southbound Weekdays", "Southbound Saturday", "Southbound Sunday"])
    writer.writerows(results)

# Close the WebDriver instance
driver.quit()
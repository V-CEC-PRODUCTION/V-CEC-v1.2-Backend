import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_month_number(month_name):
    try:
        month_number = datetime.strptime(month_name, "%b").month
        month_number_str = f"{month_number:02d}"
        return month_number_str
    except ValueError:
        return None
      
def ktu_webs_announce():
    url = "https://ktu.edu.in/Menu/announcements.htm"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # ? Find the container element that holds the announcements
    container = soup.find("div", class_="p-t-15 p-b-15 shadow row  m-b-25 row")

    if container is not None:
        # ? Find all the announcement items within the container
        announcement_items = container.find_all("td", class_="align-center")
        
        ktu_announcements = []
        for item in announcement_items[:15]:
            month = item.find("b").text.strip()
            day = item.find("label", class_="news-date").text.strip()
            year = item.find("strong").text.strip()

            ul_element = item.find_next_sibling("td").find("ul").find("li")
            headline_element = ul_element.find("b")
            link_element = ul_element.find_all("a")
            
            
            if ul_element is not None:
                d = {}
                details = headline_element.next_sibling.strip()
                headline = headline_element.text.strip()
                if link_element is not None:
                    url_info = []
                    for urls in link_element:
                        url = "https://ktu.edu.in" + urls.get('href', '').split('\n')[0] if urls else ""
                        url_file = urls.text.strip() if urls else ""
                        url_info.append({
                            "url": url,
                            "url_head": url_file
                        })
            month = get_month_number(month[4:7])
            day_number = int(day[8:10])
            day_number_str = f"{day_number:02d}"
                
            d = {
        
            "date_of_upload": year[-4:] +  "-" + str(month) +   "-" + str(day_number_str),
            "headline": headline,
            "notice_urls": url_info,
            "details": details
        
            }
            ktu_announcements.append(d)
            
        return ktu_announcements  
    else:
        print("Container element not found.")
        
        
if __name__ == "__main__":
    ktu_webs_announce()
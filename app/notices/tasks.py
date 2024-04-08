from datetime import datetime
from bs4 import BeautifulSoup
from celery import shared_task
from django.core.cache import cache
import requests
import json
from playwright.sync_api import sync_playwright
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
BASE_URL = 'https://ktu.edu.in/menu/announcements'
COLUMNS = ['title', 'date', 'description', 'download_count', 'download_url', 'download_name']
CSV_FILE = 'announcements.csv'

def download_content(page, announcement, download_files=False):
    downloadable_contents = announcement.query_selector_all("button")
    download_count = len(downloadable_contents)
    download_url = []
    download_name = []
    for downloadable_content in downloadable_contents:
        with page.expect_download() as download_info:
            downloadable_content.click()
            download = download_info.value
            download_url.append(download.url)
            download_name.append(download.suggested_filename)
            if download_files:
                download.save_as("./download_data/" + download.suggested_filename)
            else:
                download.cancel()
    return download_count, download_url, download_name


notices = []
def ktu_web_scrap_announcement():
    months = {
        'January': '1',
        'February': '2',
        'March': '3',
        'April': '4',
        'May': '5',
        'June': '6',
        'July': '7',
        'August': '8',
        'September': '9',
        'October': '10',
        'November': '11',
        'December': '12'
    }

    with sync_playwright() as pw:
        browser = pw.firefox.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(BASE_URL, wait_until='load', timeout=100000)

        page_count = 0
        while page_count < 1:
            page_count += 1
            print(f'Page {page_count}')
            page.wait_for_timeout(1000)
            page.wait_for_selector("div[class='p-t-15 p-b-15 shadow row  m-b-25 row']", timeout=100000)
            announcements = page.query_selector_all("div[class='p-t-15 p-b-15 shadow row  m-b-25 row']")
            for announcement in announcements:
                title = announcement.query_selector("h6").text_content()
                date = announcement.query_selector("div[class='font-14 text-theme h6 m-t-10 f-w-bold']").text_content()
                description = announcement.query_selector("p").text_content()

                download_count, download_url, download_name = download_content(page, announcement, False)
                
                day , month , year = date.split(',')
                
                month = month[1:].split(' ')
                
                date_concat = months[month[0]] + '/' + month[1] + '/' + year[-2:]
                
                notices.append(
                    {
                        "title": title,
                        "date": date_concat,
                        "description": description,
                        "download_count": download_count,
                        "download_url": [','.join(''.join(url[5:]) for url in download_url)],
                        "download_name":[','.join(''.join(url) for url in download_name)]
                    }
                )
                
        browser.close()
        
        return notices

        
        
        
@shared_task
def ktu_webs_announce_task():
    try:
        ktu_result = "ktu_web_scrap"  
        web_scrap_result = ktu_web_scrap_announcement()
        
        # Store the result in the cache with a week-long timeout
        cache.set(ktu_result, json.dumps(web_scrap_result), timeout=60*60*24*7)
        
        return "KTU Web Scraping Task Completed"
    except Exception as e:
        return f"KTU Web Scraping Task Failed: {str(e)}"
    
class KTUWebScrapTask(APIView):
    def post(self, request):
        try:
            ktu_result = "ktu_web_scrap"  
            web_scrap_result = ktu_web_scrap_announcement()
            
            # Store the result in the cache with a week-long timeout
            cache.set(ktu_result, json.dumps(web_scrap_result), timeout=60*60*24*7)
            
            return Response("KTU Web Scraping Task Completed", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(f"KTU Web Scraping Task Failed: {str(e)}", status=status.HTTP_400_BAD_REQUEST)       
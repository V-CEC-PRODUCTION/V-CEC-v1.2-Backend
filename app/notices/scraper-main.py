from playwright.sync_api import sync_playwright
import pandas as pd
import os

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

def main():
    with sync_playwright() as pw:
        browser = pw.firefox.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(BASE_URL, wait_until='load', timeout=100000)

        df = pd.DataFrame(columns=COLUMNS)

        if os.path.exists(CSV_FILE):
            print("Existing CSV found, comparing data...")
            try:
                existing_df = pd.read_csv(CSV_FILE)
                first_row = existing_df.iloc[0]
                first_row_dict = {'title': first_row['title'], 'date': first_row['date'], 'description': first_row['description']}
            except pd.errors.EmptyDataError:
                print("Existing CSV is empty, creating a new one...")
                first_row = None 
                first_row_dict = None
        else:
            existing_df = pd.DataFrame()
            print("Creating a new CSV...")
            first_row = None
            first_row_dict = None

        end_scraping_flag = False

        page_count = 0
        while True:
            page_count += 1
            print(f'Page {page_count}')
            page.wait_for_timeout(1000)
            page.wait_for_selector("div[class='p-t-15 p-b-15 shadow row  m-b-25 row']", timeout=100000)
            announcements = page.query_selector_all("div[class='p-t-15 p-b-15 shadow row  m-b-25 row']")
            for announcement in announcements:
                title = announcement.query_selector("h6").text_content()
                date = announcement.query_selector("div[class='font-14 text-theme h6 m-t-10 f-w-bold']").text_content()
                description = announcement.query_selector("p").text_content()

                if first_row is not None:
                    if first_row_dict == {'title': title, 'date': date, 'description': description}:
                        end_scraping_flag = True
                        exit()

                download_count, download_url, download_name = download_content(page, announcement, False)

                df = pd.concat([
                    df,
                    pd.DataFrame(
                        {
                            "title": [title],
                            "date": [date],
                            "description": [description],
                            "download_count": [download_count],
                            "download_url": [','.join(download_url)],
                            "download_name": [','.join(download_name)]
                        }
                    )
                    ],ignore_index=True
                )
            
            if end_scraping_flag:
                    break
            
            try:
                    page.click("li.next")
            except:
                break
        
        if not existing_df.empty :
            df = pd.concat([df, existing_df], ignore_index=True)
            print("Appending new data to the beginning...")
        df.to_csv(CSV_FILE, index=False)

        browser.close()

if __name__ == '__main__':
    main()
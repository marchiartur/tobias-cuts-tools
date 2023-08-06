from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from smart_open import open
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


def wait_for_div_to_load(driver, div_id, timeout=10):
    try:
        # Wait for the div to be present on the page
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, div_id))
        )
        print(f"Div with ID '{div_id}' loaded successfully.")
    except Exception as e:
        print(f"Error: {e}")


def get_video_src_from_html(html: BeautifulSoup):
    # Find the video tag and get the src attribute value
    video_tag = html.find('video')

    if video_tag:
        video_src = video_tag['src']
        return video_src

    return None


def download_video_from_url(uri_in, uri_out, chunk_size=1 << 18):  # 256kB chunks
    """Write from uri_in to uri_out with minimal memory footprint."""
    with open(uri_in, "rb") as fin, open(uri_out, "wb") as fout:
        while chunk := fin.read(chunk_size):
            fout.write(chunk)


def extract_hrefs_from_url(url):
    options = Options()
    options.headless = True

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    time.sleep(2)

    click_button_language(driver)
    click_div_by_text(driver=driver, text_to_find='Português')

    driver.implicitly_wait(20)

    page_source = driver.page_source
    driver.quit()

    hrefs = []
    soup = BeautifulSoup(page_source, 'html.parser')

    html_content = str(soup)

    # Write the HTML content to a file
    filename = 'output.html'

    with open(filename, 'w', encoding='utf-8') as file:
        try:
            file.write(html_content)
            print('wrote html')
        except:
            print('error to write')

    a_tags = soup.find_all('a', {'data-a-target': 'preview-card-image-link'})

    for a_tag in a_tags:
        href = a_tag.get('href')
        if href:
            hrefs.append('https://www.twitch.tv' + href)

    return hrefs


def click_button_language(driver: webdriver.Chrome):
    button_class = 'ScCoreButton-sc-ocjdkq-0.ibtYyW.ScCoreButton-sc-1jjluui-0.ifIPdU.tw-select-button'

    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, button_class))
        )
        button.click()
        print("Button clicked successfully.")
    except Exception as e:
        print(f"Error: {e}")


def click_div_by_text(driver: webdriver.Chrome, text_to_find):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//div[contains(text(), '{text_to_find}')]"))
        )
        element.click()
        print(f"Clicked '{text_to_find}' div successfully.")
        time.sleep(5)
    except Exception as e:
        print(f"Error: {e}")


def get_html_clip(url: str, index: int) -> BeautifulSoup:
    options = Options()
    options.headless = True

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    wait_for_div_to_load(driver, 'CoreText-sc-1txzju1-0 kmassd')

    # Get the page source after waiting for the content to load
    page_source = driver.page_source

    filename = 'videos/clip' + str(index) + '.html'

    with open(filename, 'w', encoding='utf-8') as file:
        try:
            file.write(page_source)
            print('wrote html clip')
        except:
            print('error to write')

    driver.quit()

    # Parse the page source using BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    return soup


def get_title_from_html(html: BeautifulSoup):
    title = html.find('h2', {'data-a-target': 'stream-title'})

    if title is None:
        return ''

    return title.get('title')


def append_file_properties_to_json(id: int, title: str):
    filename = 'videos/data.json'

    with open(filename, 'r') as file:
        existing_data = json.load(file)['videos']
        existing_data.append({"id": id, "title": title})

    # Write the data to the JSON file
    with open(filename, 'w') as file:
        json.dump({"videos": existing_data}, file)


def run_local():
    with open('clip.html') as f:
        html = BeautifulSoup(f, 'html.parser')
        title = get_title_from_html(html)

        print(title)


def run_production():
    url_filter = 'https://www.twitch.tv/directory/game/Counter-Strike%3A%20Global%20Offensive/clips?range=24hr'
    first_six_hrefs = extract_hrefs_from_url(url_filter)[:6]

    with open('videos/data.json', 'w') as file:
        json.dump({'videos': []}, file)

    i = 0
    for url in first_six_hrefs:
        html_clip = get_html_clip(url, i)
        src = get_video_src_from_html(html_clip)
        clip_title = get_title_from_html(html_clip)

        append_file_properties_to_json(i, clip_title)

        filename = 'videos/' + str(i) + '.mp4'

        download_video_from_url(uri_in=src, uri_out=filename)
        i += 1


def main():
    run_production()


if __name__ == "__main__":
    main()

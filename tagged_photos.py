import json
import re
import time

from datetime import datetime, timezone
from subprocess import call

from helpers import scroll_to_bottom, get_driver, FB_USER_ID

# you will likely need to update this to something that selects
# for the container around the photo info, timestamp, album, etc
CONTAINER_SELECTOR = "._403j"


def get_fb_id(link):
    match = re.search("fbid=([0-9]+)", link)
    if match:
        return match.group(1)

    return "fake_id_" + str(hash(link))


if __name__ == '__main__':
    print("-"*20 + "\nOpening Browser...")

    driver = get_driver()
    driver.get("https://m.facebook.com/{}/photos".format(FB_USER_ID))
    scroll_to_bottom(driver)
    print("scrolled to bottom")

    photo_links = list(map(
        lambda el: el.get_attribute("href"),
        driver.find_elements_by_css_selector('.timeline.photos a')
    ))

    pretty = dict(sort_keys=True, indent=4, separators=(',', ': '))

    photos = []
    for link in photo_links:
        driver.get(link)

        photo_id = get_fb_id(link)
        full_size_url = driver.find_element_by_link_text(
            "View Full Size").get_attribute("href")
        actor = driver.find_element_by_css_selector('.actor').text
        people = list(map(
            lambda el: el.text,
            driver.find_elements_by_css_selector('.tagName')
        ))
        caption = driver.find_element_by_css_selector('.msg > div').text
        timestamp_json = driver.find_element_by_css_selector(
            '{} abbr'.format(CONTAINER_SELECTOR)).get_attribute('data-store')
        timestamp = json.loads(timestamp_json).get("time")
        info = driver.find_element_by_css_selector('{} > div'.format(
            CONTAINER_SELECTOR)).text.replace('\u00b7', '-').rstrip(' -')
        date = datetime.fromtimestamp(
            timestamp, timezone.utc).strftime("%Y-%m-%d")
        filename = "{}_{}.jpg".format(date, photo_id)

        driver.get(full_size_url)
        photo = {
            "fb_url": link,
            "cdn_url": driver.current_url,
            "actor": actor,
            "caption": caption,
            "timestamp": timestamp,
            "info": info,
            "filename": filename,
            "people": people
        }
        print(json.dumps(photo, **pretty))
        photos.append(photo)

        with open('photos/data.json', 'w') as f:
            f.write(
                json.dumps(photos, **pretty)
            )

        call(["curl", driver.current_url, "--output", "photos/{}".format(filename)])

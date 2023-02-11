import re

from subprocess import call

from helpers import scroll_to_bottom, get_driver, FB_USER_ID

if __name__ == '__main__':
    print("-"*20 + "\nOpening Browser...")

    driver = get_driver()
    driver.get("https://www.facebook.com/{}/videos".format(FB_USER_ID))
    scroll_to_bottom(driver)

    video_links = list(map(
        lambda el: el.get_attribute("href").replace('www.', 'm.'),
        driver.find_elements_by_css_selector('ul.fbStarGrid > li > a')
    ))

    for link in video_links:
        driver.get(link)

        page_source = driver.page_source

        driver.find_element_by_css_selector('[data-sigil="m-video-play-button playInlineVideo"]').click() # play video
        cdn_url = driver.find_element_by_css_selector('video').get_attribute('src')
        
        filename = cdn_url.split('?')[0].split('/')[-1]

        with open('videos/{}.html'.format(filename), 'w') as f:
            f.write(page_source)

        call(["curl", cdn_url, "--output", "videos/{}".format(filename)])
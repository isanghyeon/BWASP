from seleniumwire import webdriver
from urllib.parse import urlparse, urlunparse

import analyst
from feature import clickable_tags, packet_capture, res_geturl, get_ports, extract_cookies, extract_domains, csp_evaluator

check = True
input_url = ""
visited_links = []

def start(url, depth, options):
    driver = initSelenium()

    visit(driver, url, depth, options)

def visit(driver, url, depth, options):
    global check
    global input_url
    global visited_links

    driver.get(url)

    if check:
        input_url = driver.current_url
        visited_links.append(input_url)
        check = False

        # target_port = get_ports.getPortsOnline(input_url)

    req_res_packets = packet_capture.packetCapture(driver)
    cur_page_links = clickable_tags.bs4Crawling(driver.current_url, driver.page_source)
    cur_page_links += res_geturl.getUrl(driver.current_url, req_res_packets, driver.page_source)
    cur_page_links = list(set(deleteFragment(cur_page_links)))

    cookie_result = extract_cookies.getCookies(driver.current_url, req_res_packets)
    domain_result = extract_domains.extractDomains(dict(), driver.current_url, cur_page_links)

    csp_result = csp_evaluator.cspHeader(driver.current_url)
    analyst_result = analyst.start(input_url, req_res_packets, cur_page_links, driver)

    # Here DB code 

    if depth == 0:
        return

    for visit_url in cur_page_links:
        if visit_url in visited_links:
            continue
        if not isSameDomain(input_url, visit_url):
            continue
        if isSamePath(visit_url, visited_links):
            continue

        visited_links.append(visit_url)
        visit(driver, visit_url, depth-1)

def isSameDomain(target_url, visit_url):
    try:
        target = urlparse(target_url)
        visit = urlparse(visit_url)

        if visit.scheme != "http" and visit.scheme != "https":
            return False
        if target.netloc == visit.netloc:
            return True
        else:
            return False
    except:
        return False

def isSamePath(visit_url, previous_urls):
    try:
        visit = urlparse(visit_url)

        for link in previous_urls:
            previous = urlparse(link)

            if (visit.path == previous.path) and (visit.query == previous.query):
                return True
            
            # https://naver.com 과 https://naver.com/ 는 같은 url 이므로 검증하는 코드 작성.
            visit_path_len = len(visit.path.replace("/", ""))
            previous_path_len = len(previous.path.replace("/", ""))
            
            if visit_path_len == 0 and previous_path_len == 0:
                return True
        else:
            return False
    except:
        return False

def deleteFragment(links):
    for i in range(len(links)):
        parse = urlparse(links[i])
        parse = parse._replace(fragment="")
        links[i] = urlunparse(parse)

    return links

def initSelenium():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("lang=ko_KR")
    chrome_options.add_experimental_option("prefs", {
        "download_restrictions": 3
    })
    options = {
        "disable_encoding" : True
    }

    driver = webdriver.Chrome("./config/chromedriver.exe", seleniumwire_options = options, chrome_options=chrome_options)
    return driver

if __name__ == "__main__":
    url = "https://github.com/"
    start(url, 3, {})
from seleniumwire import webdriver
from multiprocessing import Process
from urllib.parse import urlparse, urlunparse

from Crawling import analyst
from Crawling.feature import clickable_tags, packet_capture, res_geturl, get_ports, extract_cookies, extract_domains, csp_evaluator, db

check = True
input_url = ""
visited_links = []


def start(url, depth, options):
    driver = initSelenium()

    visit(driver, url, depth, options)
    driver.quit()

def analysis(input_url, req_res_packets, cur_page_links, options, cookie_result, page_source, current_url):
    
    analyst_result = analyst.start(input_url, req_res_packets, cur_page_links, page_source, current_url ,options['info'])
    print(analyst_result)
    req_res_packets = deleteCssBody(req_res_packets)

    # previous_packet_count = db.getPacketsCount()
    # db.insertDomains(req_res_packets, cookie_result, previous_packet_count, current_url)
    # db.insertWebInfo(analyst_result, input_url, previous_packet_count)
    # Here DB code 
    return 1

def visit(driver, url, depth, options):
    global check
    global input_url
    global visited_links

    try:
        driver.get(url)
        alert = driver.switch_to_alert()
        alert.accept()
    except:
        pass

    if check:
        input_url = driver.current_url
        visited_links.append(input_url)
        check = False

        if "portScan" in options["tool"]["optionalJobs"]:
            target_port = get_ports.getPortsOnline(input_url)
            db.insertPorts(target_port, input_url)

    # TODO
    # 다른 사이트로 redirect 되었을 때, 추가적으로 same 도메인 인지를 검증하는 코드가 필요함.
    # 첫 패킷에 google 관련 패킷 지우기
    req_res_packets = packet_capture.packetCapture(driver)
    cur_page_links = clickable_tags.bs4Crawling(driver.current_url, driver.page_source)
    cur_page_links += res_geturl.getUrl(driver.current_url, req_res_packets, driver.page_source)
    cur_page_links = list(set(deleteFragment(cur_page_links)))

    cookie_result = extract_cookies.getCookies(driver.current_url, req_res_packets)
    domain_result = extract_domains.extractDomains(dict(), driver.current_url, cur_page_links)

    # if "CSPEvaluate" in options["tool"]["optionalJobs"]:
    #     csp_result = csp_evaluator.cspHeader(driver.current_url)
    #     db.insertCSP(csp_result)

    # TODO
    # 찾은 정보의 Icon 제공

    # db.insertPackets(req_res_packets)

    packet_capture.writeFile(req_res_packets)

    p = Process(target=analysis, args=(input_url, req_res_packets, cur_page_links, options, cookie_result, driver.page_source, driver.current_url)) # driver 전달 시 에러. (프로세스간 셀레니움 공유가 안되는듯 보임)
    p.start()


    if depth == 0:
        return

    for visit_url in cur_page_links:
        if visit_url in visited_links:
            continue
        if not isSameDomain(input_url, visit_url):
            continue
        if isSamePath(visit_url, visited_links):
            continue

        # TODO
        # 이미지 페이지 등 방문하지 않는 코드 작성
        # target 외에 다른 사이트로 redirect 될때, 검증하는 코드 작성 필요
        # 무한 크롤링
        visited_links.append(visit_url)
        visit(driver, visit_url, depth - 1, options)


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


def deleteCssBody(packets):
    css_content_types = ["text/css"]

    for index in range(len(packets)):
        if "content-type" in list(packets[index]["response"]["headers"].keys()):
            for type in css_content_types:
                if packets[index]["response"]["headers"]["content-type"].find(type) != -1:
                    packets[index]["response"]["body"] = ""

    return packets


def initSelenium():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("lang=ko_KR")
    chrome_options.add_experimental_option("prefs", {
        "download_restrictions": 3
    })
    options = {
        "disable_encoding": True
    }

    driver = webdriver.Chrome("./Crawling/config/chromedriver", seleniumwire_options=options, chrome_options=chrome_options)
    return driver


if __name__ == "__main__":
    options = {
        "tool": {
            "analysisLevel": "771",
            "optionalJobs": [
                "portScan",
                "CSPEvaluate"
            ]
        },
        "info": {
            "server": [
                {
                    "name": "apache",
                    "version": "22"
                },
                {
                    "name": "nginx",
                    "version": "44"
                }
            ],
            "framework": [
                {
                    "name": "react",
                    "version": "22"
                },
                {
                    "name": "angularjs",
                    "version": "44"
                }
            ],
            "backend": [
                {
                    "name": "flask",
                    "version": "22"
                },
                {
                    "name": "django",
                    "version": "44"
                }
            ]
        },
        "target": {
            "url": "https://github.com/",
            "path": [
                "/apply, /login", "/admin"
            ]
        }
    }

    start(options["target"]["url"], int(options["tool"]["analysisLevel"]), options["info"])

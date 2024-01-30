import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import whois  # Added for WHOIS lookup
import colorama

# init the colorama module
colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW
RED = colorama.Fore.RED

def logo(color=RESET):
    """
    Prints the logo

    Returns
    ---------
    str
        Return the logo string.
    """

    return f"""

   __  ______  __       ______     __                  __
  / / / / __ \/ /      / ____/  __/ /__________ ______/ /_____  _____
 / / / / /_/ / /      / __/ | |/_/ __/ ___/ __ `/ ___/ __/ __ \/ ___/
/ /_/ / _, _/ /___   / /____>  </ /_/ /  / /_/ / /__/ /_/ /_/ /
\____/_/ |_/_____/  /_____/_/|_|\__/_/   \__,_/\___/\__/\____/_/


                          {RED}Developed by Prashanth{RESET}
    {RESET}
    """

# initialize the set of links (unique links)
internal_urls = set()
external_urls = set()

def is_valid(url):
    """
    Checks whether url is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_website_links(url):
    """
    Returns all URLs that are found on url in which it belongs to the same
    website
    """
    # all URLs of url
    urls = set()
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue
        # join the URL if it's relative (not an absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not is_valid(href):
            # not a valid URL
            continue
        if href in internal_urls:
            # already in the set
            continue
        if domain_name not in href:
            # external link
            if href not in external_urls:
                print(f"{GRAY}[!] External link: {href}{RESET}")
                external_urls.add(href)
            continue
        print(f"{GREEN}[*] Internal link: {href}{RESET}")
        urls.add(href)
        internal_urls.add(href)
    return urls

# number of URLs visited so far will be stored here
total_urls_visited = 0

def crawl(url, max_urls=30):
    """
    Crawls a web page and extracts all links.
    You'll find all links in external_urls and internal_urls global set
    variables.
    params:
        max_urls (int): number of max urls to crawl, default is 30.
    """

    global total_urls_visited
    total_urls_visited += 1
    print(f"{YELLOW}[*] Crawling: {url}{RESET}")
    links = get_all_website_links(url)
    for link in links:
        if total_urls_visited > max_urls:
            break
        crawl(link, max_urls=max_urls)

def whois_lookup(domain):
    """
    Performs a WHOIS lookup for domain details.
    """
    try:
        details = whois.whois(domain)
        print(f"{GREEN}[*] WHOIS Lookup for {domain}:{RESET}")
        print(details)
    except Exception as e:
        print(f"{RED}[!] WHOIS lookup failed: {str(e)}{RESET}")

if __name__ == "__main__":

    print(logo())
    while True:
        print(f"{RED}Options:{RESET}")
        print("1. URL Extractor")
        print("2. WHOIS Lookup")
        print("3. Exit")

        option = input(f"{RED}[++] Choose an option (1/2/3):{RESET}")

        if option == '1':
            start_url = input(f"{RED}[++] Enter the URL to start crawling:{RESET}")
            crawl(start_url)
            print("[+] Total Internal links:", len(internal_urls))
            print("[+] Total External links:", len(external_urls))
            print("[+] Total URLs:", len(external_urls) + len(internal_urls))
            print("[+] Total crawled URLs:", len(internal_urls))
            break
        elif option == '2':
            domain_to_lookup = input(f"{RED}[++] Enter the domain for WHOIS lookup:{RESET}")
            whois_lookup(domain_to_lookup)
            break
        elif option == '3':
            print(f"{YELLOW}[!] Exiting...{RESET}")
            break
        else:
            print(f"{RED}[!] Invalid option. Please choose a valid option.{RESET}")

import urllib.parse
from tqdm import tqdm
from playwright.sync_api import sync_playwright
from tenacity import retry, stop_after_attempt, retry_if_exception_type

MAX_RETRY = 5


class Column:
    BASE_URL = 'https://news.netkeiba.com/?pid=column_view'

    def __init__(self, cid: int, content: str = None):
        self.cid = cid
        self.content = content

    @retry(stop=stop_after_attempt(MAX_RETRY),
           retry=retry_if_exception_type(TimeoutError))
    def fetch_content(self, timeout=3000):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()

            page.goto(f"{self.BASE_URL}&cid={self.cid}", timeout=timeout,
                      wait_until="domcontentloaded")

            self.content = page.locator("div.ColumnArticle_Body").inner_text()

            context.close()
            browser.close()


class ColumnList:
    BASE_URL = "https://news.netkeiba.com/?pid=column_search"

    def __init__(self, keyword: str):
        keyword_encoded = urllib.parse.quote(keyword, encoding="euc-jp")
        self.url = f"{self.BASE_URL}&keyword={keyword_encoded}"

    def get_all(self, fetch_content: bool = True, timeout: int = 15000) -> list[Column]:
        print(f"URL: {self.url}")
        total_pages = self.__get_total_pages(timeout=timeout)
        print("Total pages:", total_pages)

        cid_list = []
        for page_no in range(1, total_pages + 1):
            cid_list += self.__get_column_list(page_no, timeout=timeout)
        print("Total columns:", len(cid_list))

        columns = []
        for cid in tqdm(cid_list, desc="Fetching columns.."):
            column = Column(cid)
            if fetch_content:
                column.fetch_content(timeout=timeout)
                # print("Fetched:", cid)

            columns.append(column)
        return columns

    @retry(stop=stop_after_attempt(MAX_RETRY),
           retry=retry_if_exception_type(TimeoutError))
    def __get_column_list(self, page_no: int = 1,
                          timeout: int = 15000) -> list[int]:
        column_ids = []

        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            page.route("**/*", lambda route: route.abort()
                       if route.request.resource_type == "image"
                       else route.continue_()
                       )

            url = f"{self.url}&page={page_no}"
            page.goto(url, timeout=timeout)
            links = page.locator("div.ColumnList > a")
            for i in range(links.count()):
                column_url = links.nth(i).get_attribute("href")
                qs = urllib.parse.urlparse(column_url).query
                cid = int(urllib.parse.parse_qs(qs)["cid"][0])
                column_ids.append(cid)

            context.close()
            browser.close()

        print(f"Page {page_no}: {len(column_ids)} columns found")
        return column_ids

    def __get_total_pages(self, timeout: int = 15000) -> int:
        last_page_num = -1
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()

            page.goto(self.url, timeout=timeout)

            links = page.locator("div.CommonPager > ul.PagerMain > li > a")
            for i in range(links.count()):
                if links.nth(i).get_attribute("title") == "最後":
                    last_page_num = int(links.nth(i).text_content())
                    break

            context.close()
            browser.close()

        return last_page_num

import asyncio
import itertools
import urllib.parse
from tqdm import tqdm
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from playwright._impl._errors import TimeoutError
from tenacity import retry, stop_after_attempt, retry_if_exception_type

MAX_RETRY = 5
REQUESTS_PER_TIME = 5


class Column:
    BASE_URL = 'https://news.netkeiba.com/?pid=column_view'

    def __init__(self, cid: int, content: str = None):
        self.cid = cid
        self.content = content

    @retry(stop=stop_after_attempt(MAX_RETRY),
           retry=retry_if_exception_type(TimeoutError))
    async def fetch_content(self, timeout=3000):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(f"{self.BASE_URL}&cid={self.cid}", timeout=timeout,
                            wait_until="domcontentloaded")

            self.content = await page.locator("div.ColumnArticle_Body").inner_text()

            await context.close()
            await browser.close()


class ColumnList:
    BASE_URL = "https://news.netkeiba.com/?pid=column_search"

    def __init__(self, keyword: str):
        keyword_encoded = urllib.parse.quote(keyword, encoding="euc-jp")
        self.url = f"{self.BASE_URL}&keyword={keyword_encoded}"

    def get_all(self, timeout: int = 15000, n_requests_per_time: int = REQUESTS_PER_TIME) -> list[Column]:
        print(f"URL: {self.url}")
        total_pages = self.__get_total_pages(timeout=timeout)
        print("Total pages:", total_pages)

        page_list = list(range(1, total_pages + 1))
        cid_list = []
        for pages in self.chunks(page_list, n_requests_per_time):
            cid_list += asyncio.run(self.__get_cid_list(pages, timeout=timeout))
        print("Total columns:", len(cid_list))

        columns = [Column(cid) for cid in cid_list]
        pbar = tqdm(total=len(columns))
        for cols in self.chunks(columns, n_requests_per_time):
            asyncio.run(self.__get_contents(cols, timeout=timeout))
            pbar.update(len(cols))
        pbar.close()

        return columns

    def chunks(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    async def __get_cid_list(self, pages: list[int], timeout: int = 15000) -> list[int]:
        tasks = []
        for page_no in pages:
            tasks.append(self.__get_column_list(page_no, timeout=timeout))

        results = await asyncio.gather(*tasks)
        cid_list = list(itertools.chain.from_iterable(results))
        return cid_list

    async def __get_contents(self, columns: list[Column], timeout: int = 15000):
        tasks = []
        for column in columns:
            tasks.append(column.fetch_content(timeout=timeout))
        await asyncio.gather(*tasks)

    @retry(stop=stop_after_attempt(MAX_RETRY),
           retry=retry_if_exception_type(TimeoutError))
    async def __get_column_list(self, page_no: int = 1,
                                timeout: int = 15000) -> list[int]:
        column_ids = []

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()
            await page.route("**/*", lambda route: route.abort()
                             if route.request.resource_type == "image"
                             else route.continue_()
                             )

            url = f"{self.url}&page={page_no}"
            await page.goto(url, timeout=timeout)
            links = page.locator("div.ColumnList > a")
            link_count = await links.count()
            for i in range(link_count):
                column_url = await links.nth(i).get_attribute("href")
                qs = urllib.parse.urlparse(column_url).query
                cid = int(urllib.parse.parse_qs(qs)["cid"][0])
                column_ids.append(cid)

            await context.close()
            await browser.close()

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

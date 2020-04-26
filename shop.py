import time
from multiprocessing.dummy import Pool

import requests
from bs4 import BeautifulSoup
from user_agent import generate_user_agent


class Shop:
    def __init__(self, name, encoding="utf-8"):
        self.name = name
        self.encoding = encoding

    @staticmethod
    def _cleanData(data):
        try:
            return str(data.text).strip().replace("'", "")
        except AttributeError:
            return "None"

    def _getContentFromSite(self, link):
        r = requests.get(link)
        r.headers = {"User-agent:", generate_user_agent()}
        content = str(r.content, self.encoding, errors="replace")
        soup = BeautifulSoup(content, 'html.parser')
        return soup

    @staticmethod
    def _getISBNNumber(link):
        pass

    @staticmethod
    def _getInfoFromBook(book):
        pass

    @staticmethod
    def _getLinks():
        pass

    def _getBooksFromLink(self, link):
        pass

    # def _getBooksFromLink(self, link, tag, tag_name):
    #     print(link)
    #     soup = self._getContentFromSite(link)
    #     books = soup.find_all(tag, class_=tag_name)
    #     books = [str(book) for book in books]
    #     pool = Pool(processes=20)
    #     pool.map(self._getInfoFromBook, books)
    #     pool.close()
    #     pool.join()

    def start(self, links, processes):
        start_time = time.time()
        pool = Pool(processes=processes)
        pool.map(self._getBooksFromLink, links)
        pool.close()
        pool.join()
        execution_time = time.time() - start_time
        print("#############", str(execution_time // 60).split(".")[0], "m", str(execution_time % 60).split(".")[0],
              "s")

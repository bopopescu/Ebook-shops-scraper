import re
from multiprocessing.dummy import Pool

from bs4 import BeautifulSoup

from database import Database
from shop import Shop


class Virtualo(Shop):
    def __init__(self, name, encoding):
        super().__init__(name, encoding)

    @staticmethod
    def _cleanPrice(price):  # if book has two prices we will pick second one
        prices = re.findall(r"\d+.\d+", price)
        return prices[1] if len(prices) > 1 else prices[0]

    def _getISBNNumber(self, link):
        soup = self._getContentFromSite(link)
        try:
            return int(str(soup.find(attrs={"itemprop": "isbn"}).text).replace("-", ""))
        except AttributeError:
            return 1000000000000

    def _getInfoFromBook(self, book):
        db = Database(self.name)
        book = BeautifulSoup(book, "html.parser")
        title = self._cleanData(book.find("h3", class_="title"))
        authors = self._cleanData(book.find("div", class_="authors"))
        price = self._cleanPrice(book.find("div", class_="price").text)
        link = book.find("a")['href']

        ISBN_number = db.check_book(title, authors)
        ISBN_number = self._getISBNNumber(link) if not ISBN_number else 1000000000000

        print(title, authors, price, link, ISBN_number)
        db.save_book(title=title, authors=authors, link=link, price=price, ISBN=ISBN_number)

    def _getBooksFromLink(self, link):
        print(link)
        soup = self._getContentFromSite(link)
        books = soup.find_all("li", class_="product")
        books = [str(book) for book in books]
        pool = Pool(processes=10)
        pool.map(self._getInfoFromBook, books)
        pool.close()
        pool.join()

    def _getLinks(self):
        soup = self._getContentFromSite("https://virtualo.pl/ebooki/?sort_Id=4&format=6&page=1")
        return int((soup.find("ul", class_="pagination")).find_all("li")[3].text)


s = Virtualo("Virtualo", "utf-8")
links = [f"https://virtualo.pl/ebooki/?sort_Id=4&format=6&page={i + 1}" for i in range(s._getLinks())]
s.start(links, 8)

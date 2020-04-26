import re
from multiprocessing.dummy import Pool

from bs4 import BeautifulSoup

from database import Database
from shop import Shop


def _cleanPrice(price):  # if book has two prices script will pick second one
    prices = str(re.findall(r"\d+.\d+", price)[0]).replace(",", ".")
    return prices


class Publio(Shop):
    def __init__(self, name, encoding):
        super().__init__(name, encoding)

    @staticmethod
    def _cleanLink(link):
        return "https://publio.pl" + link

    def _getISBNNumber(self, link):
        soup = self._getContentFromSite(link)
        ISBN = [str(item).replace("-","") for item in re.findall(r"\d+-\d+-\d+-\d+-\d+", str(soup.text).replace(","," "))]
        return ISBN[0] if len(ISBN) != 0 else 1000000000000


    def _getInfoFromBook(self, book):
        db = Database(self.name)
        book = BeautifulSoup(book, "html.parser")
        title = self._cleanData(book.find("span", class_="product-tile-title-long"))
        price = _cleanPrice(book.find("ins", class_="product-tile-price").text)
        authors = self._cleanData(book.find("span", class_="product-tile-author"))

        link = self._cleanLink(book.find("a", class_="product-tile-cover")['href'])

        ISBN_number = db.check_book(title, authors)
        ISBN_number = self._getISBNNumber(link) if not ISBN_number else 1000000000000

        print(title, authors, price, link, ISBN_number)
        db.save_book(title=title, authors=authors, link=link, price=price, ISBN=ISBN_number)

    def getLinks(self):
        soup = self._getContentFromSite("http://www.publio.pl/e-booki,strona1.html")
        return int(str((soup.find_all("a", class_="page"))[4].text).replace(u"\xa0", ""))

    def _getBooksFromLink(self, link):
        print(link)
        soup = self._getContentFromSite(link)
        books = soup.find_all("div", class_="product-tile")
        books = [str(book) for book in books]
        pool = Pool(processes=20)
        pool.map(self._getInfoFromBook, books)
        pool.close()
        pool.join()


s = Publio("Publio", "utf-8")
links = [f"http://www.publio.pl/e-booki,strona{i + 1}.html" for i in range(s.getLinks())]
s.start(links, 8)

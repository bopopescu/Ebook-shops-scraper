import re
from multiprocessing.dummy import Pool

from bs4 import BeautifulSoup

from database import Database
from shop import Shop


class Ebookpoint(Shop):
    def __init__(self, name, encoding):
        super().__init__(name, encoding)

    @staticmethod
    def _cleanPrice(price):  # if book has two prices script will pick second one
        prices = re.findall(r"\d+.\d+", price)
        return prices[1] if len(prices) > 1 else prices[0]

    def _getISBNNumber(self, link):
        soup = self._getContentFromSite(link)
        try:
            return int(str(soup.find(attrs={"property": "book:isbn"})['content']))
        except (AttributeError, ValueError, TypeError):
            return False

    def _getInfoFromBook(self, book):
        db = Database(self.name)
        book = BeautifulSoup(book, "html.parser")
        title = self._cleanData(book.find(attrs={"itemprop": "name"}))
        authors = self._cleanData(book.find("p", class_="author"))
        price = self._cleanPrice(book.find(attrs={"itemprop": "price"}).text)
        link = self._cleanLink(book.find("a")['href'])

        ISBN_number = db.check_book(title, authors)
        ISBN_number = self._getISBNNumber(link) if not ISBN_number else 1000000000000

        print(title, authors, price, link, ISBN_number)
        db.save_book(title=title, authors=authors, link=link, price=price, ISBN=ISBN_number)

    def getLinks(self):
        soup = self._getContentFromSite("https://ebookpoint.pl/kategorie/ebooki")
        return int((soup.find_all("a", class_="pozycjaStronicowania"))[2].text)

    @staticmethod
    def _cleanLink(link):
        return str(link).replace("//", "https://")

    def _getBooksFromLink(self, link):
        print(link)
        soup = self._getContentFromSite(link)
        books = soup.find_all("li", class_="classPresale")
        books = [str(book) for book in books]
        pool = Pool(processes=20)
        pool.map(self._getInfoFromBook, books)
        pool.close()
        pool.join()


s = Ebookpoint("Ebookpoint", "iso-8859-2")
links = [f"https://ebookpoint.pl/kategorie/ebooki/{i + 1}" for i in range(s.getLinks())]
s.start(links, 4)

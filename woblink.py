import time
from multiprocessing.dummy import Pool

from bs4 import BeautifulSoup

from database import Database
from shop import Shop


class Woblink(Shop):
    def __init__(self, name, encoding):
        super().__init__(name, encoding)

    def _cleanPrice(self, price):  # if book has two prices script will pick second one
        return price.replace(",", ".").split()[0]

    def _getISBNNumber(self, link):
        soup = self._getContentFromSite(link)
        try:
            return int(str(soup.find(attrs={"property": "product:retailer_item_id"})['content']).split(":")[1])
        except (AttributeError, ValueError):
            return False

    def _getLinks(self):
        soup = self._getContentFromSite("https://woblink.com/katalog/ebooki")
        return int((soup.find_all("a", class_="vpagination__pagebutton"))[3].text)

    @staticmethod
    def _cleanLink(link):
        return str(link).replace("//", "https://")

    def _getBooksFromLink(self, link):
        print(link)
        soup = self._getContentFromSite(link)
        books = soup.find_all("div", class_="catalog-tile")
        books = [str(book) for book in books]
        pool = Pool(processes=20)
        pool.map(self._getInfoFromBook, books)
        pool.close()
        pool.join()

    def _getInfoFromBook(self, book):
        db = Database(self.name)
        book = BeautifulSoup(book, "html.parser")
        title = self._cleanData(book.find(attrs={"class": "catalog-tile__title"}))
        authors = self._cleanData(book.find_all("p")[2])
        price = self._cleanPrice(book.find(attrs={"class": "catalog-tile__new-price"}).text)
        link = (book.find(attrs={"class": "catalog-tile__title"}))['href']

        ISBN_number = db.check_book(title, authors)
        ISBN_number = self._getISBNNumber(link) if not ISBN_number else 1000000000000
        print(title, authors, price, link, ISBN_number)
        db.save_book(title=title, authors=authors, link=link, price=price, ISBN=ISBN_number)


s = Woblink("Woblink", "utf-8")
links = [f"https://woblink.com/katalog/ebooki?strona={i + 1}" for i in range(s._getLinks())]
s.start(links, 6)

import mysql.connector


class Database():
    def __init__(self, shop_name):
        self.con = mysql.connector.connect(user='scraper', password='lalala',
                                           host='192.168.1.7',
                                           database='books')
        self.cursor = self.con.cursor(buffered=True)

        self.cursor.execute(f"SELECT id_shops from shops where name = '{shop_name}'")
        self.id_shop = self.cursor.fetchone()[0]

    def clean_data(self, value):
        return str(value).replace("'","").strip()

    def save_book(self, title, price, link, authors, ISBN):
        id_title = self._add_title(self.clean_data(title))
        for author in authors.split(","):
            id_author = self._add_authors(self.clean_data(author))
            self._authors_titles(id_title, id_author)
        self.cursor.execute(f"select id_titles from prices where id_titles={id_title} and id_shops={self.id_shop}")
        if self.cursor.rowcount == 0:
            self.cursor.execute(
                f"INSERT INTO prices (id_titles, id_shops, price, link,add_time) VALUES ({id_title}, {self.id_shop}, {price}, '{link}',current_timestamp)")
        else:
            self.cursor.execute(
                f"UPDATE prices SET price={price}, link='{link}', add_time=current_timestamp WHERE id_titles = {id_title} and id_shops = {self.id_shop} ")
        self._ISBN_titles(ISBN, id_title)

        self.con.commit()
    def check_book(self, title, authors):
        id_title = self._add_title(self.clean_data(title))
        author = self.clean_data(authors.split(',')[0])
        check = f"SELECT ISBN_titles.ISBN from ISBN_titles inner join titles t on ISBN_titles.id_titles = t.id_titles inner join authors_titles a on t.id_titles = a.id_titles inner join authors a2 on a.id_authors = a2.id_authors where ISBN_titles.id_titles = 1 and a2.name = '{author}'"
        self.cursor.execute(check)

        return False if self.cursor.rowcount == 0 else self.cursor.fetchone()[0]
    def _add_title(self, title):
        check = f"select id_titles from titles where title='{title}'"
        self.cursor.execute(check)
        if self.cursor.rowcount != 0:
            return self.cursor.fetchone()[0]
        else:
            self.cursor.execute(f"INSERT INTO titles (title) values ('{title}')")
            return self.cursor.lastrowid

    def _authors_titles(self, id_title, id_author):
        self.cursor.execute(f"SELECT id_authors FROM authors_titles WHERE id_authors = {id_author} and id_titles = {id_title}")
        if self.cursor.rowcount != 0:
            return self.cursor.fetchone()[0]
        else:
            self.cursor.execute(f"INSERT INTO authors_titles (id_titles, id_authors) values ({id_title},{id_author})")
            return self.cursor.lastrowid

    def _add_authors(self, author):
        author = author.strip()
        self.cursor.execute(f"SELECT id_authors FROM authors WHERE name = '{author}'")
        if self.cursor.rowcount != 0:
            return self.cursor.fetchone()[0]
        else:
            self.cursor.execute(f"INSERT INTO authors (name) values ('{author}')")
            return self.cursor.lastrowid

    def _ISBN_titles(self,ISBN, id_title):
        ISBN = int(ISBN)
        self.cursor.execute(f"SELECT id_titles FROM ISBN_titles WHERE ISBN = {ISBN} and id_titles = {id_title}")
        self.cursor.execute(f"INSERT INTO ISBN_titles (ISBN,id_titles) values ({ISBN},{id_title})") if self.cursor.rowcount == 0 else None

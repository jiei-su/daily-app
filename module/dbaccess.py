"""
SQLモジュール
"""
import sqlite3
import os

# テーブル定義
DATABASES = {
    "weather": [
        ("pkey", "integer", "PRIMARY KEY AUTOINCREMENT"),
        ("place", "text", "NOT NULL"),
        ("url", "text", "NOT NULL"),
    ],
    "train": [
        ("pkey", "integer", "PRIMARY KEY AUTOINCREMENT"),
        ("route", "text", "NOT NULL"),
        ("url", "text", "NOT NULL"),
    ],
    "english_study": [
        ("pkey", "integer", "PRIMARY KEY AUTOINCREMENT"),
        ("english", "text", "NOT NULL"),
        ("japanese", "text", "NOT NULL"),
    ],
}


class Base:
    """
    基底クラス.
    """
    
    def __init__(self, table: str):
        """
        データベース接続.

        param:
            table テーブル名
        """

        db_path = os.path.join(os.getcwd(), table + ".db")
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = self.dict_factory
        self.cur = self.conn.cursor()
    
    def dict_factory(self, cursor: object, row: dict) -> dict:
        """
        検索結果をdict形式に変換する.

        param:
            row 行

        return:
            d {カラム: 値}
        """

        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]

        return d

    def select_all(self) -> list:
        """
        全件取得する.

        return:
            fetchall 全件
        """

        sql = "SELECT * FROM %s" % self.table
        if self.cur.execute(sql) is False:
            return False

        return self.cur.fetchall()
    
    def commit(self) -> bool:
        """
        コミットする.

        return:
            True
        """

        if self.conn.commit() is False:
            return False
        self.conn.close()

        return True


class CreateTable:
    """
    テーブル生成クラス.
    """

    def __init__(self):
        for table in DATABASES:
            db_path = os.path.join(os.getcwd(), table + ".db")
            self.conn = sqlite3.connect(db_path)
            self.cur = self.conn.cursor()
            self.create(table)
        self.conn.commit()
        self.conn.close()

    def create(self, table: str) -> bool:
        """
        テーブルを生成する.

        param:
            table テーブル名

        return:
            True
        """

        sql = "CREATE TABLE IF NOT EXISTS %s (" % table
        for column in DATABASES[table]:
            sql += "%s %s %s, " % (column[0], column[1], column[2])
        sql = sql.rstrip(", ") + ")"
        if self.cur.execute(sql) is False:
            return False

        return True


class Weather(Base):
    """
    天気予報クラス.
    """

    def __init__(self):
        self.table = 'weather'
        super().__init__(self.table)
    
    def insert(self, place: str, url: str) -> bool:
        """
        insertする.

        param:
            place 場所
            url 収集url

        return:
            True
        """

        sql = "INSERT INTO %s (place, url) " % self.table
        sql += "VALUES (?, ?)"
        data = (place, url)
        if self.cur.execute(sql, data) is False:
            return False

        return True
 
    def delete_by_route(self, place: str) -> bool:
        """
        deleteする.

        param:
            place 場所

        return:
            True
        """

        sql = "DELETE FROM %s " % self.table
        sql += "WHERE place = ?"
        data = (place,)
        if self.cur.execute(sql, data) is False:
            return False

        return True


class Train(Base):
    """
    運行情報クラス.
    """

    def __init__(self):
        self.table = 'train'
        super().__init__(self.table)

    def insert(self, route: str, url: str) -> bool:
        """
        insertする.

        param:
            route 路線
            url 収集url

        return:
            True
        """

        sql = "INSERT INTO %s (route, url) " % self.table
        sql += "VALUES (?, ?)"
        data = (route, url)
        if self.cur.execute(sql, data) is False:
            return False

        return True

    def delete_by_route(self, route: str) -> bool:
        """
        deleteする.

        param:
            route 路線

        return:
            True
        """

        sql = "DELETE FROM %s " % self.table
        sql += "WHERE route = ?"
        data = (route,)
        if self.cur.execute(sql, data) is False:
            return False

        return True


class EnglishStudy(Base):
    """
    英単語クラス.
    """

    def __init__(self):
        self.table = 'english_study'
        super().__init__(self.table)

    def insert(self, english_word: str, japanese_word: str) -> bool:
        """
        insertする.

        param:
            english_word 英単語
            japanese_word 日本語

        return:
            True
        """

        sql = "INSERT INTO %s (english, japanese) " % self.table
        sql += "VALUES (?, ?)"
        data = (english_word, japanese_word)
        if self.cur.execute(sql, data) is False:
            return False

        return True

    def select_random_english(self) -> list:
        """
        ランダムに抽出する.

        return:
            fetchall 英単語と日本語(3件ずつ)
        """

        sql = "SELECT * FROM %s " % self.table
        sql += "ORDER BY RANDOM() LIMIT 3"
        if self.cur.execute(sql) is False:
            return False

        return self.cur.fetchall()

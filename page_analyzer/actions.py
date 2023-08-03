from datetime import date
import page_analyzer.db_functions as db
from page_analyzer.url_checker import get_seo_params


def is_exist(where_name: str, table: str = 'urls') -> bool:
    """Predicate func checks if id exists"""
    return bool(db.select(table_name=table,
                          fields=['id'],
                          where='name',
                          param=where_name))


def get_id(where_name: str, table: str = 'urls') -> int:
    """Returns id by name"""
    return db.extract_one(
        db.select(table_name=table,
                  fields=['id'],
                  where='name',
                  param=where_name)
    )


def add_url(url: str) -> None:
    """Add new url in table URLS in DB"""
    db.insert(table_name='urls',
              fields=['name', 'created_at'],
              values=[url, date.today()])


def get_site(i_d: int) -> dict:
    """Returns site data from DB by id"""
    site_data = db.select(table_name='urls',
                          take_all=True,
                          where='id',
                          param=i_d)

    return db.change_structure(site_data, keys=["id", "name", "created_at"])[0]


def get_check(i_d: int) -> list[dict]:
    """Returns check data from DB by id"""
    check_data = db.select(table_name='url_checks',
                           take_all=True,
                           where='url_id',
                           param=i_d,
                           sort_by='id')

    return db.change_structure(check_data,
                               keys=["id", "url_id", "status_code",
                                     "h1", "title", "description",
                                     "created_at"]
                               )


def get_websites() -> list[dict]:
    """Returns table websites"""
    data = db.select_table_websites()

    return db.change_structure(
        data, keys=["id", "name", "created_at", "status_code"]
    )


def get_url(i_d: int) -> str:
    """Returns url by id"""
    url = db.select(table_name='urls',
                    fields=["name"],
                    where='id',
                    param=int(i_d))

    return db.extract_one(url)


def add_check(i_d: int, code: int, url: str) -> None:
    """Add new check for url"""
    seo_params = get_seo_params(url)
    db.insert(table_name='url_checks',
              fields=['url_id', 'created_at',
                      'status_code', 'h1',
                      'title', 'description'],
              values=[int(i_d), date.today(), code, seo_params["h1"],
                      seo_params["title"], seo_params["description"]])

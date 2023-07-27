import os
from datetime import date
from dotenv import load_dotenv
from page_analyzer import db_actions as db
from page_analyzer.validator import validate
from page_analyzer.parser import parse, get_status_code
from flask import (
    Flask,
    render_template,
    request,
    flash,
    url_for,
    redirect)


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route("/")
def view_home_page():
    return render_template('home_page.html')


@app.post("/urls")
def receive_url():
    income_url = request.form.get('url').strip()
    errors = validate(income_url)

    if errors:
        for error in errors:
            flash(error, "danger")
        return redirect(url_for('view_home_page', url=income_url), code=302)

    id = db.select(table_name='urls',
                   fields=['id'],
                   where='name',
                   param=income_url)
    if id:
        value_of_id = db.extract_one(id)
        flash("Страница уже существует", "info")
        return redirect(url_for('show_site_page', id=value_of_id), code=302)

    db.insert(table_name='urls',
              fields=['name', 'created_at'],
              values=[income_url, date.today()])

    id = db.select(table_name='urls',
                   fields=['id'],
                   where='name',
                   param=income_url)
    value_of_id = db.extract_one(id)

    flash("Страница добавлена успешно", "success")
    return redirect(url_for("show_site_page", id=value_of_id), code=302)


@app.get("/urls/<id>")
def show_site_page(id):
    item_data = db.select(table_name='urls',
                          take_all=True,
                          where='id',
                          param=id)
    item = db.change_structure(item_data, keys=["id", "name", "created_at"])[0]

    checks_data = db.select(table_name='url_checks',
                            take_all=True,
                            where='url_id',
                            param=id,
                            sort_by='id')
    checks = db.change_structure(checks_data,
                                 keys=[
                                     "id", "url_id", "status_code",
                                     "h1", "title", "description",
                                     "created_at"
                                 ])

    return render_template('url_page.html', item=item, checks=checks)


@app.get("/urls")
def show_websites():
    selected = db.select_table_websites()
    data = db.change_structure(selected, keys=["id",
                                               "name",
                                               "created_at",
                                               "status_code"])
    return render_template("urls_page.html", data=data)


@app.post("/urls/<id>/checks")
def check(id):
    selected_url = db.select(table_name='urls',
                             fields=["name"],
                             where='id',
                             param=int(id))
    url = db.extract_one(selected_url)
    code = get_status_code(url)

    if not code:
        flash("Произошла ошибка при проверке", "danger")
        return redirect(url_for('show_site_page', id=id), code=302)

    seo_params = parse(url)
    db.insert(table_name='url_checks',
              fields=['url_id', 'created_at', 'status_code',
                      'h1', 'title', 'description'],
              values=[id, date.today(), code, seo_params["h1"],
                      seo_params["title"], seo_params["description"]])
    flash("Страница успешно проверена", "success")
    return redirect(url_for("show_site_page", id=id), code=302)


if __name__ == '__main__':
    app.run()

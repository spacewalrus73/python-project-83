import os
from dotenv import load_dotenv
from page_analyzer import db_manager as db
from page_analyzer.validator import validate
from flask import (
    Flask,
    render_template,
    request,
    flash,
    url_for,
    redirect)


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route("/")
def view_home_page(url=''):
    return render_template('home_page.html', url=url)


@app.post("/urls")
def receive_url():
    income_url = request.form.get('url').strip()
    errors = validate(income_url)

    if errors:
        for error in errors:
            flash(error, "danger")
        return redirect(url_for('view_home_page', url=income_url), code=302)

    with db.connect_db(DATABASE_URL) as conn:

        if db.get_id(conn, income_url):
            flash("Страница уже существует", "info")
            return redirect(url_for('view_home_page', url=income_url), code=302)

        db.add_url(conn, income_url)
        id = db.get_id(conn, income_url)
    flash("Страница добавлена успешно", "success")
    return redirect(url_for("show_site_page", id=id), code=302)


@app.get("/urls/<id>")
def show_site_page(id):
    with db.connect_db(DATABASE_URL) as conn:
        item_data = db.get_by_id(conn, int(id))
    return render_template('url_page.html', item=item_data)


@app.get("/urls")
def show_websites():
    with db.connect_db(DATABASE_URL) as conn:
        data = db.get_all_data(conn)
    return render_template("urls_page.html", data=data)

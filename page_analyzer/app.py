import os
from dotenv import load_dotenv
import page_analyzer.actions as act
from page_analyzer.validator import validate
from page_analyzer.normalizer import normalize
from page_analyzer.url_checker import get_status_code
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
    normalized_url = normalize(income_url)

    if errors:
        for error in errors:
            flash(error, "danger")
        return render_template('home_page.html'), 422

    if act.is_exist(where_name=normalized_url):
        flash("Страница уже существует", "info")
    else:
        act.add_url(normalized_url)
        flash("Страница успешно добавлена", "success")

    return redirect(
        url_for("show_site_page", id=act.get_id(normalized_url)), code=302
    )


@app.get("/urls/<id>")
def show_site_page(id):
    return render_template('url_page.html',
                           item=act.get_site(int(id)),
                           checks=act.get_check(int(id)))


@app.get("/urls")
def show_websites():
    return render_template("urls_page.html", data=act.get_websites())


@app.post("/urls/<id>/checks")
def check(id):
    url = act.get_url(id)
    code = get_status_code(url)

    if not code:
        flash("Произошла ошибка при проверке", "danger")
    else:
        act.add_check(id, code, url)
        flash("Страница успешно проверена", "success")

    return redirect(url_for("show_site_page", id=id), code=302)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html")


if __name__ == '__main__':
    app.run()

from flask import render_template, request, redirect, url_for, flash

from flask_login import login_user, login_required

from werkzeug.security import check_password_hash

from . import app
from .database import session, Entry, User


PAGINATE_BY = 10


@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1):

    global PAGINATE_BY

    #zero indexed page
    page_index = page - 1

    if 'limit' in request.args:
        if request.args.get('limit').isdigit():
            PAGINATE_BY = int(request.args.get('limit'))

    count = session.query(Entry).count()

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) / PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]

    return render_template("entries.html",
                           entries=entries,
                           has_next=has_next,
                           has_prev=has_prev,
                           page=page,
                           total_pages=total_pages)


@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")


@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))


@app.route("/entry/<int:id>")
def view_entry(id):

    entry = session.query(Entry).get(id + 1)

    return render_template("view_entry.html", entry=entry)


@app.route("/entry/edit/<int:id>", methods=["GET"])
def edit_entry(id):

    entry = session.query(Entry).get(id + 1)

    return render_template("edit_entry.html", entry=entry)


@app.route("/entry/edit/<int:id>", methods=["POST"])
def edit_entry_post(id):

    entry = session.query(Entry).get(id + 1)

    entry.content = request.form["content"]
    session.commit()

    return render_template("view_entry.html", entry=entry)


@app.route("/entry/delete/<int:id>", methods=["GET"])
def delete_entry(id):

    entry = session.query(Entry).get(id + 1)

    session.delete(entry)
    session.commit()

    return redirect("/")


@app.route("/login", methods=['GET'])
def login_get():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))




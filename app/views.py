# -*- coding:utf-8 -*-
from flask import render_template, redirect, request, url_for, flash, g, abort
from app import app, lm, db
from models import User, Book, Log
from flask.ext.login import current_user, login_required, login_user, logout_user
from .forms import LoginForm, RegistrationForm, EditProfileForm, EditBookForm, ChangePasswordForm, SearchForm
from functools import wraps


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.admin:
            abort(403)
        return func(*args, **kwargs)

    return decorated_function


@app.before_request
def before_request():
    g.user = current_user


@app.route('/')
def index():
    search_form = SearchForm()
    popular_books = Book.query.outerjoin(Log).group_by(Book.id).order_by(db.func.count(Log.id).desc()).limit(5)
    popular_users = User.query.outerjoin(Log).group_by(User.id).order_by(db.func.count(Log.id).desc()).limit(5)
    print popular_books
    return render_template("index.html", books=popular_books, users=popular_users, search_form=search_form)


@app.route('/book/')
def book():
    searchword = request.args.get('search', None)
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)

    if searchword:
        searchword = searchword.strip()
        books = Book.query.filter(Book.title.ilike(u"%%%s%%" % searchword)).order_by(Book.id.desc())
        search_form.search.data = searchword
    else:
        books = Book.query.order_by(Book.id.desc())

    pagination = books.paginate(page, per_page=8)
    result_books = pagination.items
    return render_template("book.html", books=result_books, pagination=pagination, search_form=search_form,
                           title=u"书籍清单")


@app.route('/book/<int:bid>/')
def book_detail(bid):
    the_book = Book.query.get_or_404(bid)
    # borrowing_data = map(lambda l: (l.user, l.timestamp), Log.query.filter_by(book_id=bid, returned=0).all())
    # borrowed_data = map(lambda l: (l.user, l.timestamp), Log.query.filter_by(book_id=bid, returned=1).all())

    show = request.args.get('show', 0, type=int)
    if show != 0:
        show = 1

    page = request.args.get('page', 1, type=int)
    pagination = the_book.logs.filter_by(returned=show) \
        .order_by(Log.borrow_timestamp.desc()).paginate(page, per_page=10)
    logs = pagination.items

    return render_template("book_detail.html", book=the_book, logs=logs, title=the_book.title)


@app.route('/book/<int:bid>/edit/', methods=['GET', 'POST'])
@admin_required
def book_edit(bid):
    book = Book.query.get_or_404(bid)
    form = EditBookForm()
    if form.validate_on_submit():
        book.title = form.title.data
        book.subtitle = form.subtitle.data
        book.author = form.author.data
        book.isbn = form.isbn.data
        book.category = form.category.data
        book.numbers = form.numbers.data
        book.description = form.description.data
        db.session.add(book)
        db.session.commit()
        flash(u'书籍资料已保存!', 'success')
        return redirect(url_for('book_detail', bid=bid))
    form.title.data = book.title
    form.subtitle.data = book.subtitle
    form.author.data = book.author
    form.isbn.data = book.isbn
    form.category.data = book.category
    form.numbers.data = book.numbers
    form.description.data = book.description
    return render_template("book_edit.html", form=form, book=book, title=u"编辑书籍资料")


@app.route('/book/add/', methods=['GET', 'POST'])
@admin_required
def book_add():
    form = EditBookForm()
    if form.validate_on_submit():
        new_book = Book(
            title=form.title.data,
            subtitle=form.subtitle.data,
            author=form.author.data,
            isbn=form.isbn.data,
            category=form.category.data,
            numbers=form.numbers.data,
            description=form.description.data)
        db.session.add(new_book)
        db.session.commit()
        flash(u'书籍 %s 已添加至图书馆!' % new_book.title, 'success')
        return redirect(url_for('book_detail', bid=new_book.id))
    return render_template("book_edit.html", form=form, title=u"添加新书")


@app.route('/book/<int:bid>/borrow/')
@login_required
def book_borrow(bid):
    the_book = Book.query.get_or_404(bid)
    flash(*current_user.borrow_book(the_book))
    db.session.commit()
    return redirect(request.args.get('next') or url_for('book_detail', bid=bid))


@app.route('/book/return/<lid>/')
@login_required
def book_return(lid):
    flash(*current_user.return_book(lid))
    db.session.commit()
    return redirect(request.args.get('next') or url_for('book_detail', bid=lid))


@app.route('/user/')
def user():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id.desc()).paginate(page, per_page=10)
    users = pagination.items
    return render_template("user.html", users=users, pagination=pagination, title=u"已注册用户")


@app.route('/user/<int:uid>/')
def user_detail(uid):
    the_user = User.query.get_or_404(uid)
    # borrowing_data = Log.query.filter_by(user_id=uid, returned=0).all()
    # borrowed_data = Log.query.filter_by(user_id=uid, returned=1).all()

    show = request.args.get('show', 0, type=int)
    if show != 0:
        show = 1

    page = request.args.get('page', 1, type=int)
    pagination = the_user.logs.filter_by(returned=show) \
        .order_by(Log.borrow_timestamp.desc()).paginate(page, per_page=10)
    logs = pagination.items

    return render_template("user_detail.html", user=the_user, logs=logs, pagination=pagination,
                           title=u"用户: " + the_user.name)


@app.route('/card/')
def card():
    show = request.args.get('show', 0, type=int)
    if show != 0:
        show = 1

    page = request.args.get('page', 1, type=int)
    pagination = Log.query.filter_by(returned=show).order_by(Log.borrow_timestamp.desc()).paginate(page, per_page=10)
    logs = pagination.items
    return render_template("card.html", logs=logs, pagination=pagination, title=u"借阅信息")


@app.route('/login/', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        the_user = User.query.filter(db.func.lower(User.email) == db.func.lower(login_form.email.data)).first()
        if the_user is not None and the_user.password == login_form.password.data:
            login_user(the_user, login_form.remember_me.data)
            flash(u'登录成功!  欢迎您 %s' % the_user.name, 'success')
            return redirect(request.args.get('next') or url_for('index'))
        flash(u'用户名无效或密码错误', 'danger')
    return render_template("login.html", form=login_form, title=u"登入")


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash(u'您已经成功登出!', 'info')
    return redirect(url_for('index'))


@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        the_user = User(email=form.email.data,
                        name=form.name.data,
                        password=form.password.data)
        db.session.add(the_user)
        db.session.commit()
        flash(u'注册成功! 欢迎您 %s' % form.name.data, 'success')
        login_user(the_user)
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('register.html', form=form, title=u"新用户注册")


@app.route('/user/<int:uid>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(uid):
    if current_user.id == uid or current_user.admin:
        the_user = User.query.get_or_404(uid)
        form = EditProfileForm()
        if form.validate_on_submit():
            the_user.name = form.name.data
            the_user.major = form.major.data
            the_user.about_me = form.about_me.data
            db.session.add(the_user)
            db.session.commit()
            flash(u'资料更新成功!', "info")
            return redirect(url_for('user_detail', uid=uid))
        form.name.data = the_user.name
        form.major.data = the_user.major
        form.about_me.data = the_user.about_me
        return render_template('user_edit.html', form=form, user=the_user, title=u"编辑资料")
    else:
        abort(403)


@app.route('/change_password/', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.new_password.data
        db.session.add(current_user)
        db.session.commit()
        flash(u'密码更新成功!', 'info')
        return redirect(url_for('user_detail', uid=current_user.id))
    return render_template('user_edit.html', form=form, user=current_user, title=u"修改密码")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

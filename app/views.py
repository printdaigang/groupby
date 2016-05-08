# -*- coding:utf-8 -*-
from flask import render_template, redirect, request, url_for, flash, g, abort
from app import app, lm, db, avatars
from .models import User, Book, Log, Comment
from flask.ext.login import current_user, login_required, login_user, logout_user
from .forms import LoginForm, RegistrationForm, EditProfileForm, EditBookForm, ChangePasswordForm, SearchForm, \
    CommentForm, AvatarEditForm, AvatarUploadForm
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
    recently_comments = Comment.query.filter_by(deleted=0).order_by(Comment.edit_timestamp.desc()).limit(5)
    # print popular_books
    return render_template("index.html", books=popular_books, users=popular_users, recently_comments=recently_comments,
                           search_form=search_form)


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


@app.route('/book/<book_id>/')
def book_detail(book_id):
    the_book = Book.query.get_or_404(book_id)
    # borrowing_data = map(lambda l: (l.user, l.timestamp), Log.query.filter_by(book_id=book_id, returned=0).all())
    # borrowed_data = map(lambda l: (l.user, l.timestamp), Log.query.filter_by(book_id=book_id, returned=1).all())

    show = request.args.get('show', 0, type=int)
    page = request.args.get('page', 1, type=int)
    form = CommentForm()

    if show in (1, 2):
        pagination = the_book.logs.filter_by(returned=show - 1) \
            .order_by(Log.borrow_timestamp.desc()).paginate(page, per_page=5)
    else:
        pagination = the_book.comments.filter_by(deleted=0) \
            .order_by(Comment.edit_timestamp.desc()).paginate(page, per_page=5)

    data = pagination.items
    # print data
    return render_template("book_detail.html", book=the_book, data=data, pagination=pagination, form=form,
                           title=the_book.title)


@app.route('/book/<int:book_id>/edit/', methods=['GET', 'POST'])
@admin_required
def book_edit(book_id):
    book = Book.query.get_or_404(book_id)
    form = EditBookForm()
    if form.validate_on_submit():
        book.isbn = form.isbn.data
        book.title = form.title.data
        book.origin_title = form.origin_title.data
        book.subtitle = form.subtitle.data
        book.author = form.author.data
        book.translator = form.translator.data
        book.publisher = form.publisher.data
        book.image = form.image.data
        book.pubdate = form.pubdate.data
        book.tags = form.tags.data
        book.pages = form.pages.data
        book.price = form.price.data
        book.binding = form.binding.data
        book.numbers = form.numbers.data
        book.summary = form.summary.data
        book.catalog = form.catalog.data
        db.session.add(book)
        db.session.commit()
        flash(u'书籍资料已保存!', 'success')
        return redirect(url_for('book_detail', book_id=book_id))
    form.isbn.data = book.isbn
    form.title.data = book.title
    form.origin_title.data = book.origin_title
    form.subtitle.data = book.subtitle
    form.author.data = book.author
    form.translator.data = book.translator
    form.publisher.data = book.publisher
    form.image.data = book.image
    form.pubdate.data = book.pubdate
    form.tags.data = book.tags
    form.pages.data = book.pages
    form.price.data = book.price
    form.binding.data = book.binding
    form.numbers.data = book.numbers
    form.summary.data = book.summary or ""
    form.catalog.data = book.catalog or ""
    return render_template("book_edit.html", form=form, book=book, title=u"编辑书籍资料")


@app.route('/book/add/', methods=['GET', 'POST'])
@admin_required
def book_add():
    form = EditBookForm()
    form.numbers.data = 3
    if form.validate_on_submit():
        new_book = Book(
            isbn=form.isbn.data,
            title=form.title.data,
            origin_title=form.origin_title.data,
            subtitle=form.subtitle.data,
            author=form.author.data,
            translator=form.translator.data,
            publisher=form.publisher.data,
            image=form.image.data,
            pubdate=form.pubdate.data,
            tags=form.tags.data,
            pages=form.pages.data,
            price=form.price.data,
            binding=form.binding.data,
            numbers=form.numbers.data,
            summary=form.summary.data or "",
            catalog=form.catalog.data or "")
        db.session.add(new_book)
        db.session.commit()
        flash(u'书籍 %s 已添加至图书馆!' % new_book.title, 'success')
        return redirect(url_for('book_detail', book_id=new_book.id))
    return render_template("book_edit.html", form=form, title=u"添加新书")


@app.route('/book/<int:book_id>/borrow/')
@login_required
def book_borrow(book_id):
    the_book = Book.query.get_or_404(book_id)
    flash(*current_user.borrow_book(the_book))
    db.session.commit()
    return redirect(request.args.get('next') or url_for('book_detail', book_id=book_id))


@app.route('/book/return/<lid>/')
@login_required
def book_return(lid):
    flash(*current_user.return_book(lid))
    db.session.commit()
    return redirect(request.args.get('next') or url_for('book_detail', book_id=lid))


@app.route('/book/<int:book_id>/comment/', methods=['POST', ])
@login_required
def add_comment(book_id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(user=current_user, book=Book.query.get_or_404(book_id), comment=form.comment.data)
        db.session.add(comment)
        db.session.commit()
    return redirect(request.args.get('next') or url_for('book_detail', book_id=book_id))


@app.route('/user/')
def user():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id.desc()).paginate(page, per_page=10)
    users = pagination.items
    return render_template("user.html", users=users, pagination=pagination, title=u"已注册用户")


@app.route('/user/<int:user_id>/')
def user_detail(user_id):
    the_user = User.query.get_or_404(user_id)
    # borrowing_data = Log.query.filter_by(user_id=user_id, returned=0).all()
    # borrowed_data = Log.query.filter_by(user_id=user_id, returned=1).all()

    show = request.args.get('show', 0, type=int)
    if show != 0:
        show = 1

    page = request.args.get('page', 1, type=int)
    pagination = the_user.logs.filter_by(returned=show) \
        .order_by(Log.borrow_timestamp.desc()).paginate(page, per_page=10)
    logs = pagination.items

    return render_template("user_detail.html", user=the_user, logs=logs, pagination=pagination,
                           title=u"用户: " + the_user.name)


@app.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    if current_user.id == user_id or current_user.admin:
        the_user = User.query.get_or_404(user_id)
        form = EditProfileForm()
        if form.validate_on_submit():
            the_user.name = form.name.data
            the_user.major = form.major.data
            the_user.headline = form.headline.data
            the_user.about_me = form.about_me.data
            db.session.add(the_user)
            db.session.commit()
            flash(u'资料更新成功!', "info")
            return redirect(url_for('user_detail', user_id=user_id))
        form.name.data = the_user.name
        form.major.data = the_user.major
        form.headline.data = the_user.headline
        form.about_me.data = the_user.about_me

        return render_template('user_edit.html', form=form, user=the_user, title=u"编辑资料")
    else:
        abort(403)


@app.route('/user/<int:user_id>/avatar_edit', methods=['GET', 'POST'])
@login_required
def avatar_edit(user_id):
    if current_user.id == user_id or current_user.admin:
        the_user = User.query.get_or_404(user_id)
        avatar_edit_form = AvatarEditForm()
        avatar_upload_form = AvatarUploadForm()
        if avatar_upload_form.validate_on_submit():
            print "avatar_edit_form"
            if 'avatar' in request.files:
                forder = str(user_id)
                avatar_name = avatars.save(avatar_upload_form.avatar.data, folder=forder)
                the_user.avatar = '/_uploads/avatars/%s' % avatar_name
                db.session.add(the_user)
                db.session.commit()
                flash(u'头像更新成功!', 'success')
                return redirect(url_for('user_detail', user_id=user_id))
        if avatar_edit_form.validate_on_submit():
            the_user.avatar = avatar_edit_form.avatar_url.data
            db.session.add(the_user)
            db.session.commit()
            return redirect(url_for('user_detail', user_id=user_id))
        return render_template('avatar_edit.html', user=the_user, avatar_edit_form=avatar_edit_form,
                               avatar_upload_form=avatar_upload_form, title=u"更换头像")
    else:
        abort(403)


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
            flash(u'登录成功!  欢迎您 %s!' % the_user.name, 'success')
            return redirect(request.args.get('next') or url_for('index'))
        flash(u'用户名无效或密码错误!', 'danger')
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
        flash(u'注册成功! 欢迎您 %s!' % form.name.data, 'success')
        login_user(the_user)
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('register.html', form=form, title=u"新用户注册")


@app.route('/change_password/', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.new_password.data
        db.session.add(current_user)
        db.session.commit()
        flash(u'密码更新成功!', 'info')
        return redirect(url_for('user_detail', user_id=current_user.id))
    return render_template('user_edit.html', form=form, user=current_user, title=u"修改密码")


@app.route('/commnet/delete/<int:comment_id>')
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user.id == comment.user_id or current_user.admin:
        comment.deleted = 1
        book_id = comment.book_id
        db.session.add(comment)
        db.session.commit()
        flash(u'成功删除一条评论.', 'info')
        return redirect(request.args.get('next') or url_for('book_detail', book_id=book_id))
    else:
        abort(403)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(413)
def request_entity_too_large(e):
    return 'Request Entity Too Large', 413


@app.errorhandler(415)
def UploadNotAllowed(e):
    return 'Upload Not Allowed', 415

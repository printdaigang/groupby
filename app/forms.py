# -*- coding:utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, FileField
from wtforms import ValidationError
from wtforms.validators import Email, Length, DataRequired, EqualTo, Regexp
from .models import User
from flask.ext.pagedown.fields import PageDownField


class LoginForm(Form):
    email = StringField('Email',
                        validators=[DataRequired(message=u"该项忘了填写了!"), Length(1, 64), Email(message=u"你确定这是 Email ?")])
    password = PasswordField(u'密码', validators=[DataRequired(message=u"该项忘了填写了!"), Length(1, 128)])
    remember_me = BooleanField(u"保持我的登入状态", default=True)
    submit = SubmitField(u'登入')


class RegistrationForm(Form):
    email = StringField('Email',
                        validators=[DataRequired(message=u"该项忘了填写了!"), Length(1, 64), Email(message=u"你确定这是 Email ?")])
    name = StringField(u'用户名', validators=[DataRequired(message=u"该项忘了填写了!"), Length(1, 64)])
    password = PasswordField(u'密码',
                             validators=[DataRequired(message=u"该项忘了填写了!"), EqualTo('password2', message=u'密码必须匹配'),
                                         Length(1, 128)])
    password2 = PasswordField(u'再次确认密码', validators=[DataRequired(message=u"该项忘了填写了!")])
    submit = SubmitField(u'注册')

    def validate_email(self, filed):
        from app import db
        if User.query.filter(db.func.lower(User.email) == db.func.lower(filed.data)).first():
            raise ValidationError(u'该 Email 已经被注册了')


class EditProfileForm(Form):
    name = StringField(u'用户名', validators=[DataRequired(message=u"该项忘了填写了!"), Length(1, 64, message=u"长度为1到64个字符")])
    major = StringField(u'主修专业', validators=[Length(0, 128, message=u"长度为0到128个字符")])
    about_me = TextAreaField(u"用户自我简介")
    submit = SubmitField(u"保存更改")


class EditBookForm(Form):
    isbn = StringField(u"ISBN",
                       validators=[DataRequired(message=u"该项忘了填写了!"), Regexp('[0-9]{13,13}', message=u"ISBN必须是13位数字")])
    title = StringField(u"书名", validators=[DataRequired(message=u"该项忘了填写了!"), Length(1, 128, message=u"长度为1到128个字符")])
    origin_title = StringField(u"原作名", validators=[Length(0, 128, message=u"长度为0到128个字符")])
    subtitle = StringField(u"副标题", validators=[Length(0, 128, message=u"长度为0到128个字符")])
    author = StringField(u"作者", validators=[Length(0, 128, message=u"长度为0到64个字符")])
    translator = StringField(u"译者",
                             validators=[Length(0, 64, message=u"长度为0到64个字符")])
    publisher = StringField(u"出版社", validators=[Length(0, 64, message=u"长度为0到64个字符")])
    image = StringField(u"图片地址", validators=[Length(0, 128, message=u"长度为0到128个字符")])
    pubdate = StringField(u"出版日期", validators=[Length(0, 32, message=u"长度为0到32个字符")])
    tags = StringField(u"标签", validators=[Length(0, 128, message=u"长度为0到128个字符")])
    pages = IntegerField(u"页数")
    price = StringField(u"定价", validators=[Length(0, 64, message=u"长度为0到32个字符")])
    binding = StringField(u"装帧", validators=[Length(0, 16, message=u"长度为0到16个字符")])
    numbers = IntegerField(u"馆藏", validators=[DataRequired(message=u"该项忘了填写了!")])
    summary = PageDownField(u"内容简介")
    catalog = PageDownField(u"目录")
    submit = SubmitField(u"保存更改")


class ChangePasswordForm(Form):
    old_password = PasswordField(u'旧密码', validators=[DataRequired(message=u"该项忘了填写了!")])
    new_password = PasswordField(u'新密码', validators=[DataRequired(message=u"该项忘了填写了!"),
                                                     EqualTo('confirm_password', message=u'密码必须匹配'),
                                                     Length(1, 128)])
    confirm_password = PasswordField(u'确认新密码', validators=[DataRequired(message=u"该项忘了填写了!")])
    submit = SubmitField(u"保存密码")

    def validate_old_password(self, filed):
        from app.views import current_user
        if current_user.password != filed.data:
            raise ValidationError(u'原密码错误')


class SearchForm(Form):
    search = StringField(u"搜索书籍", validators=[DataRequired()])


class CommentForm(Form):
    comment = TextAreaField(u"你的书评",
                            validators=[DataRequired(message=u"内容不能为空"), Length(1, 1024, message=u"书评长度限制在1024字符以内")])
    submit = SubmitField(u"发布")

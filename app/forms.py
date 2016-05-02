# -*- coding:utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField
from wtforms import ValidationError
from wtforms.validators import Email, Length, DataRequired, EqualTo
from .models import User


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[DataRequired()])
    remember_me = BooleanField(u"保持我的登入状态", default=True)
    submit = SubmitField(u'登入')


class RegistrationForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    name = StringField(u'用户名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField(u'密码', validators=[DataRequired(), EqualTo('password2', message=u'密码必须匹配')])
    password2 = PasswordField(u'再次确认密码', validators=[DataRequired()])
    submit = SubmitField(u'注册')

    def validate_email(self, filed):
        from app import db
        if User.query.filter(db.func.lower(User.email) == db.func.lower(filed.data)).first():
            raise ValidationError(u'邮箱已注册')


class EditProfileForm(Form):
    name = StringField(u'用户名', validators=[DataRequired(), Length(1, 64)])
    major = StringField(u'主修专业', validators=[Length(0, 128)])
    about_me = TextAreaField(u"用户自我简介")
    submit = SubmitField(u"保存更改")


class EditBook(Form):
    title = StringField(u"书名", validators=[DataRequired(), Length(1, 128)])
    subtitle = StringField(u"副标题", validators=[Length(0, 256)])
    author = StringField(u"作者", validators=[DataRequired(), Length(0, 64)])
    isbn = StringField(u"ISBN", validators=[DataRequired(), Length(0, 32)])
    category = StringField(u"分类", validators=[DataRequired(), Length(0, 64)])
    numbers = IntegerField(u"馆藏", validators=[DataRequired()])
    description = TextAreaField(u"内容简介")
    submit = SubmitField(u"保存更改")

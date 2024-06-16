# -*- coding: UTF-8 -*-

import os
from flask import Flask, g, render_template, request, jsonify, url_for, send_file, redirect, flash, get_flashed_messages
from sqlalchemy import or_
from models import db_session, Categories, News, Author, Comment, Portal, UserArticleInteraction
import settings
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import uuid
from datetime import datetime
from sqlalchemy.orm import joinedload

# Инициализация приложения Flask
app = Flask(__name__, template_folder="templates")

# Установка секретного ключа для сессий
app.config['SECRET_KEY'] = str(uuid.uuid4())

# Настройка менеджера входа в систему
manager = LoginManager(app)

# Обработчик ошибки 404 (страница не найдена)
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.htm'), 404

# Маршрут для перенаправления на главную страницу
@app.route("/")
def index():
    return redirect(url_for('view_main_page'))

# Маршрут для отображения главной страницы
@app.route("/main/")
def view_main_page():
    portal = db_session.query(Portal).first()  # Получение данных о портале
    news = db_session.query(News).all()  # Получение всех новостей
    return render_template("news.htm", portal=portal, news=news, enumerate=enumerate)

# Маршрут для поиска новостей по ключевому слову
@app.route("/search/", methods=['POST'])
def search():
    keyword = request.form['keyword']  # Получение ключевого слова из формы
    portal = db_session.query(Portal).first()  # Получение данных о портале
    # Поиск новостей по ключевому слову в названии или кратком описании
    news = db_session.query(News).filter(or_(News.name.like(f"%{keyword}%"), News.short_description.like(f"%{keyword}%"))).all()
    return render_template("search_results.htm", news=news, portal=portal, enumerate=enumerate)

# Маршрут для отображения новостей в категории "Политика"
@app.route("/politic/")
def view_politic_page():
    portal = db_session.query(Portal).first()  # Получение данных о портале
    news = db_session.query(News).filter(News.category_id == 2).all()  # Фильтрация новостей по категории
    return render_template("news.htm", portal=portal, news=news, enumerate=enumerate)

# Маршрут для добавления комментария к новости
@app.route("/add_comment/<int:news_id>/", methods=['POST'])
def add_comment(news_id):
    portal = db_session.query(Portal).first()
    comment_text = request.form["comment"]  # Получение текста комментария из формы
    if current_user.is_authenticated:
        # Создание нового комментария
        new_comment = Comment(
            author_id=current_user.author_id,
            news_id=news_id,
            datetime=datetime.now(),
            comment=comment_text
        )
        db_session.add(new_comment)
        db_session.commit()
    return redirect(url_for('news_by_id', id=news_id, portal=portal, enumerate=enumerate))

# Маршрут для отображения конкретной новости
@app.route("/news/<int:news_id>/")
def view_news_item(news_id):
    item = db_session.query(News).filter_by(news_id=news_id).first()  # Получение новости по ID
    comments = db_session.query(Comment).filter_by(news_id=news_id).all()  # Получение комментариев для новости
    return render_template("news_item.htm", item=item, comments=comments)

# Маршрут для отображения карточки новости
@app.route("/main/news_card/<int:id>/")
def news_by_id(id):
    item = db_session.query(News).filter(News.news_id == id).first()  # Получение новости по ID
    comments = db_session.query(Comment).filter_by(news_id=id).all()  # Получение комментариев для новости
    portal = db_session.query(Portal).first()  # Получение данных о портале

    # Загружаем взаимодействия пользователя с текущей статьей
    user_interaction = None
    if current_user.is_authenticated:
        user_interaction = db_session.query(UserArticleInteraction).filter_by(user_id=current_user.author_id, news_id=id).first()

    # Получаем flash-сообщения
    flash_messages = get_flashed_messages(with_categories=True)

    return render_template("news_card.htm", portal=portal, comments=comments, item=item,
                           user_interaction=user_interaction, flash_messages=flash_messages, enumerate=enumerate)

# Маршрут для отображения новостей в категории "Наука"
@app.route("/science/")
def view_science_page():
    portal = db_session.query(Portal).first()  # Получение данных о портале
    news = db_session.query(News).filter(News.category_id == 5).all()  # Фильтрация новостей по категории
    return render_template("news.htm", portal=portal, news=news, enumerate=enumerate)

# Маршрут для удаления комментария
@app.route("/delete_comment/<int:comment_id>/", methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = db_session.query(Comment).filter_by(comment_id=comment_id).first()  # Получение комментария по ID
    if comment:
        # Проверка, что текущий пользователь является автором комментария
        if current_user.author_id == comment.author_id:
            db_session.delete(comment)
            db_session.commit()
            flash("Комментарий успешно удален", "success")
        else:
            flash("Вы не можете удалить этот комментарий", "error")
    else:
        flash("Комментарий не найден", "error")
    return redirect(request.referrer)

# Маршрут для отображения новостей в категории "Спорт"
@app.route("/sport/")
def view_sport_page():
    portal = db_session.query(Portal).first()  # Получение данных о портале
    news = db_session.query(News).filter(News.category_id == 4).all()  # Фильтрация новостей по категории
    return render_template("news.htm", portal=portal, news=news, enumerate=enumerate)

# Маршрут для отображения новостей в категории "Экономика"
@app.route("/economic/")
def view_economic_page():
    portal = db_session.query(Portal).first()  # Получение данных о портале
    news = db_session.query(News).filter(News.category_id == 3).all()  # Фильтрация новостей по категории
    return render_template("news.htm", portal=portal, news=news, enumerate=enumerate)

# Маршрут для входа в систему
@app.route("/login/", methods=['GET', 'POST'])
def login():
    portal = db_session.query(Portal).first()  # Получение данных о портале
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        user = Author.query.filter_by(name=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('view_main_page', page_name='index'))  # Перенаправление на главную страницу
        else:
            # В случае неверного логина или пароля
            return render_template('login.htm', error='Invalid username or password', portal=portal)
    return render_template("login.htm", portal=portal)

# Маршрут для выхода из системы
@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('view_main_page', page_name='index'))  # Перенаправление на главную страницу

# Маршрут для регистрации нового пользователя
@app.route("/registration/", methods=['GET', 'POST'])
def register():
    portal = db_session.query(Portal).first()  # Получение данных о портале
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        # Создание нового пользователя
        new_user = Author(name=username, password=password)
        db_session.add(new_user)
        db_session.commit()
        login_user(new_user)
        return redirect(url_for('view_main_page'))
    return render_template("registration.htm", portal=portal)

# Маршрут для оценки статьи (лайк)
@app.route('/like_article/<int:news_id>/', methods=['POST'])
@login_required
def like_article(news_id):
    # Проверка существующего взаимодействия
    existing_interaction = db_session.query(UserArticleInteraction).filter_by(user_id=current_user.author_id, news_id=news_id).first()
    if existing_interaction:
        flash("Вы уже оценили эту статью ранее.")
        return redirect(url_for('news_by_id', id=news_id))

    interaction = UserArticleInteraction(user_id=current_user.author_id, news_id=news_id, interaction_type='like')
    db_session.add(interaction)
    news = db_session.query(News).get(news_id)
    news.likes += 1
    db_session.commit()
    flash('Статья оценена.', 'success')
    return redirect(url_for('news_by_id', id=news_id))

# Маршрут для оценки статьи (дизлайк)
@app.route('/dislike_article/<int:news_id>/', methods=['POST'])
@login_required
def dislike_article(news_id):
    # Проверка существующего взаимодействия
    existing_interaction = db_session.query(UserArticleInteraction).filter_by(user_id=current_user.author_id, news_id=news_id).first()
    if existing_interaction:
        flash("Вы уже взаимодействовали с этой статьей ранее.")
        return redirect(url_for('news_by_id', id=news_id))

    interaction = UserArticleInteraction(user_id=current_user.author_id, news_id=news_id, interaction_type='dislike')
    db_session.add(interaction)
    news = db_session.query(News).get(news_id)
    news.dislikes += 1
    db_session.commit()
    return redirect(url_for('news_by_id', id=news_id))

# Маршрут для сохранения статьи
@app.route('/save_article/<int:news_id>/', methods=['POST'])
@login_required
def save_article(news_id):
    # Проверка существующего взаимодействия
    existing_interaction = db_session.query(UserArticleInteraction).filter_by(user_id=current_user.author_id, news_id=news_id).first()
    if existing_interaction:
        flash("Вы уже взаимодействовали с этой статьей ранее.")
        return redirect(url_for('news_by_id', id=news_id))

    interaction = UserArticleInteraction(user_id=current_user.author_id, news_id=news_id, interaction_type='save')
    db_session.add(interaction)
    db_session.commit()
    return redirect(url_for('news_by_id', id=news_id))

# Маршрут для отображения страницы
@app.route("/<page_name>/")
def main(page_name):
    return render_template(page_name + ".htm")

# Загрузка пользователя по ID для flask-login
@manager.user_loader
def load_user(user_id):
    return Author.query.get(user_id)

# Запуск приложения
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

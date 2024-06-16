from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base, db_session, engine as db_engine
from datetime import datetime
from flask_login import UserMixin


# Модель Author, представляющая пользователей авторов в базе данных
class Author(Base, UserMixin):
    __tablename__ = 'authors'
    author_id = Column(Integer, primary_key=True)  # Первичный ключ
    name = Column(String, unique=True)  # Имя автора, должно быть уникальным
    password = Column(String)  # Пароль автора
    photo = Column(String)  # Фото автора

    # Отношение один-ко-многим с новостями, комментариями и взаимодействиями
    news = relationship("News", backref="author")
    comments = relationship("Comment", backref="author")
    interactions = relationship("UserArticleInteraction", backref="user")

    # Метод для получения ID пользователя для flask-login
    def get_id(self):
        return str(self.author_id)


# Модель News, представляющая новости в базе данных
class News(Base):
    __tablename__ = 'news'
    news_id = Column(Integer, primary_key=True)  # Первичный ключ
    category_id = Column(Integer, ForeignKey('categories.category_id'))  # Внешний ключ к категории
    datetime = Column(DateTime, default=datetime.utcnow)  # Дата и время публикации
    name = Column(String)  # Название новости
    short_description = Column(String(150), default='')  # Краткое описание новости
    photo = Column(String)  # Фото к новости
    full_description = Column(String)  # Полное описание новости
    author_id = Column(Integer, ForeignKey('authors.author_id'))  # Внешний ключ к автору
    likes = Column(Integer, default=0)  # Количество лайков
    dislikes = Column(Integer, default=0)  # Количество дизлайков

    # Отношение один-ко-многим с комментариями и взаимодействиями
    comments = relationship("Comment", backref="news")
    interactions = relationship("UserArticleInteraction", backref="news")

    # Отношение многие-к-одному с категорией
    category = relationship("Categories", back_populates="news")


# Модель Comment, представляющая комментарии в базе данных
class Comment(Base):
    __tablename__ = 'comments'
    comment_id = Column(Integer, primary_key=True)  # Первичный ключ
    author_id = Column(Integer, ForeignKey('authors.author_id'))  # Внешний ключ к автору
    news_id = Column(Integer, ForeignKey('news.news_id'))  # Внешний ключ к новости
    datetime = Column(DateTime, default=datetime.utcnow)  # Дата и время комментария
    comment = Column(String)  # Текст комментария


# Модель UserArticleInteraction, представляющая взаимодействия пользователей со статьями
class UserArticleInteraction(Base):
    __tablename__ = 'user_article_interactions'
    id = Column(Integer, primary_key=True)  # Первичный ключ
    user_id = Column(Integer, ForeignKey('authors.author_id'))  # Внешний ключ к пользователю
    news_id = Column(Integer, ForeignKey('news.news_id'))  # Внешний ключ к новости
    interaction_type = Column(String)  # Тип взаимодействия ('like', 'dislike', 'save')
    timestamp = Column(DateTime, default=datetime.utcnow)  # Время взаимодействия


# Модель Portal, представляющая информацию о портале в базе данных
class Portal(Base):
    __tablename__ = "portal"
    id = Column(Integer, primary_key=True)  # Первичный ключ
    name = Column(String(150), nullable=False, default='')  # Название портала
    redactor_name = Column(String(150), default="")  # Имя редактора
    address = Column(String(150), default="")  # Адрес
    email = Column(String(150), default="")  # Электронная почта
    number = Column(String(150), default="")  # Номер телефона
    registration_number = Column(String(150), default="")  # Регистрационный номер
    integration_email = Column(String(150), default="")  # Email для интеграций
    social_link1 = Column(String(150), default="")  # Социальная ссылка 1
    social_link2 = Column(String(150), default="")  # Социальная ссылка 2

    # Отношение один-ко-многим с категориями
    categories = relationship("Categories", back_populates="portal")


# Модель Categories, представляющая категории новостей в базе данных
class Categories(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True)  # Первичный ключ
    categories_name = Column(String(100), nullable=False, default='')  # Название категории
    portal_id = Column(Integer, ForeignKey("portal.id"))  # Внешний ключ к порталу

    # Отношение многие-к-одному с порталом
    portal = relationship("Portal", back_populates="categories")

    # Отношение один-ко-многим с новостями
    news = relationship("News", back_populates="category")


# Функция инициализации базы данных
def init_db():
    from database import engine
    Base.metadata.create_all(bind=engine)  # Создание всех таблиц
    db_session.commit()  # Фиксация изменений


# Функция для печати схемы таблицы
def print_schema(table_class):
    from sqlalchemy.schema import CreateTable, CreateColumn
    print(str(CreateTable(table_class.__table__).compile(db_engine)))


# Функция для печати колонок таблицы
def print_columns(table_class, *attrNames):
    from sqlalchemy.schema import CreateTable, CreateColumn
    c = table_class.__table__.c
    print(',\r\n'.join((str(CreateColumn(getattr(c, attrName)).compile(db_engine))
                        for attrName in attrNames if hasattr(c, attrName)
                        )))


# Главная точка входа для инициализации базы данных
if __name__ == "__main__":
    init_db()

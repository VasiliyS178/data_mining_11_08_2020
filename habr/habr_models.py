from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table
)

Base = declarative_base()

tag_post = Table('tag_post', Base.metadata,
                 Column('post_id', Integer, ForeignKey('post.id')),
                 Column('tag_id', Integer, ForeignKey('tag.id'))
                 )

hab_post = Table('hab_post', Base.metadata,
                 Column('post_id', Integer, ForeignKey('post.id')),
                 Column('hab_id', Integer, ForeignKey('hab.id'))
                 )


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    writer_id = Column(Integer, ForeignKey('writer.id'))
    writer = relationship("Writer", back_populates='post')
    tag = relationship('Tag', secondary=tag_post, back_populates='post')
    hab = relationship('Hab', secondary=hab_post, back_populates='post')

    def __init__(self, title: str, url: str, writer, tags: list = None, habs: list = None):
        self.title = title
        self.url = url
        self.writer = writer
        if tags:
            self.tag.extend(tags)
        if habs:
            self.hab.extend(habs)


class Writer(Base):
    __tablename__ = 'writer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    post = relationship("Post", back_populates='writer')

    def __init__(self, name, url, username):
        self.name = name
        self.url = url
        self.username = username


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    post = relationship('Post', secondary=tag_post, back_populates='tag')

    def __init__(self, name, url):
        self.name = name
        self.url = url


class Hab(Base):
    __tablename__ = 'hab'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    post = relationship('Post', secondary=hab_post, back_populates='hab')

    def __init__(self, name, url):
        self.name = name
        self.url = url
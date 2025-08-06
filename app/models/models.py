from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, Float
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Exhibition(Base):
    __tablename__ = 'exhibition'
    exhibition_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50))
    image_url = Column(String(255))

    galleries = relationship('Gallery', back_populates='exhibition', cascade="all, delete")

class Gallery(Base):
    __tablename__ = 'gallery'
    gallery_id = Column(Integer, primary_key=True, index=True)
    exhibition_id = Column(Integer, ForeignKey('exhibition.exhibition_id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    image_url = Column(String(255))

    exhibition = relationship('Exhibition', back_populates='galleries')
    artifacts = relationship('Artifact', back_populates='gallery', cascade="all, delete")

class Artifact(Base):
    __tablename__ = 'artifact'
    artifact_id = Column(Integer, primary_key=True, index=True)
    gallery_id = Column(Integer, ForeignKey('gallery.gallery_id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    x_coord = Column(Float)
    y_coord = Column(Float)
    image_url = Column(String(255))

    gallery = relationship('Gallery', back_populates='artifacts')
    explanations = relationship('ArtifactExplanation', back_populates='artifact', cascade="all, delete")
    questions = relationship('Question', back_populates='artifact', cascade="all, delete")
    faqs = relationship('FAQ', back_populates='artifact', cascade="all, delete")
    user_artworks = relationship('UserArtwork', back_populates='artifact', cascade="all, delete")

class ArtifactExplanation(Base):
    __tablename__ = 'artifact_explanation'
    explanation_id = Column(Integer, primary_key=True, index=True)
    artifact_id = Column(Integer, ForeignKey('artifact.artifact_id', ondelete='CASCADE'), nullable=False)
    explanation_text = Column(Text)
    explanation_audio_key = Column(String(255))

    artifact = relationship('Artifact', back_populates='explanations')

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, index=True)
    language_preference = Column(String(50))
    created_at = Column(TIMESTAMP, nullable=False)

    artworks = relationship('UserArtwork', back_populates='user', cascade="all, delete")

class UserArtwork(Base):
    __tablename__ = 'user_artwork'
    artwork_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    artifact_id = Column(Integer, ForeignKey('artifact.artifact_id', ondelete='CASCADE'), nullable=False)
    image_url = Column(String(255))
    qr_code_url = Column(String(255))
    created_at = Column(TIMESTAMP, nullable=False)

    user = relationship('User', back_populates='artworks')
    artifact = relationship('Artifact', back_populates='user_artworks')

class Question(Base):
    __tablename__ = 'question'
    question_id = Column(Integer, primary_key=True, index=True)
    artifact_id = Column(Integer, ForeignKey('artifact.artifact_id', ondelete='CASCADE'), nullable=False)
    question_text = Column(Text)
    answer_text = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False)

    artifact = relationship('Artifact', back_populates='questions')

class FAQ(Base):
    __tablename__ = 'faq'
    faq_id = Column(Integer, primary_key=True, index=True)
    artifact_id = Column(Integer, ForeignKey('artifact.artifact_id', ondelete='CASCADE'), nullable=False)
    question_text = Column(Text)
    answer_text = Column(Text)

    artifact = relationship('Artifact', back_populates='faqs')

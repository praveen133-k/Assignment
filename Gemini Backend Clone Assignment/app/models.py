from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, func
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSONB
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    mobile = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    otp = Column(String(6), nullable=True)
    otp_created_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    stripe_customer_id = Column(String, nullable=True)
    subscription = relationship('Subscription', back_populates='user', uselist=False)
    chatrooms = relationship('Chatroom', back_populates='user')

class Chatroom(Base):
    __tablename__ = 'chatrooms'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now())
    user = relationship('User', back_populates='chatrooms')
    messages = relationship('Message', back_populates='chatroom')

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    chatroom_id = Column(Integer, ForeignKey('chatrooms.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    content = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    chatroom = relationship('Chatroom', back_populates='messages')
    user = relationship('User')

class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    tier = Column(String, default='basic')  # 'basic' or 'pro'
    stripe_subscription_id = Column(String, nullable=True)
    status = Column(String, default='inactive')
    started_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    user = relationship('User', back_populates='subscription') 
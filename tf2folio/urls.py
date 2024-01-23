from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_item", views.new_item, name="new_item"),
    path("new_trade", views.new_trade, name="new_trade"),
    path("register_item", views.register_item, name="register_item"),
    path("get_item_html/<int:item_id>", views.get_item_html, name="get_item_html"),
    path("register_trade", views.register_trade, name="register_trade"),
    path("trade_history", views.trade_history, name="trade_history"),
    path("item_trade_history/<int:item_id>", views.item_trade_history, name="item_trade_history"),
]
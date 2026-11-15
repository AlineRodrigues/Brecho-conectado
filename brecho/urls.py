from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("vendas/registrar/", views.registrar_venda, name="registrar_venda"),
    path(
        "vendas/<int:venda_id>/sucesso/",
        views.venda_sucesso,
        name="venda_sucesso",
    ),
]

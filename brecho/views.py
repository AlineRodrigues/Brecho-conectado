from django.shortcuts import render


def inicio(request):
    return render(request, "brecho/inicio.html")

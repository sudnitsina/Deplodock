# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ScopedTokenForm
from .models import Token, InventoryToken


@login_required(login_url="/login")
def main(request):
    try:
        token = Token.objects.get(user=request.user).key
    except Token.DoesNotExist:
        token = ''
    if request.method == 'POST':
        if token != '':
            Token.objects.get(user=request.user).delete()
        token = Token(user=request.user)
        token.save()
        return redirect('main')
    lst = InventoryToken.objects.filter(user=request.user)
    return render(request, 'authtoken/token.html', {'token': token, "list": lst})


@login_required(login_url="/login")
def scoped(request):
    if request.method == "POST":
        form = ScopedTokenForm(request.POST, user=request.user)
        if form.is_valid():
            new_token = form.save(commit=False)
            new_token.user = request.user
            new_token.save()
            form.save_m2m()
            return redirect('main')
    else:
            form = ScopedTokenForm(user=request.user)
    return render(request, 'authtoken/scopedtoken.html', {'form': form})


@login_required(login_url="/login")
def scoped_edit(request, token):
    token = get_object_or_404(InventoryToken, token=token, user=request.user)
    if request.method == "POST":
        form = ScopedTokenForm(request.POST, instance=token, user=request.user)
        if form.is_valid():
            token = form.save(commit=False)
            token.user = request.user
            token.save()
            form.save_m2m()
            return redirect('main')
    else:
        form = ScopedTokenForm(instance=token, user=request.user)
    return render(request, 'authtoken/scopedtoken.html', {'form': form})


@login_required(login_url="/login")
def scoped_delete(request, token):
    token = get_object_or_404(InventoryToken, token=token, user=request.user)
    token.delete()
    return redirect('main')


@login_required(login_url="/login")
def token_delete(request, token):
    token = get_object_or_404(Token, key=token, user=request.user)
    token.delete()
    return redirect('main')

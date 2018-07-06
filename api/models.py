# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core import validators
from django.db import models


class LimitError(Exception):
    pass


class Inventory(models.Model):
    inventory = models.CharField(
        max_length=256,
        validators=[validators.RegexValidator(r'^[A-Za-z0-9-_.:]+$')])
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('inventory', 'user')
        ordering = ['inventory']

    def __str__(self):
        return self.inventory


class Group(models.Model):
    group = models.CharField(
                max_length=256,
                validators=[validators.RegexValidator(r'^[A-Za-z0-9-_.:]+$')])
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)

    def __str__(self):
        return self.group

    class Meta:
        unique_together = ('group', 'inventory')
        ordering = ['group']


class Variable(models.Model):
    variable = models.CharField(
        max_length=256,
        validators=[validators.RegexValidator(r'^[A-Za-z0-9-_.:]+$')])
    value = models.TextField(blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return self.variable

    class Meta:
        unique_together = ('group', 'variable')
        ordering = ['variable']


class Machine(models.Model):
    machine = models.CharField(
        max_length=256,
        validators=[validators.RegexValidator(r'^[A-Za-z0-9-_.:]+$')])
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.machine

    class Meta:
        unique_together = ('machine', 'user')
        ordering = ['machine']


class HostVariable(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    host = models.ForeignKey(Machine, on_delete=models.CASCADE)
    variable = models.CharField(
        max_length=256,
        validators=[validators.RegexValidator(r'^[A-Za-z0-9-_.:]+$')])
    value = models.TextField(blank=True)

    def __str__(self):
        return self.variable

    class Meta:
        unique_together = ('inventory', 'host', 'variable')
        ordering = ['variable']


class Host(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    host = models.ForeignKey(Machine, on_delete=models.CASCADE)

    def __str__(self):
        return self.host.machine

    class Meta:
        unique_together = ('group', 'host')
        ordering = ['host']


class Child(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='parent')
    child = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='child')

    def __str__(self):
        return self.child.group

    class Meta:
        unique_together = ('group', 'child')
        ordering = ['child']

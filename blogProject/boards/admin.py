# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Board, Topic, Post, Action
from django.contrib import admin

# Register your models here.
admin.site.register(Board)
admin.site.register(Topic)
admin.site.register(Post)
admin.site.register(Action)

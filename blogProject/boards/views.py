# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from .forms import NewTopicForm, PostForm, NewBoardForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Board, Topic, Post
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.template.loader import render_to_string


# Create your views here.


class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'


@login_required
def new_board(request):
    if request.method == 'POST':
        form = NewBoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.creater = request.user
            board.save()
            return redirect('home')
    else:
        form = NewBoardForm()
    return render(request, 'new_board.html', {'form': form})


def board_topics(request, pk):

    board = get_object_or_404(Board, pk=pk)
    queryset = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 20)
    try:
        topics = paginator.page(page)
    except PageNotAnInteger:
        # fallback to the first page
        topics = paginator.page(1)
    except EmptyPage:
        # probably the user tried to add a page number
        # in the url, so we fallback to the last page
        topics = paginator.page(paginator.num_pages)

    return render(request, 'topics.html', {'board': board, 'topics': topics})


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()

            topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=int(topic.get_page_count())
            )

            return redirect(topic_post_url)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


@login_required
def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        data = dict()
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()

            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False

        context = {'post': post}

        data['html_form'] = render_to_string('includes/post.html',
                                             context=context,
                                             request=request)
        return JsonResponse(data)
            # topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            # topic_post_url = '{url}?page={page}#{id}'.format(
            #     url=topic_url,
            #     id=post.pk,
            #     page=int(topic.get_page_count())
            # )

    else:
        form = PostForm()
    return render(request, 'topic_posts.html', {'topic': topic, 'form': form})


class NewPostView(CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('post_list')
    template_name = 'new_post.html'


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super(PostUpdateView, self).get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super(TopicListView, self).get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset

# CBV for topic_posts
# class PostListView(ListView):
#     model = Post
#     context_object_name = 'posts'
#     template_name = 'topic_posts.html'
#
#     paginate_by = 20
#
#     def get_context_data(self, **kwargs):
#
#         session_key = 'viewed_topic_{}'.format(self.topic.pk)  # <-- here
#         if not self.request.session.get(session_key, False):
#             self.topic.views += 1
#             self.topic.save()
#             self.request.session[session_key] = True           # <-- until here
#
#         kwargs['topic'] = self.topic
#         return super(PostListView, self).get_context_data(**kwargs)
#
#     def get_queryset(self):
#         self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
#         queryset = self.topic.posts.order_by('created_at')
#         return queryset
#
#     def form_valid(self, form):
#         self.post = form.save(commit=False)
#         self.post.topic = self.topic
#         self.post.created_by = self.request.user
#         self.post.save()
#
#         self.topic.last_updated = timezone.now()
#         self.topic.save()
#         return redirect('topic_posts', pk=self.post.topic.board.pk, topic_pk=self.post.topic.pk)

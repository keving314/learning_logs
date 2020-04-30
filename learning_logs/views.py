from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, Entry
from .forms import TopicForm, EntryForm
from django.contrib.auth.decorators import login_required
from django.http import Http404

import pytz
from django.utils import timezone

# Create your views here.

def index(request):
    """Home Page"""
    return render(request, 'learning_logs/index.html')

@login_required
def topics(request):
    """shows topics"""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics':topics}
    return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    """show a single topic and all it's entries"""
    #topic = Topic.objects.get(id=topic_id)
    #tries to get Topic object, if fails, we get a 500 error
    topic = get_object_or_404(Topic, id=topic_id)
    #make sure the topic belongs to the correct user
    if topic.owner != request.user:
        raise Http404
    #we can use 'blah'_set when we have a fk relationship, the - reverses the order
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic':topic,'entries':entries}
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    """Adds a new topic"""
    if request.method != 'POST':
        #no data submitted create a blank form
        form = TopicForm()
    else:
        #Data submitted; process it
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')

    #display a blank or invalid form
    context = {'form':form}
    return render(request, 'learning_logs/new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    """adds a new entry for a specific topic"""
    topic = Topic.objects.get(pk=topic_id)

    if request.method != 'POST':
        form = EntryForm()

    else:
        form = EntryForm(data= request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id = topic_id)

    context = {'topic':topic, 'form':form}
    return render(request, 'learning_logs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """edit existing entry"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        #initial request, fill form with the current entry
        form = EntryForm(instance=entry)

    else:
        #the edited entries post data has been submitted, process
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id = topic.id)

    context = {'entry': entry, 'topic': topic, 'form':form}

    return render(request, 'learning_logs/edit_entry.html', context)

from django.shortcuts import render, redirect
from .models import TweetModel, TweetComment
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, TemplateView

# Create your views here.

def home(request):
    user = request.user.is_authenticated
    if user:
        return redirect('/tweet')
    else:
        return redirect('/sign-in')

def tweet(request):
    if request.method == 'GET':
        user = request.user.is_authenticated
        if user:
            all_tweet = TweetModel.objects.all().order_by('-created_at')
            return render(request, 'tweet/home.html', {'tweet': all_tweet})
        else:
            return redirect('/sign-in')
    elif request.method == 'POST':
        user = request.user
        content = request.POST.get('my-content','')
        tags = request.POST.get('tag','').split(',')

        if content == '':
            all_tweet = TweetModel.objects.all().order_by('-created_at')
            return render(request, 'tweet/home.html', {'error':'글은 공백일 수 없습니다.', 'tweet': all_tweet})
        else:
            my_tweet = TweetModel.objects.create(author=user, content=content)
            for tag in tags:
                tag = tag.strip()
                if tag != '':
                    my_tweet.tags.add(tag)
            my_tweet.save()
            return redirect('/tweet')

class TagCloudTV(TemplateView):
    template_name = 'taggit/tag_cloud_view.html'


class TaggedObjectLV(ListView):
    template_name = 'taggit/tag_with_post.html'
    model = TweetModel

    def get_queryset(self):
        return TweetModel.objects.filter(tags__name=self.kwargs.get('tag'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tagname'] = self.kwargs['tag']
        return context

@login_required
def delete_tweet(request, id):
    my_tweet = TweetModel.objects.get(id=id)
    my_tweet.delete()
    return redirect('/tweet')

def detail_tweet(request,id):
    if request.method == 'GET':
        tweet = TweetModel.objects.get(id=id)
        comment = TweetComment.objects.filter(tweet=id)
        return render(request, 'tweet/tweet_detail.html', {'tweet':tweet, 'comment':comment})

def write_comment(request,id):
    if request.method == 'POST':
        user = request.user
        comment = TweetComment()
        comment.tweet = TweetModel.objects.get(id=id)
        comment.author = user
        comment.comment = request.POST.get('comment')
        comment.save()
        return redirect(f'/tweet/{id}')

def delete_comment(request, id):
    delete_comment = TweetComment.objects.get(id=id)
    tweet_id = delete_comment.tweet_id
    delete_comment.delete()

    return redirect(f'/tweet/{tweet_id}')
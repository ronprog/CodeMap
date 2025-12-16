from django.shortcuts import render
from django.core.paginator import Paginator
from CodeMap.models import Question, Answer, Tag, QuestionLike, AnswerLike
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from CodeMap.models import User, Profile
from django.core.exceptions import ValidationError
from django.contrib import messages

class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        
        if not email:
            raise forms.ValidationError("Email is required.")
        
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        
        return email
    
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

def signup(request, *args, **kwargs):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return render(request, "settings.html", {"form": form})
    
    return render(request, "signup.html", context={"popular_tags": popular_tags(), "form": form})

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile 
        fields = ['avatar']

@login_required
def sett(request):
    user = request.user
    profile = user.profile
    
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('settings')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)
    
    return render(request, "settings.html", {
        'user_form': user_form,
        'profile_form': profile_form
    })

def log_in(request, *args, **kwargs):
    form = AuthenticationForm(request=request)
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)

        if form.is_valid():
            login(request, form.get_user())
            return redirect('index')
    
    return render(request, "login.html", context={"popular_tags": popular_tags(), 'form': form})

def log_out(request):
    logout(request)
    return redirect('index')

def popular_tags():
    return Tag.objects.annotate(num_questions=Count('question')).order_by('-num_questions')[:20]


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import AnswerForm
from django.urls import reverse

def question(request, id):
    question_obj = get_object_or_404(Question, id=id)
    
    answers_list = Answer.objects.filter(question=question_obj)
    answers_with_reaction = []
    
    for answer in answers_list:
        user_reaction = 0
        if request.user.is_authenticated:
            try:
                like = AnswerLike.objects.get(user=request.user, answer=answer)
                user_reaction = like.value
            except AnswerLike.DoesNotExist:
                pass
        answers_with_reaction.append({
            'obj': answer,
            'user_reaction': user_reaction
        })
    
    user_reaction_question = 0
    if request.user.is_authenticated:
        try:
            like = QuestionLike.objects.get(user=request.user, question=question_obj)
            user_reaction_question = like.value
        except QuestionLike.DoesNotExist:
            pass
    
    answer_form = AnswerForm(request.POST if request.method == 'POST' and 'content' in request.POST else None)
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            if 'content' in request.POST:
                if answer_form.is_valid():
                    answer = answer_form.save(commit=False)
                    answer.author = request.user
                    answer.question = question_obj
                    answer.save()
                    
                    messages.success(request, "✅ Ваш ответ успешно добавлен!")
                    
                    return redirect(reverse('question', kwargs={'id': id}))
                else:
                    for field, errors in answer_form.errors.items():
                        for error in errors:
                            messages.error(request, f"Ошибка: {error}")
                    
                    
            elif 'answer_id' in request.POST:
                answer_id = request.POST.get('answer_id')
                answer = get_object_or_404(Answer, id=answer_id)
                if request.user == question_obj.author:
                    answer.is_correct = not answer.is_correct
                    answer.save()
                    messages.info(request, "Ответ отмечен как правильный!" if answer.is_correct else "Ответ снят с отметки правильного")
        
        return redirect(reverse('question', kwargs={'id': id}))
    
    context = {
        'question': question_obj,
        'answers': answers_with_reaction,
        'user_reaction_question': user_reaction_question,
        'popular_tags': popular_tags(),
        'answer_form': answer_form,
    }
    
    return render(request, 'question.html', context)
def index(request):
    questions = Question.objects.all().order_by('-created_date')
    paginator = Paginator(questions, per_page=3)

    try:
        page = request.GET.get("page", 1)
        question_page = paginator.page(page)
        return render(request, "index.html", context={"questions_page": question_page, "popular_tags": popular_tags()})
    except:
        raise Http404('')

def hot(request):
    questions = Question.objects.all().order_by('-rating')
    paginator = Paginator(questions, per_page=3)
    
    try:
        page = request.GET.get("page", 1)
        question_page = paginator.page(page)
        return render(request, "hot.html", context={"questions_page": question_page, "popular_tags": popular_tags()})
    except:
        raise Http404('')

def tag(request, *args, **kwargs):
    tag_name = kwargs.get('tag')
    questions = Question.objects.filter(tags__name=tag_name).order_by('-rating')
    paginator = Paginator(questions, per_page=3)
    
    try:
        page = request.GET.get("page", 1)
        question_page = paginator.page(page)
        return render(request, "tag.html", context={
            "questions_page": question_page,
            "tag": tag_name,
            "popular_tags": popular_tags()
        })
    except:
        raise Http404()

@login_required
def ask(request):
    error_messages = {}
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        tags_input = request.POST.get('tags', '').strip()
        
        if not title:
            error_messages['title'] = 'Заголовок обязателен'
        elif len(title) > 100:
            error_messages['title'] = 'Заголовок не должен превышать 100 символов'
        
        if not content:
            error_messages['content'] = 'Текст вопроса обязателен'
        elif len(content) > 5000:
            error_messages['content'] = 'Текст вопроса не должен превышать 5000 символов'
        
        tags = []
        if tags_input:
            raw_tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            if len(raw_tags) > 3:
                error_messages['tags'] = 'Можно указать не более 3 тегов'
            else:
                tags = raw_tags
        
        if not error_messages:
            question = Question.objects.create(
                title=title,
                content=content,
                author=request.user
            )
            
            for tag_name in tags[:3]:
                tag_obj, created = Tag.objects.get_or_create(name=tag_name.lower())
                question.tags.add(tag_obj)
            
            return redirect('question', id=question.id)
        
        return render(request, 'ask.html', {
            'error_messages': error_messages,
            'title': title,
            'content': content,
            'tags_input': tags_input
        })
    
    return render(request, 'ask.html')

def custom_404(request, exception):
    context = {
        'error_message': 'Страница не найдена',
        'exception': str(exception)
    }
    return render(request, '404.html', context, status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

def custom_400(request, exception):
    return render(request, '400.html', status=400)

@login_required
def like_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    try:
        like = QuestionLike.objects.get(user=request.user, question=question)
        like.delete()
    except QuestionLike.DoesNotExist:
        QuestionLike.objects.create(
            user=request.user,
            question=question,
            value=1
        )
    
    question.update_rating()
    return redirect('question', id=question_id)

@login_required
def like_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    
    try:
        like = AnswerLike.objects.get(user=request.user, answer=answer)
        like.delete()
    except AnswerLike.DoesNotExist:
        AnswerLike.objects.create(
            user=request.user,
            answer=answer,
            value=1
        )
    
    answer.update_rating()
    return redirect('question', id=answer.question.id)

# views.py
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render

def search(request):
    query = request.GET.get('q', '').strip()
    search_results = []
    
    if query:
        search_results = Question.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(answers__content__icontains=query)
        ).distinct().order_by('-rating', '-created_date')
    
    paginator = Paginator(search_results, per_page=5)
    page = request.GET.get('page', 1)
    
    try:
        results_page = paginator.page(page)
    except:
        results_page = paginator.page(1)
    
    context = {
        'search_query': query,
        'results_page': results_page,
        'results_count': search_results.count(),
        'popular_tags': popular_tags(),
    }
    
    return render(request, 'search.html', context)
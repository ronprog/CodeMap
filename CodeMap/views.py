from django.shortcuts import render
from django.core.paginator import Paginator
from CodeMap.models import Question, Answer , Tag ,QuestionLike, AnswerLike
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404

Lorem = "Lorem ipsum dolor sit amet lo consectetur adipisicing elit. Dolorem hic dicta saepe dolores assumenda quisquam perspiciatis odio pariatur voluptates commodi magni eos illum sequi dignissimos id, molestiae debitis ratione. Ad! Lorem ipsum dolor sit amet consectetur adipisicing elit. Accusantium ab earum porro et? Nihil sunt, veritatis aliquid, voluptas, excepturi exercitationem obcaecati omnis repudiandae rerum assumenda dolorem placeat porro? Repellat, atque."


def popular_tags():

    
    return Tag.objects.annotate(num_questions=Count('question')).order_by('-num_questions')[:20]

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
    
  
    if request.method == 'POST':
        if request.user.is_authenticated:
            if 'content' in request.POST:  
                content = request.POST.get('content')
                if content:
                    Answer.objects.create(
                        content=content,
                        author=request.user,
                        question=question_obj
                    )
            elif 'answer_id' in request.POST:  
                answer_id = request.POST.get('answer_id')
                answer = get_object_or_404(Answer, id=answer_id)
                if request.user == question_obj.author:
                    answer.is_correct = not answer.is_correct
                    answer.save()
        
        return redirect('question', id=id)
    
    context = {
        'question': question_obj,
        'answers': answers_with_reaction,
        'user_reaction_question': user_reaction_question,
        'popular_tags': popular_tags(),
    }
    
    return render(request, 'question.html', context)
    
    

def index(request ):
    questions = Question.objects.all().order_by('-created_date')  
    paginator = Paginator(questions, per_page=3 ) 

    try:
        
        
        page = request.GET.get("page",1)
        question_page = paginator.page(page)
        return render(request, "index.html", context={"questions_page" : question_page, "popular_tags" : popular_tags()})
    except:
        raise Http404('')
    



def hot(request ):
    
    questions = Question.objects.all().order_by('-rating')  
    paginator = Paginator(questions, per_page=3 ) 
    try:
            
        page = request.GET.get("page",1)
        question_page = paginator.page(page)

        
        return render(request, "hot.html", context={"questions_page" : question_page, "popular_tags" : popular_tags()})
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

def login(request , *args, **kwargs):
    
    return render(request, "login.html" ,context={ "popular_tags" : popular_tags()} )

def signup(request , *args, **kwargs):
    
    return render(request, "signup.html" ,context={ "popular_tags" : popular_tags()} )




@login_required
def ask(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        tags_input = request.POST.get('tags', '')
        
        if not title or not content:
            return render(request, 'ask.html', {
                'error': 'Заголовок и текст вопроса обязательны'
            })
        
        question = Question.objects.create(
            title=title,
            content=content,
            author=request.user
        )
        
        if tags_input:
            tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            for tag_name in tags[:3]:
                tag = Tag.objects.get_or_create(name=tag_name.lower())
                question.tags.add(tag)
        
      
        return redirect('question', id=question.id)
    
    return render(request, 'ask.html')

def sett(request , *args, **kwargs):
    
    return render(request, "settings.html" ,context={ "popular_tags" : popular_tags()} )
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
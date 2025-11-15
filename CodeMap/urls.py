
from django.contrib import admin
from django.urls import path
from CodeMap.views import  question,index ,hot, tag,login , signup,ask ,sett , like_question ,like_answer
from django.conf import settings
from django.conf.urls.static import static


urlpatterns1 = [

    path("question/<int:id>/", question, name='question'),
    path("", index, name = "index"),
    path("hot/", hot, name = "hot"),
    path("tag/<str:tag>/", tag, name = "tag"),
    path("login/", login , name = "login"),
    path("signup/", signup, name = "signup"),
    path("ask/", ask, name = "ask"),
    path("settings/", sett, name = "settings"),
    path("question/<int:question_id>/like/", like_question, name="like_question"),
    path("answer/<int:answer_id>/like/", like_answer, name="like_answer"),


    
   
] 

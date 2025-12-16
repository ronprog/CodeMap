
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)
    
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class QuestionManager(models.Manager):
    def new_questions(self):
        return self.order_by('-created_date')
    
    def best_questions(self):
        return self.order_by('-rating')
    
    def by_tag(self, tag_name):
        return self.filter(tags__name=tag_name).order_by('-rating')

class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True )
    
    objects = QuestionManager()
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f"/question/{self.pk}/"
    
    def update_rating(self):
        likes = QuestionLike.objects.filter(question=self)
        self.rating = sum(like.value for like in likes)
        self.save()
    
    def answers_count(self):
        return self.answers.count()
    
    class Meta:
        ordering = ['-created_date']

class AnswerManager(models.Manager):
    def for_question(self, question):
        return self.filter(question=question).order_by('-rating', '-created_date')

class Answer(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    created_date = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)
    
    objects = AnswerManager()
    
    def __str__(self):
        return f"Answer to {self.question.title}"
    
    def update_rating(self):
        likes = AnswerLike.objects.filter(answer=self)
        self.rating = sum(like.value for like in likes)
        self.save()
    
    class Meta:
        ordering = ['-rating', '-created_date']

class QuestionLike(models.Model):
    LIKE = 1
    DISLIKE = -1
    VALUE_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'question']
    
    def __str__(self):
        action = "liked" if self.value == self.LIKE else "disliked"
        return f"{self.user.username} {action} {self.question.title}"

class AnswerLike(models.Model):
    LIKE = 1
    DISLIKE = -1
    VALUE_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'answer']
    
    def __str__(self):
        action = "liked" if self.value == self.LIKE else "disliked"
        return f"{self.user.username} {action} answer {self.answer.id}"
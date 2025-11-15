from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from CodeMap.models import Question, Answer, Tag, Profile, QuestionLike, AnswerLike
import random
from django.db import transaction
from django.db.models import Sum

class Command(BaseCommand):
    help = 'Fill database with test data'
    
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Ratio coefficient')

    def handle(self, *args, **options):
        ratio = options['ratio']
        
        self.stdout.write(f"Starting with ratio: {ratio}")
        
    
        with transaction.atomic():
        
            self.stdout.write(f"Creating {ratio} users...")
            users_data = []
            for i in range(ratio):
                users_data.append(User(
                    username=f'user_{i}',
                    email=f'user_{i}@example.com',
                    password='testpass123'
                ))
            
            users = User.objects.bulk_create(users_data, batch_size=1000)
            self.stdout.write(f"Created {len(users)} users")
            
          
            profiles_data = [Profile(user=user) for user in users]
            Profile.objects.bulk_create(profiles_data, batch_size=1000)
            
           
            self.stdout.write(f"Creating {ratio} tags...")
            tags = []
            for i in range(ratio):
                tag, created = Tag.objects.get_or_create(name=f'tag_{i}')
                tags.append(tag)
            
            self.stdout.write(f"Created/retrieved {len(tags)} tags")
            
            
            questions_count = ratio * 10
            self.stdout.write(f"Creating {questions_count} questions...")
            questions_data = []
            for i in range(questions_count):
                questions_data.append(Question(
                    title=f'Question {i} - {random.choice(["Help needed", "Problem with", "How to", "Best way to"])}',
                    content=f'This is the content for question {i}. ' * 10,
                    author=random.choice(users),
                    rating=random.randint(0, 100)
                ))
            
            questions = Question.objects.bulk_create(questions_data, batch_size=1000)
            self.stdout.write(f"Created {len(questions)} questions")
            
            
            self.stdout.write("Adding tags to questions...")
            for question in questions:
                question_tags = random.sample(tags, min(3, len(tags)))
                question.tags.add(*question_tags)
            
 
            answers_count = ratio * 100
            self.stdout.write(f"Creating {answers_count} answers...")
            answers_data = []
            for i in range(answers_count):
                answers_data.append(Answer(
                    content=f'This is answer {i} for the question. ' * 5,
                    author=random.choice(users),
                    question=random.choice(questions),
                    rating=random.randint(0, 50),
                    is_correct=random.choice([True, False]) if i % 10 == 0 else False
                ))
            
            answers = Answer.objects.bulk_create(answers_data, batch_size=1000)
            self.stdout.write(f"Created {len(answers)} answers")
            
        
            likes_count = ratio * 200
            self.stdout.write(f"Creating {likes_count} user ratings...")
            
     
            question_likes_data = []
            question_likes_set = set()  
            
            for i in range(likes_count // 2):
                user = random.choice(users)
                question = random.choice(questions)
                key = (user.id, question.id)
                
                if key not in question_likes_set:
                    question_likes_set.add(key)
                    question_likes_data.append(QuestionLike(
                        user=user,
                        question=question,
                        value=random.choice([1, -1])
                    ))
                
                if len(question_likes_data) >= 1000:
                    QuestionLike.objects.bulk_create(question_likes_data, batch_size=1000)
                    question_likes_data = []
            
            if question_likes_data:
                QuestionLike.objects.bulk_create(question_likes_data, batch_size=1000)
            
     
            answer_likes_data = []
            answer_likes_set = set()
            
            for i in range(likes_count // 2):
                user = random.choice(users)
                answer = random.choice(answers)
                key = (user.id, answer.id)
                
                if key not in answer_likes_set:
                    answer_likes_set.add(key)
                    answer_likes_data.append(AnswerLike(
                        user=user,
                        answer=answer,
                        value=random.choice([1, -1])
                    ))
                
                if len(answer_likes_data) >= 1000:
                    AnswerLike.objects.bulk_create(answer_likes_data, batch_size=1000)
                    answer_likes_data = []
            
            if answer_likes_data:
                AnswerLike.objects.bulk_create(answer_likes_data, batch_size=1000)
        
        
        self.stdout.write("Updating ratings...")
        

        self._update_ratings_using_orm()
        
  
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'- Users: {User.objects.count()}\n'
                f'- Questions: {Question.objects.count()}\n'
                f'- Answers: {Answer.objects.count()}\n'
                f'- Tags: {Tag.objects.count()}\n'
                f'- Question likes: {QuestionLike.objects.count()}\n'
                f'- Answer likes: {AnswerLike.objects.count()}\n'
                f'- Total ratings: {QuestionLike.objects.count() + AnswerLike.objects.count()}'
            )
        )
    
    def _update_ratings_using_orm(self):
       
        questions = Question.objects.all()
        for question in questions.iterator(chunk_size=1000):
            total_rating = QuestionLike.objects.filter(
                question=question
            ).aggregate(total=Sum('value'))['total'] or 0
            Question.objects.filter(id=question.id).update(rating=total_rating)
        
       
        answers = Answer.objects.all()
        for answer in answers.iterator(chunk_size=1000):
            total_rating = AnswerLike.objects.filter(
                answer=answer
            ).aggregate(total=Sum('value'))['total'] or 0
            Answer.objects.filter(id=answer.id).update(rating=total_rating)
    
    def _update_ratings_using_sqlite(self):
       
        from django.db import connection
        
       
        with connection.cursor() as cursor:
            
            cursor.execute("""
                UPDATE CodeMap_question 
                SET rating = (
                    SELECT COALESCE(SUM(value), 0) 
                    FROM CodeMap_questionlike 
                    WHERE CodeMap_questionlike.question_id = CodeMap_question.id
                )
            """)
            
 
            cursor.execute("""
                UPDATE CodeMap_answer 
                SET rating = (
                    SELECT COALESCE(SUM(value), 0) 
                    FROM CodeMap_answerlike 
                    WHERE CodeMap_answerlike.answer_id = CodeMap_answer.id
                )
            """)
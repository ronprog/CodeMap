# CodeMap/management/commands/fill_db.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from CodeMap.models import Question, Answer, Tag, Profile, QuestionLike, AnswerLike
import random
from faker import Faker

class Command(BaseCommand):
    help = 'Fill database with test data according to ratio'
    
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Ratio coefficient for data generation')

    def handle(self, *args, **options):
        ratio = options['ratio']
        fake = Faker()
        
        self.stdout.write(f"Starting data generation with ratio: {ratio}")
        
        # 1. Создаем пользователей (ratio)
        self.stdout.write(f"Creating {ratio} users...")
        users = []
        for i in range(ratio):
            user = User.objects.create_user(
                username=f'user_{i}',
                email=f'user_{i}@example.com',
                password='testpass123'
            )
            Profile.objects.create(user=user)
            users.append(user)
            if i % 1000 == 0 and i > 0:
                self.stdout.write(f"Created {i} users...")
        
        # 2. Создаем теги (ratio)
        self.stdout.write(f"Creating {ratio} tags...")
        tags = []
        for i in range(ratio):
            tag_name = fake.word() + str(i)  # Уникальное имя тега
            tag = Tag.objects.create(name=tag_name)
            tags.append(tag)
            if i % 1000 == 0 and i > 0:
                self.stdout.write(f"Created {i} tags...")
        
        # 3. Создаем вопросы (ratio * 10)
        questions_count = ratio * 10
        self.stdout.write(f"Creating {questions_count} questions...")
        questions = []
        for i in range(questions_count):
            author = random.choice(users)
            question = Question.objects.create(
                title=fake.sentence()[:200],
                content=fake.text(max_nb_chars=500),
                author=author,
                rating=0  # Будет обновлен после создания лайков
            )
            
            # Добавляем случайные теги (1-3 тега на вопрос)
            question_tags = random.sample(tags, random.randint(1, 3))
            question.tags.set(question_tags)
            questions.append(question)
            
            if i % 10000 == 0 and i > 0:
                self.stdout.write(f"Created {i} questions...")
        
        # 4. Создаем ответы (ratio * 100)
        answers_count = ratio * 100
        self.stdout.write(f"Creating {answers_count} answers...")
        answers = []
        for i in range(answers_count):
            question = random.choice(questions)
            author = random.choice(users)
            answer = Answer.objects.create(
                content=fake.text(max_nb_chars=300),
                author=author,
                question=question,
                rating=0,  # Будет обновлен после создания лайков
                is_correct=random.choice([True, False]) if i % 10 == 0 else False
            )
            answers.append(answer)
            
            if i % 100000 == 0 and i > 0:
                self.stdout.write(f"Created {i} answers...")
        
        # 5. Создаем оценки пользователей (ratio * 200)
        likes_count = ratio * 200
        self.stdout.write(f"Creating {likes_count} user ratings...")
        
        # Лайки для вопросов
        for i in range(likes_count // 2):
            user = random.choice(users)
            question = random.choice(questions)
            
            # Проверяем, не существует ли уже такой лайк
            if not QuestionLike.objects.filter(user=user, question=question).exists():
                QuestionLike.objects.create(
                    user=user,
                    question=question,
                    value=random.choice([1, -1])
                )
            
            if i % 100000 == 0 and i > 0:
                self.stdout.write(f"Created {i} question likes...")
        
        # Лайки для ответов
        for i in range(likes_count // 2):
            user = random.choice(users)
            answer = random.choice(answers)
            
            if not AnswerLike.objects.filter(user=user, answer=answer).exists():
                AnswerLike.objects.create(
                    user=user,
                    answer=answer,
                    value=random.choice([1, -1])
                )
            
            if i % 100000 == 0 and i > 0:
                self.stdout.write(f"Created {i} answer likes...")
        
        # Обновляем рейтинги вопросов и ответов
        self.stdout.write("Updating ratings...")
        for question in questions:
            question.update_rating()
        
        for answer in answers:
            answer.update_rating()
        
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
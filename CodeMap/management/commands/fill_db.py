from django.core.management.base import BaseCommand
from CodeMap.models import QuestionLike, AnswerLike, Question, Answer
from django.db import transaction

class Command(BaseCommand):
    help = 'Clear all user reactions and reset ratings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        
        question_likes_count = QuestionLike.objects.count()
        answer_likes_count = AnswerLike.objects.count()
        total_reactions = question_likes_count + answer_likes_count
        
        if total_reactions == 0:
            self.stdout.write(
                self.style.SUCCESS('No reactions found in database')
            )
            return
        
        self.stdout.write("REACTIONS CLEANUP SUMMARY:")
        self.stdout.write(f"  - Question likes: {question_likes_count}")
        self.stdout.write(f"  - Answer likes: {answer_likes_count}")
        self.stdout.write(f"  - Total reactions: {total_reactions}")
        
        
        if not force:
            confirm = input(
                f"\nAre you sure you want to delete ALL reactions and reset ratings? "
                f"Type 'DELETE ALL' to continue: "
            )
            if confirm != 'DELETE ALL':
                self.stdout.write(self.style.WARNING('Deletion cancelled'))
                return
        
     
        with transaction.atomic():
            
            question_deleted, _ = QuestionLike.objects.all().delete()
            answer_deleted, _ = AnswerLike.objects.all().delete()
            
          
            questions_updated = Question.objects.all().update(rating=0)
            answers_updated = Answer.objects.all().update(rating=0)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully cleared all reactions and reset ratings:\n'
                    f'- Question likes deleted: {question_likes_count}\n'
                    f'- Answer likes deleted: {answer_likes_count}\n'
                    f'- Questions ratings reset: {questions_updated}\n'
                    f'- Answers ratings reset: {answers_updated}\n'
                    f'- Total objects affected: {question_deleted + answer_deleted + questions_updated + answers_updated}'
                )
            )
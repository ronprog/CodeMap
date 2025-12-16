# forms.py
from django import forms
from .models import Question, Tag

class AskForm(forms.ModelForm):
    tags = forms.CharField(
        max_length=100,
        help_text="Введите теги через запятую (максимум 3 тега)"
    )
    
    class Meta:
        model = Question
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
    
    def clean_tags(self):
        tags = self.cleaned_data['tags']
        tag_list = [tag.strip() for tag in tags.split(',')]
        if len(tag_list) > 3:
            raise forms.ValidationError("Можно указать не более 3 тегов")
        return tag_list
    
from django import forms
from .models import Question, Tag, Answer

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'my__answer__pole',
                'placeholder': 'Enter your answer...',
                'rows': 4,
                'maxlength': '5000'  # Максимальная длина 5000 символов
            }),
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        
        if not content:
            raise forms.ValidationError("Ответ не может быть пустым")
        
        if len(content) > 5000:
            raise forms.ValidationError("Ответ не должен превышать 5000 символов")
        
        if len(content) < 10:
            raise forms.ValidationError("Ответ должен содержать минимум 10 символов")
        
        return content
    
from django import forms

class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=100,
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'class': 'header__search',
            'placeholder': 'Search...',
            'id': 'searchInput'
        })
    )
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
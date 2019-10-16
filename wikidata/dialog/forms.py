from django import forms

class dialogForm(forms.Form):

    search = forms.CharField(label='',
        max_length=100,
        required=True,
        widget=forms.TextInput({
            'id': 'post-search-query',
            'class': 'form-control',
            'type': 'search',
            'placeholder': 'Type a question',
            })
        )
from django import forms
from .models import Ad, ExchangeProposal
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'image_url', 'category', 'condition']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Название товара')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Подробное описание товара')
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/image.jpg'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'condition': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'title': _('Название'),
            'description': _('Описание'),
            'image_url': _('Ссылка на изображение'),
            'category': _('Категория'),
            'condition': _('Состояние'),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise ValidationError(_('Название слишком короткое (минимум 5 символов)'))
        return title

    def clean_description(self):
        description = self.cleaned_data['description']
        if len(description) < 20:
            raise ValidationError(_('Описание слишком короткое (минимум 20 символов)'))
        return description


class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Напишите сообщение владельцу (необязательно)')
            }),
        }
        labels = {
            'comment': _('Комментарий'),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.request:
            # Проверка, что у пользователя есть объявления для обмена
            if not Ad.objects.filter(user=self.request.user).exists():
                raise ValidationError(_('У вас нет объявлений для обмена'))
        return cleaned_data


class ExchangeProposalStatusForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'status': _('Изменить статус'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ограничиваем выбор статусов для получателя предложения
        if self.instance and self.instance.status == 'pending':
            self.fields['status'].choices = [
                ('accepted', _('Принять')),
                ('rejected', _('Отклонить')),
            ]
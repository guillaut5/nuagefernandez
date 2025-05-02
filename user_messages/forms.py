from django import forms
from django.contrib.auth.models import User
from .models import Message, Group
from .models import Group


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        label="Confirmez le mot de passe", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("username", "email")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data


class MessageForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Envoyer à un utilisateur",
        empty_label="Aucun",
    )
    recipient_group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label="Envoyer à un groupe",
        empty_label="Aucun",
    )

    class Meta:
        model = Message
        fields = (
            "text",
            "image",
            "recipient",
            "recipient_group",
            "latitude",
            "longitude",
        )
        widgets = {
            "image": forms.FileInput(
                attrs={"accept": "image/*", "capture": "environment"}
            ),
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(MessageForm, self).__init__(*args, **kwargs)
        if user:
            self.fields["recipient"].queryset = User.objects.exclude(id=user.id)
            self.fields["recipient_group"].queryset = user.custom_user_groups.all()

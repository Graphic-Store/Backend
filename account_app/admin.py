from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

from .models import MyUser


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = [
            'email', 'date_of_birth', 'first_name', 'last_name', 'username',
            'nickname', 'phone_number'
        ]

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if not password1:
            raise ValidationError("Password cannot be empty.")
        validate_password(password1)
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        help_text="Raw passwords are not stored, so there is no way to see "
                  "this user's password, but you can change the password "
                  "using <a href=\"../password/\">this form</a>."
    )

    class Meta:
        model = MyUser
        fields = [
            "email", "password", "date_of_birth",
            "first_name", "last_name", "nickname",
            "username", "phone_number",
            "is_active", "is_admin"
        ]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ["email", "first_name", "last_name", "is_admin", "is_active"]
    list_filter = ["is_admin", "is_active"]
    
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Personal info", {
            "fields": [
                "first_name", "last_name", "nickname", "date_of_birth",
                "username", "phone_number"
            ]
        }),
        ("Permissions", {"fields": ["is_admin", "is_active"]}),
    ]
    
    add_fieldsets = [
        (None, {
            "classes": ["wide"],
            "fields": [
                "email", "date_of_birth", "first_name", "last_name",
                "nickname", "username", "phone_number",
                "password1", "password2"
            ],
        }),
    ]

    search_fields = ["email", "first_name", "last_name", "username"]
    ordering = ["email"]
    filter_horizontal = []


admin.site.register(MyUser, UserAdmin)
admin.site.unregister(Group)
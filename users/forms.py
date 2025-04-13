from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from PIL import Image
from .models import Application

class ProfileAdminForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    ACS_association = forms.CharField(max_length=100, required=False, label="ACS Association")
    ROLE_CHOICES = [
        ('mentor', 'Mentor'),
        ('mentee', 'Mentee'),
        ('both', 'Both'),
    ]
    desired_role = forms.ChoiceField(choices=ROLE_CHOICES, required=False, label="Desired Role")

    application_question = forms.CharField(
        max_length=100,
        required=False,
        label='Application Question',
    )
    #class ProfileUpdateForm(forms.ModelForm):

    interests = forms.CharField(max_length=100, required=True, label="Interests (single words)")
    ATHLETICS_CHOICES = [
        ('basketball', 'Basketball'),
        ('football', 'Football'),
        ('volleyball', 'Volleyball'),
        ('other', 'Other'),
    ]

    STEM_CHOICES = [
        ('physics', 'Physics'),
        ('biology', 'Biology'),
        ('computer_science', 'Computer Science'),
        ('other', 'Other'),
    ]

    athletics = forms.MultipleChoiceField(
        choices=ATHLETICS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Athletics',
    )
    athletics_other = forms.CharField(
        max_length=100,
        required=False,
        label='Other Athletics (Keywords)',
    )

    stem = forms.MultipleChoiceField(
        choices=STEM_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='STEM',
    )
    stem_other = forms.CharField(
        max_length=100,
        required=False,
        label='Other STEM (Keywords)',
    )




    bio = forms.CharField(
        max_length=350, 
        required=False, 
        label="Description, write something about yourself", 
        help_text="Write a description about yourself"
    ) 
    #google_form_url = forms.URLField(required=False, label='Google Form URL for Protege Application. <a href="https://docs.google.com/forms/u/0/">Create new Form</a>')
    

    class Meta:
        model = User
        fields = ['first_name','last_name','username','email','password1','password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    question = forms.CharField(max_length=255, required=False, label="What question would you like to ask an applicant?")


    class Meta:
        model = User
        fields = ['first_name','last_name','username','email']


class ProfileUpdateForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)

    image = forms.ImageField(label=('Image'), error_messages = {'invalid':("Image files only")}, widget=forms.FileInput, required=False)
    bio = forms.CharField(
        max_length=350, 
        required=False, 
        label="Description", 
        help_text="Write a description about yourself"
    )
    question = forms.CharField(
        max_length=255,
        required=False,
        label="Mentor Application Question",
        widget=forms.Textarea(attrs={'rows': 4})
    )


    class Meta:
        model = Profile
        fields = ['bio','date_of_birth','image', 'question']


    """Saving Cropped Image"""
    def save(self,*args,**kwargs):
        img = super(ProfileUpdateForm, self).save(*args, **kwargs)

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')

        if x and y and w and h:
            image = Image.open(img.image)
            cropped_image = image.crop((x, y, w+x, h+y))
            resized_image = cropped_image.resize((300, 300), Image.ANTIALIAS)
            resized_image.save(img.image.path)

        return img
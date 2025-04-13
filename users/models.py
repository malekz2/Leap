from django.db import models
from django.contrib.auth.models import User
import numpy as np
import os
import re
import json
from django.conf import settings

""" Model for User Profile """

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    following = models.ManyToManyField(User, related_name="following", blank=True)
    friends = models.ManyToManyField(User, related_name='my_friends', blank=True)
    bio = models.CharField(
        default="",
        blank=True,
        null=True,
        max_length=50,
        verbose_name="Description",
        help_text="Write a short sentence description about yourself"
    )
    date_of_birth = models.CharField(blank=True,max_length=150)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics',blank=True, null=True)

    ACS_association = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        verbose_name="ACS Association"
    )
    desired_role = models.CharField(
        max_length=10,
        choices=[
            ('mentor', 'Mentor'),
            ('mentee', 'Mentee'),
            ('both', 'Both'),
        ],
        blank=True,
        null=True,
        verbose_name="Desired Role"
    )
    application_question = models.CharField(max_length=100, blank=True, null=True, verbose_name="Question")
    interests = models.CharField(max_length=100, blank=True, null=True, verbose_name="Interests (single words)")
    #glove embeddings
    interests_embeddings = models.TextField(blank=True, null=True, verbose_name="Interests Embeddings")
    cluster_label = models.IntegerField(blank=True, null=True, help_text="K-means cluster label")
    class AreasOfInterest(models.Model):
        profile = models.OneToOneField('Profile', on_delete=models.CASCADE, related_name='areas_of_interest')
        
        ATHLETICS_CHOICES = [
            ('basketball', 'Basketball'),
            ('football', 'Football'),
            ('volleyball', 'Volleyball'),
            ('other', 'Other'),
        ]
        athletics = models.CharField(
            max_length=200,
            blank=True,
            null=True,
            verbose_name="Athletics",
            help_text="Select your athletics interests, separated by commas."
        )
        athletics_other = models.CharField(
            max_length=100,
            blank=True,
            null=True,
            verbose_name="Other Athletics"
        )
        
        STEM_CHOICES = [
            ('physics', 'Physics'),
            ('biology', 'Biology'),
            ('computer_science', 'Computer Science'),
            ('other', 'Other'),
        ]
        stem = models.CharField(
            max_length=200,
            blank=True,
            null=True,
            verbose_name="STEM",
            help_text="Select your STEM interests, separated by commas."
        )
        stem_other = models.CharField(
            max_length=100,
            blank=True,
            null=True,
            verbose_name="Other STEM"
        )

        def __str__(self):
            return f"Areas of Interest for {self.profile.user.username}"
    #user choices on what they want to teach or learn

    # embeddings of those choices
    
    # Inside Profile class:
    def update_embeddings(self):
        """Calculate and store GloVe embeddings for user interests"""
        
        if not self.interests:
            self.interests_embeddings = ""
            return

        # Load GloVe embeddings (ideally do this once and cache)
        embeddings_dict = {}
        glove_path = os.path.join(settings.BASE_DIR, 'glove.6B.50d.txt')
        
        try:
            with open(glove_path, 'r', encoding='utf-8') as f:
                for line in f:
                    values = line.split()
                    word = values[0]
                    vector = np.array(values[1:], dtype='float32')
                    embeddings_dict[word] = vector
        except FileNotFoundError:
            print(f"GloVe embeddings file not found at {glove_path}")
            return

        # Process interests
        words = re.split(r'[,\s]+|and', self.interests.lower())
        words = [word.strip() for word in words if word.strip()]
        
        vectors = []
        for word in words:
            if word in embeddings_dict:
                vectors.append(embeddings_dict[word])
        
        if vectors:
            # Calculate average embedding
            avg_vector = np.mean(vectors, axis=0)
            # Store as JSON string
            print(f"Average vector for {self.user.username}: {avg_vector}")
            self.interests_embeddings = json.dumps(avg_vector.tolist())
        else:
            print(f"No valid words found in interests for {self.user.username}")
            # If no valid words, set to empty
            self.interests_embeddings = ""
        # Inside Profile class:
    def save(self, *args, **kwargs):
        # Check if interests field changed or is new
        if self.pk is None or Profile.objects.get(pk=self.pk).interests != self.interests:
            self.update_embeddings()
        super().save(*args, **kwargs)
    def profile_posts(self):
        return self.user.post_set.all()

        # Inside Profile class:
    def get_embeddings_vector(self):
        """Return the embeddings as a numpy array"""
        if not self.interests_embeddings:
            return None
        try:
            return np.array(json.loads(self.interests_embeddings))
        except:
            return None
    def get_friends(self):
        return self.friends.all()

    def get_friends_no(self):
        return self.friends.all().count()

    def __str__(self):
        return f'{self.user.username} Profile'


class Application(models.Model):
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_applications')
    response = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application from {self.applicant.username} to {self.mentor.username}"
    
STATUS_CHOICES = (
    ('send','send'),
    ('accepted','accepted')
)

class Relationship(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friend_sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friend_receiver')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"


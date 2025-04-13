from friend.models import FriendList, FriendRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile, Application
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.dispatch import receiver 
from django.contrib.auth.signals import user_logged_in, user_logged_out
from notification.models import Notification
import requests
from django.conf import settings
from friend.utils import get_friend_request_or_false
from friend.friend_request_status import FriendRequestStatus
from django.db.models import Q
from chat.models import Room

@receiver(user_logged_in)
def got_online(sender, user, request, **kwargs):    
    user.profile.is_online = True
    user.profile.save()

@receiver(user_logged_out)
def got_offline(sender, user, request, **kwargs):   
    user.profile.is_online = False
    user.profile.save()

""" Following and Unfollowing users """
@login_required
def follow_unfollow_profile(request):
    if request.method == 'POST':
        my_profile = Profile.objects.get(user = request.user)
        pk = request.POST.get('profile_pk')
        obj = Profile.objects.get(pk=pk)

        if obj.user in my_profile.following.all():
            my_profile.following.remove(obj.user)
            notify = Notification.objects.filter(sender=request.user, notification_type=2)
            notify.delete()
        else:
            my_profile.following.add(obj.user)
            notify = Notification(sender=request.user, user=obj.user, notification_type=2)
            notify.save()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profile-list-view')

""" User account creation """
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # This creates the User
            
            # Get profile fields from form
            profile_fields = {
                'bio': form.cleaned_data.get('bio', ''),
                'date_of_birth': form.cleaned_data.get('date_of_birth', ''),
                'ACS_association': form.cleaned_data.get('ACS_association', ''),
                'desired_role': form.cleaned_data.get('desired_role', ''),
                'interests': form.cleaned_data.get('interests', ''),
                'application_question': form.cleaned_data.get('application_question', '')
                # Add any other profile fields here
            }
            
            # Update the user's profile with these fields
            profile = Profile.objects.get_or_create(user=user)[0]
            for field, value in profile_fields.items():
                setattr(profile, field, value)
            
            # Save the profile to trigger update_embeddings
            profile.save()
            
            # Handle areas of interest if needed
            
            messages.success(request, f'Your account has been created! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


""" User profile """
@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Your account has been updated!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)



""" Creating a public profile view """
def public_profile(request, username):
    user = User.objects.get(username=username)
    return render(request, 'users/public_profile.html', {"cuser":user})


""" All user profiles """
class ProfileListView(LoginRequiredMixin,ListView):
    model = Profile
    template_name = "users/all_profiles.html"
    context_object_name = "profiles"

    def get_queryset(self):
        return Profile.objects.all().exclude(user=self.request.user)

""" User profile details view """
class ProfileDetailView(LoginRequiredMixin,DetailView):
    model = Profile
    template_name = "users/user_profile_details.html"
    context_object_name = "profiles"

    def get_queryset(self):
        return Profile.objects.all().exclude(user=self.request.user)

    def get_object(self, **kwargs):
        pk = self.kwargs.get("pk")
        user = get_object_or_404(User, pk=pk)
        view_profile, created = Profile.objects.get_or_create(user=user)
        return view_profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        view_profile = self.get_object()
        my_profile = Profile.objects.get(user=self.request.user)
        if view_profile.user in my_profile.following.all():
            follow = True
        else:
            follow = False
        context["follow"] = follow

        # FRIENDS START

        account = view_profile.user
        try:
            friend_list = FriendList.objects.get(user=account)
        except FriendList.DoesNotExist:
            friend_list = FriendList(user=account)
            friend_list.save()
        friends = friend_list.friends.all()
        context['friends']=friends

        is_self = True
        is_friend = False
        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
        friend_requests = None
        user=self.request.user
        if user.is_authenticated and user!=account:
            is_self = False
            if friends.filter(pk=user.id):
                is_friend = True
            else:
                is_friend = False
                # CASE 1: request from them to you
                if get_friend_request_or_false(sender=account, receiver=user) != False:
                    request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                    context['pending_friend_request_id'] = get_friend_request_or_false(sender=account, receiver=user).pk
                # CASE 2: request you sent to them
                elif get_friend_request_or_false(sender=user, receiver=account) != False:
                    request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
                # CASE 3: no request has been sent
                else:
                    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value

        elif not user.is_authenticated:
            is_self = False
        else:
            try:
                friend_requests = FriendRequest.objects.filter(receiver=user, is_active=True)
            except:
                pass
        context['request_sent'] = request_sent
        context['is_friend'] = is_friend
        context['is_self'] = is_self
        context['friend_requests'] = friend_requests
        # FRIENDS END
        
        return context

class MentorApplicationView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "users/mentor_application.html"
    context_object_name = "profile"

    def post(self, request, *args, **kwargs):
        profile = self.get_object()
        question = request.POST.get('question')
        
        # Create and save the application
        application = Application.objects.create(
            applicant=request.user,
            mentor=profile.user,
            response=question
        )
        
        Notification.objects.create(
            sender=request.user,
            user=profile.user,
            notification_type=7,  # Mentor application type
            text_preview="New mentor application submitted."
        )
        messages.success(request, "Your mentor application has been submitted.")
        return redirect('profile-detail-view', pk=profile.pk)

# Add this new class
class ApplicationReviewView(LoginRequiredMixin, View):
    def get(self, request, applicant_id):
        applicant = get_object_or_404(User, id=applicant_id)
        # Get the most recent application instead of expecting just one
        application = Application.objects.filter(
            applicant=applicant,
            mentor=request.user
        ).order_by('-id').first()  # Assuming newer applications have higher IDs
        
        if not application:
            messages.error(request, f"No application found from {applicant.username}.")
            return redirect('show-notifications')
        
        return render(request, 'users/application_review.html', {
            'application': application,
            'applicant': applicant
        })
    
    def post(self, request, applicant_id):
        applicant = get_object_or_404(User, id=applicant_id)
        # Fix: Use filter().first() pattern consistently instead of get_object_or_404
        application = Application.objects.filter(
            applicant=applicant, 
            mentor=request.user
        ).order_by('-id').first()
        
        if not application:
            messages.error(request, f"No application found from {applicant.username}.")
            return redirect('show-notifications')
        action = request.POST.get('action')
        
        if action == 'accept':
            # Create a relationship between mentor and mentee
            mentor_profile = Profile.objects.get(user=request.user)
            mentee_profile = Profile.objects.get(user=applicant)
            
            # Send notification to applicant about acceptance
            Notification.objects.create(
                sender=request.user,
                user=applicant,
                notification_type=2,
                text_preview="Your mentor application has been accepted!"
            )
            
            # Create or get existing chat room
            chat_room = Room.objects.filter(
                Q(author=request.user, friend=applicant) | 
                Q(author=applicant, friend=request.user)
            ).first()
            
            if not chat_room:
                chat_room = Room(author=request.user, friend=applicant)
                chat_room.save()
            
            messages.success(request, f"You've accepted {applicant.username}'s application.")
            
            # Delete the notification that prompted review
            Notification.objects.filter(sender=applicant, 
                                      user=request.user, 
                                      notification_type=7).delete()
            
            # Redirect to the new chat room
            return redirect('room', chat_room.room_id, applicant.id)
            
        elif action == 'deny':
            # Send notification to applicant about rejection
            Notification.objects.create(
                sender=request.user,
                user=applicant,
                notification_type=2,  # Using Follow type for now
                text_preview="Your mentor application has been declined."
            )
            
            messages.info(request, f"You've declined {applicant.username}'s application.")
        
        # Delete the original notification since it's been processed
        Notification.objects.filter(sender=applicant, 
                                   user=request.user, 
                                   notification_type=7).delete()
        
        return redirect('show-notifications')
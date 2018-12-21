import hashlib
import json
import logging
import pathlib

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django import forms
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import six

from editor.models import ExternalTools
from editor.models import Preferences
from editor.models import Disk_filesystem
from editor.models import Profile

logger = logging.getLogger(__name__)

if settings.CUSTOM['filesystem'] == 'disk_filesystem':
    fs = Disk_filesystem(*settings.CUSTOM['filesystem_parameters'])
else:
    raise Exception("Invalid Filesystem: ", settings.CUSTOM['filesystem'], " Parameters: ", settings.CUSTOM['filesystem_parameters'])

def index(request):
    if settings.CUSTOM['login_required'] and not request.user.is_authenticated :
        return HttpResponseRedirect('accounts/login')
    context = {
        "username": None
    }
    if settings.CUSTOM['login_required']:
        context['username'] = request.user.username
    return render(request, 'editor/index.html', context)

def control(request):
    if settings.CUSTOM['login_required'] and not request.user.is_authenticated :
        return HttpResponseRedirect('accounts/login')

    send_dict = {}
    # request types we actually handle
    if request.method == "POST":
        # parse json from post body
        received_data = json.loads(request.body)
        if not isinstance(received_data,dict):
            logger.error("received_data is not a dictionary but a", str(type(received_data)))
            logger.error("the content of the request is:")
            logger.error(request.body)
            logger.error("the content of received_data is:")
            logger.error(received_data)
            send_dict['status'] = 'invalid_format'
        else:
            logger.debug("received_data:")
            for key, value in received_data.items():
                logger.debug("    ",key,":",value)
            command = None
            if not 'command' in received_data:
                logger.warning('command key not in received json data.')
            else:
                command = received_data['command']
            logger.debug('command=' + str(command))

            # tools
            if command == 'prove_local':
                send_dict = ExternalTools.run_local_prover(received_data)
            elif command == 'prove_local_predefined':
                send_dict = ExternalTools.run_predefined_local_prover(received_data)
            elif command == 'prove_remote':
                send_dict = ExternalTools.run_remote_prover(received_data)
            elif command == 'get_remote_provers':
                send_dict = ExternalTools.get_remote_provers(received_data)
            elif command == 'export_latex':
                send_dict = ExternalTools.export_latex(received_data)
            elif command == 'embed':
                send_dict = ExternalTools.embed(received_data)

            # user
            elif command == 'load_preferences':
                if settings.CUSTOM['login_required']:
                    send_dict = Profile.load(request, received_data)
                else:
                    send_dict = Preferences.store(received_data)
            elif command == 'store_preferences':
                if settings.CUSTOM['login_required']:
                    send_dict = Profile.store(request, received_data)
                else:
                    send_dict = Preferences.store(received_data)

            # filesystem
            elif command == 'list_directory':
                send_dict = fs.list_directory(request, received_data)
            elif command == 'path_info':
                send_dict = fs.info(request, received_data)
            elif command == 'retrieve_file':
                send_dict = fs.retrieve_file(request, received_data)
            elif command == 'store_file':
                send_dict = fs.store_file(request, received_data)
            elif command == 'create_file':
                send_dict = fs.create_file(request, received_data)
            elif command == 'delete_file':
                send_dict = fs.delete_file(request, received_data)
            elif command == 'rename_file':
                send_dict = fs.rename_file(request, received_data)
            elif command == 'create_directory':
                send_dict = fs.create_directory(request, received_data)
            elif command == 'delete_directory':
                send_dict = fs.delete_directory(request, received_data)
            elif command == 'rename_directory':
                send_dict = fs.rename_directory(request, received_data)

            else:
                send_dict['status'] = 'command_not_implemented.command=' + str(command)
                logger.debug('command not implemented. command=' + str(command))

    # request types we do not want
    else:
        send_dict['status'] = 'request_not_post'
        logger.debug('no post request')

    # respond with dict in json form
    send_json_data = json.dumps(send_dict)
    return HttpResponse(send_json_data)

###############################
# User Management
###############################

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
account_activation_token = TokenGenerator()

class SignupForm(UserCreationForm):
    #email = forms.EmailField(max_length=200, help_text='Required')
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    def clean_email(self):
        # Get the email
        email = self.cleaned_data.get('email')

        # Check to see if any users already exist with this email as a username.
        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            # Unable to find a user, this is fine
            return email
        except Exception:
            pass

        # A user was found with this as a username, raise an error.
        raise forms.ValidationError('This email address is already in use.')

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            mail_subject = 'Activate your TPTP editor account.'
            token = account_activation_token.make_token(user)
            print("hash",token)
            message = render_to_string('registration/activate_email.html', {
                'protocol': settings.CUSTOM['protocol'],
                'user': user,
                'domain': settings.CUSTOM['domain'],
                'uid': user.id,
                'token': token
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'registration/activate_after_signup.html')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})

class ActivateResendForm(forms.Form):
    email = forms.EmailField()

def resend_activation_link(request):
    if request.method == 'POST':
        form = ActivateResendForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return render(request, 'registration/activate_link_resend_invalid.html', context={"error_message": "This email is not in use."})
            if user.is_active:
                return render(request, 'registration/activate_link_resend_invalid.html', context={"error_message": "This account is already activated."})
            mail_subject = 'Activate your TPTP editor account.'
            token = account_activation_token.make_token(user)
            message = render_to_string('registration/activate_email.html', {
                'protocol': settings.CUSTOM['protocol'],
                'user': user,
                'domain': settings.CUSTOM['domain'],
                'uid': user.id,
                'token': token
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'registration/activate_after_signup.html')
    else:
        form = ActivateResendForm()
    return render(request, 'registration/activate_link_resend.html', {'form': form})

def activate(request, uid, token):
    try:
        user = User.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        fs.on_user_creation(user)
        user.save()
        login(request, user)
        return redirect(settings.BASE_URL)
    else:
        return render(request, 'registration/activate_link_invalid.html')
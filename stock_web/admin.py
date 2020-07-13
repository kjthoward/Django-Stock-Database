from django.core.exceptions import PermissionDenied
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, AdminPasswordChangeForm, ReadOnlyPasswordHashField
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import gettext, gettext_lazy as _
from django.template.response import TemplateResponse
from django import forms
import pdb
from .models import Suppliers, Reagents, CytoUsage, Internal, Validation, Recipe, Inventory, Solutions, ForceReset
#Registers models so they can be interacted with in Admin site
admin.site.register(Suppliers)
admin.site.register(Reagents)
admin.site.register(Internal)
admin.site.register(CytoUsage)
admin.site.register(Validation)
admin.site.register(Recipe)
admin.site.register(Inventory)
admin.site.register(Solutions)
admin.site.register(ForceReset)
#Changes titles on Admin Site
admin.site.site_header="Stock (Web) Database Admin Page"
admin.site.index_title="Stock Administration"
#Changes the "View site" URL
admin.site.site_url = "/stock/listinv/"


class PWResetForm(AdminPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PWResetForm, self).__init__(*args, **kwargs)
        self.fields['password1'] = forms.CharField(initial="stockdb1",widget=forms.HiddenInput(),label="")
        self.fields['password2'] = forms.CharField(initial="stockdb1",widget=forms.HiddenInput(),label="")

#Password gets set as 'password' required to change on first login
class UserCreationFormExtended(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationFormExtended, self).__init__(*args, **kwargs)
        self.fields['password1'] = forms.CharField(widget=forms.HiddenInput(),initial="stockdb1")
        self.fields['password2'] = forms.CharField(widget=forms.HiddenInput(),initial="stockdb1")

UserAdmin.add_form = UserCreationFormExtended
UserAdmin.add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': ('username', 'password1', 'password2',)
    }),
)

#Replaces default Admin site with custom version (which is altered default)
admin.site.unregister(User)
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username","email","first_name","last_name","is_staff","is_active")
    change_password_form = PWResetForm
    add_form_template = 'admin/stock_web/add_form.html'
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()
        #Only Superusers can change usernames or create super users, checks if form is add or change
        #as obviously you need to be able to add username...
        if not is_superuser:

            if "change" in request.path:
                disabled_fields = {
                'username',
                'is_superuser',
            }
            else:
                disabled_fields = {
                    'is_superuser',
                }
        if (
            not is_superuser
            and obj is not None
            and obj == request.user
        ):
            disabled_fields |= {
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            }
        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True
        #changes password text from change to reset
        form.base_fields["password"]=ReadOnlyPasswordHashField(
                                    label=_("Password"),
                                    help_text=_(
                                        "Raw passwords are not stored, so there is no way to see this "
                                        "user's password, but you can reset the password using "
                                        "<a href=\"{}\">this form</a>."
                                    ))
        return form
    #Can't edit date joined
    readonly_fields = [
        'date_joined',
        'last_login',
    ]

    #custom "change password" form which is pre-filled in with "password" and boxes are hidden
    #so it gets reset to password
    def user_change_password(self, request, id, form_url=''):
        user = self.get_object(request, unquote(id))
        if not self.has_change_permission(request, user):
            raise PermissionDenied
        if user is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': self.model._meta.verbose_name,
                'key': escape(id),
            })
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                msg = gettext('Password reset successfully.')
                force=ForceReset.objects.get(user=user.id)
                force.force_password_change=True
                force.save()
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect(
                    reverse(
                        '%s:%s_%s_change' % (
                            self.admin_site.name,
                            user._meta.app_label,
                            user._meta.model_name,
                        ),
                        args=(user.pk,),
                    )
                )
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Reset Password: %s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
            **self.admin_site.each_context(request),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            'admin/stock_web/change_password.html',
            context,
        )

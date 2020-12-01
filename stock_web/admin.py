from django.core.exceptions import PermissionDenied
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, AdminPasswordChangeForm, ReadOnlyPasswordHashField
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext, gettext_lazy as _
from django.template.response import TemplateResponse
from django import forms
import pdb
from .models import Suppliers, Teams, Reagents, VolUsage, Internal, Validation, Recipe, Inventory, Solutions, ForceReset

#Modify admin view pages to include things like search
class Supplier_Admin(admin.ModelAdmin):
    list_display = ("name","is_active")
    search_fields = ("name",)

class Team_Admin(admin.ModelAdmin):
    list_display = ("name","is_active")
    search_fields = ("name",)

class Reagent_Admin(admin.ModelAdmin):
    def amount_in_stock(self, obj):
        if obj.track_vol==True:
            return "{}µl".format(obj.count_no)
        else:
            return obj.count_no
    amount_in_stock.short_description = "Amount in Stock"
    list_display = ("name", "supplier_def", "cat_no", "team_def", "amount_in_stock", "open_no", "track_vol", "is_active")
    search_fields = ("name", "cat_no", "supplier_def__name", "team_def__name")

class Usage_Admin(admin.ModelAdmin):
    list_display = ("item", "start", "end", "used", "date", "user")
    search_fields = ("item__reagent__name", "item__internal__batch_number", "date", "user__username")

class Validation_Admin(admin.ModelAdmin):
    list_display = ("val_run", "val_date", "val_user")
    search_fields = ("val_run", "val_date", "val_user__username")

class Recipe_Admin(admin.ModelAdmin):
    def list_comp_recipe(self, obj):
        link_list=[]
        for comp in obj.list_comp():
            link="../reagents/{}/change".format(comp.id)
            text=comp.name
            link_list+=['<a href="{}">{}</a>'.format(link,text)]
        return mark_safe(", ".join(link_list))
    list_comp_recipe.short_description = "Components"
    list_display = ("name", "Default_Team", "shelf_life", "track_vol", "list_comp_recipe", "witness_req") 
    search_fields = ("name", "reagent__team_def__name", "comp1__name", "comp2__name", \
                     "comp3__name", "comp4__name", "comp5__name", "comp6__name", \
                     "comp7__name", "comp8__name", "comp9__name", "comp10__name")

class Inventory_Admin(admin.ModelAdmin):
    def val_links(self, obj):
        if obj.val is not None:
            link="../validation/{}/change/".format(obj.val.id)
            return mark_safe('<a href="{}">{}</a>'.format(link,obj.val))
        else:
            return "-"
    val_links.short_description = "Validation"
    list_display = ("reagent", "internal", "supplier", "po", "lot_no", "team", "date_rec", "rec_user",\
                     "date_exp", "date_op", "op_user", "val_links", "date_fin", "fin_user")
    search_fields = ("reagent__name", "internal__batch_number", "po", "team__name", "rec_user__username", \
                     "op_user__username", "fin_user__username", "val__val_run")


class Solution_Admin(admin.ModelAdmin):
    def list_comp_soltuion(self, obj):
        link_list=[]
        for comp in obj.list_comp():
            link="../inventory/{}/change".format(comp.id)
            text=comp.reagent.name
            link_list+=['<a href="{}">{}</a>'.format(link,text)]
        return mark_safe(", ".join(link_list))
    def current_vol(self, obj):
        if Inventory.objects.get(sol=obj.id).reagent.track_vol==True:
            return "{}µl".format(Inventory.objects.get(sol=obj.id).current_vol)
        else:
            return "N/A"
    current_vol.short_description = "Current Volume"
    list_display = ("recipe", "Stock_Number", "current_vol", "creator_user", "date_created", "list_comp_soltuion")
    search_fields = ("recipe__name", "inventory__internal__batch_number", "creator_user__username", "comp1__reagent__name", "comp2__reagent__name", \
                     "comp3__reagent__name", "comp4__reagent__name", "comp5__reagent__name", "comp6__reagent__name", \
                     "comp7__reagent__name", "comp8__reagent__name", "comp9__reagent__name", "comp10__reagent__name")
    # list_select_related = ("recipe", "comp1", "comp2", "comp3", "comp4", "comp5", "comp6", "comp7", "comp8", "comp9", "comp10", "creator_user")
#Registers models so they can be interacted with in Admin site
admin.site.register(Suppliers, Supplier_Admin)
admin.site.register(Teams, Team_Admin)
admin.site.register(Reagents, Reagent_Admin)
admin.site.register(Internal)
admin.site.register(VolUsage, Usage_Admin)
admin.site.register(Validation, Validation_Admin)
admin.site.register(Recipe, Recipe_Admin)
admin.site.register(Inventory, Inventory_Admin)
admin.site.register(Solutions, Solution_Admin)
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

def SU(self):
    return self.is_superuser
SU.boolean = True
SU.admin_order_field = 'is_superuser'
SU.short_description='SuperUser'

#function to list all roles someone has
def roles(self):
    value = ', '.join([str(name) for name in self.groups.all()])
    return mark_safe("<nobr>{}</nobr>".format(value))
roles.allow_tags = True
roles.short_description = u'Groups'

# function to show last login
def last(self):
    fmt = "%b %d, %H:%M"
    #fmt = "%Y %b %d, %H:%M:%S"
    if self.last_login is not None:
        value = self.last_login.strftime(fmt)
    else:
        value = None
    return mark_safe("<nobr>%s</nobr>" % value)
last.allow_tags = True
last.admin_order_field = "last_login"
last.short_description = "Last Login"

def pw_reset(self):
    url="./{}/password/".format(self.id)
    text = "Reset"
    return mark_safe('<a href="{}">{}</a>'.format(url,text))
pw_reset.allow_tags = True
pw_reset.short_description = "Reset PW"

#Replaces default Admin site with custom version (which is altered default)
admin.site.unregister(User)
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username","email","first_name","last_name","is_active", SU, roles, last, pw_reset)
    change_password_form = PWResetForm
    add_form_template = 'admin/stock_web/add_form.html'
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_superuser', 'groups'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    # import pdb; pdb.set_trace()
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
                'is_superuser',
                'groups',
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

import datetime
from dateutil.relativedelta import relativedelta
from django import forms
from django.db.models import F
from django.contrib.auth.models import User
from django_select2.forms import Select2Widget
from bootstrap_daterangepicker import widgets, fields
from .models import Suppliers, Reagents, Internal, Recipe, Inventory, Teams
from django.contrib.auth.forms import PasswordChangeForm

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"autocomplete": "off"}))
    password = forms.CharField(max_length=20, widget=forms.PasswordInput(attrs={"autocomplete": "off"}))
#sets width of all Select2Widget search boxes
Select2Widget=Select2Widget(attrs={"style": "width:12.5em"})

class DateInput(forms.DateInput):
    input_type = 'date'


class ShowActiveModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.show_active()

class NewInvForm1(forms.ModelForm):
    reagent=forms.ModelChoiceField(queryset = Reagents.objects.all().exclude(is_active=False).order_by("name"), label="Reagent", widget=Select2Widget)

    class Meta:
        model = Inventory
        fields= ("reagent",)
    def clean(self):
        super(NewInvForm1, self).clean()
        errors=[]
        item=Reagents.objects.get(pk=self.data["reagent"])
        if item.recipe is not None:
            for i in range(1,item.recipe.length()+1):
                if Reagents.objects.get(pk=eval('item.recipe.comp{}.id'.format(i))).count_no==0:
                    errors+=[forms.ValidationError("There is no {} in stock".format(eval('item.recipe.comp{}.name'.format(i))))]
            if errors:
                raise forms.ValidationError(errors)
        #filters out recipes from inventory selection form
##    def __init__(self, *args, **kwargs):
##        super(NewInvForm1, self).__init__(*args, **kwargs)
##        self.fields["reagent"].queryset=Reagents.objects.filter(recipe_id=None)
class NewInvForm(forms.ModelForm):
    num_rec=forms.IntegerField(min_value=1, label="Number Received")
    class Meta:
        model = Inventory
        fields = ("reagent", "supplier", "team", "lot_no", "cond_rec", "date_rec", "po", "date_exp", "num_rec", "accept_reason")
        widgets = {"supplier":Select2Widget,
                   "team":Select2Widget,
                   "accept_reason":forms.Textarea(attrs={"style": "height:4em;"}),
                   "date_rec":DateInput(),
                   "date_exp":DateInput(),
                   "reagent":forms.HiddenInput(),
                   "vol_rec":forms.HiddenInput(),
                   "current_vol":forms.HiddenInput()}

    def clean(self):
        super(NewInvForm, self).clean()
        errors=[]
        if (((self.cleaned_data["date_exp"]-self.cleaned_data["date_rec"])<=datetime.timedelta(181)) and (self.cleaned_data["accept_reason"] is None)):
            errors+=[("accept_reason", forms.ValidationError("If an item expires within 6 months an Acceptance Reason must be given"))]
        if errors!=[]:
            for error in errors:
                self.add_error(error[0], error[1])
    def __init__(self, *args, **kwargs):
        super(NewInvForm, self).__init__(*args, **kwargs)
        self.fields["supplier"].queryset=Suppliers.objects.exclude(name="Internal").exclude(is_active=False)
        self.fields["accept_reason"].required= False
        self.fields["team"].queryset=Teams.objects.exclude(is_active=False)

class NewProbeForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ("reagent", "supplier", "team", "lot_no", "cond_rec", "date_rec", "po", "date_exp", "vol_rec", "accept_reason")
        widgets = {"supplier":Select2Widget,
                   "team":Select2Widget,
                   "accept_reason":forms.Textarea(attrs={"style": "height:4em;"}),
                   "date_rec":DateInput(),
                   "date_exp":DateInput(),
                   "reagent":forms.HiddenInput(),
                   "current_vol":forms.HiddenInput()}

    def clean(self):
        super(NewProbeForm, self).clean()
        errors=[]
        if (((self.cleaned_data["date_exp"]-self.cleaned_data["date_rec"])<=datetime.timedelta(181)) and (self.cleaned_data["accept_reason"] is None)):
            errors+=[("accept_reason", forms.ValidationError("If an item expires within 6 months an Acceptance Reason must be given"))]
        if errors!=[]:
            for error in errors:
                self.add_error(error[0], error[1])
    def __init__(self, *args, **kwargs):
        super(NewProbeForm, self).__init__(*args, **kwargs)
        self.fields["supplier"].queryset=Suppliers.objects.exclude(name="Internal").exclude(is_active=False)
        self.fields["accept_reason"].required= False
        self.fields["team"].queryset=Teams.objects.exclude(is_active=False)

class UseItemForm(forms.ModelForm):
    vol_used = forms.IntegerField(min_value=1, label=u"Volume Used (µl)")
    date_used = forms.DateField(widget=DateInput(), label=u"Date Used")
    class Meta:
        model = Inventory
        fields = ("current_vol","date_op", "last_usage")
        widgets= {"current_vol":forms.HiddenInput,
                  "date_op":forms.HiddenInput,
                  "last_usage":forms.HiddenInput}
    def clean(self):
        super(UseItemForm, self).clean()
        errors=[]
        if self.cleaned_data["vol_used"]>self.cleaned_data["current_vol"]:
            errors+=[("vol_used", forms.ValidationError("Volume Used Exceeds Current Volume in Tube"))]
        if self.cleaned_data["date_used"]<self.cleaned_data["date_op"]:
            errors+=[("date_used", forms.ValidationError("Date Used is before Date Open"))]
        if self.cleaned_data["last_usage"] is not None:
            if self.cleaned_data["date_used"]<self.cleaned_data["last_usage"].date:
                errors+=[("date_used", forms.ValidationError("This Usage Date is before the most recent use"))]
        if errors!=[]:
            for error in errors:
                self.add_error(error[0], error[1])

class OpenItemForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ("date_rec", "date_op")
        widgets = {"date_rec":forms.HiddenInput,
                   "date_op":DateInput()}
        labels = {"date_op":"Date Open"}
    def clean(self):
        super(OpenItemForm, self).clean()
        if self.cleaned_data["date_op"]<datetime.datetime.strptime(self.data["date_rec"],"%Y-%m-%d").date():
            self.add_error("date_op", forms.ValidationError("Date open occurs before received date"))

class ValItemForm(forms.ModelForm):
    val_date = forms.DateField(widget=DateInput(), label="Validation Date")
    val_run = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"autocomplete": "off"}), label="Validation Run")
    class Meta:
        model = Inventory
        fields = ("date_op",)
        widgets=  {"date_op":forms.HiddenInput}
    def clean(self):
        super(ValItemForm, self).clean()
        if self.cleaned_data["val_date"]<datetime.datetime.strptime(self.data["date_op"],"%Y-%m-%d").date():
            self.add_error("val_date", forms.ValidationError("Date validated occurs before date opened"))


class FinishItemForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ("date_op","date_rec", "fin_text","is_op", "date_fin")
        widgets = {"date_op":forms.HiddenInput,
                   "date_rec":forms.HiddenInput,
                   "is_op":forms.HiddenInput,
                   "fin_text":forms.Textarea(attrs={"style": "height:5em;"}),
                   "date_fin":DateInput()}
        labels = {"date_fin":"Date Finished"}
    def clean(self):
        super(FinishItemForm, self).clean()
        fin_date=self.cleaned_data["date_fin"]
        if fin_date<self.cleaned_data["date_rec"]:
            self.add_error("date_fin", forms.ValidationError("Date occurs before the item was received"))
        if self.cleaned_data["is_op"]==True:
            if fin_date<datetime.datetime.strptime(self.data["date_op"],"%Y-%m-%d").date():
                self.add_error("date_fin", forms.ValidationError("Date occurs before item was opened"))


    def __init__(self, *args, **kwargs):
        super(FinishItemForm, self).__init__(*args, **kwargs)
        if self.initial["is_op"]==False:
            self.fields["fin_text"].required = True

class NewSupForm(forms.ModelForm):
    class Meta:
        model = Suppliers
        fields = "__all__"
        widgets = {"is_active":forms.HiddenInput}
    def clean(self):
        super(NewSupForm, self).clean()
        if Suppliers.objects.filter(name=self.cleaned_data["name"]).exists():
            self.add_error("name", forms.ValidationError("A Supplier with the name {} already exists".format(self.cleaned_data["name"])))

class NewTeamForm(forms.ModelForm):
    class Meta:
        model = Teams
        fields = "__all__"
        widgets = {"is_active":forms.HiddenInput}
    def clean(self):
        super(NewTeamForm, self).clean()
        if Teams.objects.filter(name=self.cleaned_data["name"]).exists():
            self.add_error("name", forms.ValidationError("A Team with the name {} already exists".format(self.cleaned_data["name"])))

class NewReagentForm(forms.ModelForm):
    class Meta:
        model = Reagents
        fields= "__all__"
        ####UNHIDE STORAGE IF EVER USED
        widgets = {"count_no":forms.HiddenInput,
                   "recipe":forms.HiddenInput,
                   "supplier_def":Select2Widget,
                   "team_def": Select2Widget,
                   "storage":forms.HiddenInput,
                   "is_active":forms.HiddenInput}
        labels = {"track_vol":"Tick if this reagent should have it's volume tracked (e.g FISH probe)"}
    def __init__(self, *args, **kwargs):
        super(NewReagentForm, self).__init__(*args, **kwargs)
        self.fields["supplier_def"].queryset=Suppliers.objects.exclude(name="Internal").exclude(is_active=False)
        self.fields["supplier_def"].required = True
        self.fields["team_def"].queryset=Teams.objects.exclude(is_active=False)
        self.fields["team_def"].required = True

    def clean(self):
        super(NewReagentForm, self).clean()
        if Reagents.objects.filter(name=self.cleaned_data["name"]).exists():
            self.add_error("name", forms.ValidationError("A Reagent with the name {} already exists".format(self.cleaned_data["name"])))

class NewRecipeForm(forms.ModelForm):
    number=forms.IntegerField(min_value=1, label=u"Minimum Stock Level")
    team_def=forms.ModelChoiceField(queryset = Teams.objects.all().order_by("name"), label=u"Default Team", widget=Select2Widget, required=True)
    class Meta:
        model = Recipe
        fields = "__all__"
        widgets = {"reagent":forms.HiddenInput,
                   "comp1":Select2Widget,
                   "comp2":Select2Widget,
                   "comp3":Select2Widget,
                   "comp4":Select2Widget,
                   "comp5":Select2Widget,
                   "comp6":Select2Widget,
                   "comp7":Select2Widget,
                   "comp8":Select2Widget,
                   "comp9":Select2Widget,
                   "comp10":Select2Widget}
        labels = {"track_vol":"Tick if this reagent should have it's volume tracked (e.g FISH probe)"}          
    def __init__(self, *args, **kwargs):
        super(NewRecipeForm, self).__init__(*args, **kwargs)
        self.fields["team_def"].queryset=Teams.objects.exclude(is_active=False)
##        for i in range(1,11):
##            self.fields["comp{}".format(i)].queryset=Reagents.objects.filter(recipe_id=None)

    def clean(self):
        super(NewRecipeForm, self).clean()
        comps=[]
        errors=[]
        present=True
        reagents={}
        for k,v in self.cleaned_data.items():
            if "comp" in k:
                reagents[k]=v
##        reagents=self.cleaned_data
##        del(reagents["name"])
##        del(reagents["shelf_life"])
        for key, value in sorted(reagents.items(), key = lambda x:int(x[0][4:])):
            if "comp" in key:
                if value is not None:
                    if present==False:
                        errors+=[forms.ValidationError("There is a gap in selected reagents")]
                    if value.name in comps:
                        errors+=[forms.ValidationError("Reagent {} appears more than once".format(value.name))]
                    comps+=[value.name]
                else:
                    present=False
        if len(comps)<1:
            errors+=[forms.ValidationError("At least 1 component is needed to create a recipe")]
        if self.cleaned_data["shelf_life"]<1:
            self.add_error("shelf_life", forms.ValidationError("Shelf Life must be 1 month or more"))
        if errors:
            raise forms.ValidationError(errors)

class SearchForm(forms.Form):
    rec_range = fields.DateRangeField(required=False, label=u"Received Between", input_formats=['%Y-%m-%d'], widget=widgets.DateRangeWidget(format="%Y-%m-%d", attrs={"style": "width:15em"}))
    open_range = fields.DateRangeField(required=False, label=u"Opened Between",widget=widgets.DateRangeWidget(attrs={"style": "width:15em"}))
    val_range = fields.DateRangeField(required=False, label=u"Validated Between",widget=widgets.DateRangeWidget(attrs={"style": "width:15em"}))
    fin_range = fields.DateRangeField(required=False, label=u"Finished Between",widget=widgets.DateRangeWidget(attrs={"style": "width:15em"}))
    reagent=forms.CharField(label="Reagent Name", max_length=30, required=False)
    supplier=forms.CharField(label="Supplier Name", max_length=25, required=False)
    lot_no=forms.CharField(label="Lot Number", max_length=20, required=False)
    int_id=forms.CharField(label="Stock Number", max_length=4, required=False)
    team=forms.ModelChoiceField(queryset = Teams.objects.all().order_by("name"), label=u"Team", widget=Select2Widget, required=False)
    in_stock=forms.ChoiceField(label="Include Finished Items?", choices=[(0,"NO"),(1,"YES")])

class ValeDatesForm(forms.Form):
    val_range = fields.DateRangeField(required=False, label=u"Validated Between",widget=widgets.DateRangeWidget(attrs={"style": "width:15em"}))

class ChangeDefSupForm1(forms.Form):
    name=forms.ModelChoiceField(queryset = Reagents.objects.filter(recipe_id=None).order_by("name"), widget=Select2Widget)

class ChangeDefSupForm(forms.Form):
    supplier_def=forms.ModelChoiceField(queryset = Suppliers.objects.all().exclude(name="Internal").exclude(is_active=False).order_by("name"), label=u"Select New Supplier", widget=Select2Widget)
    old=forms.ModelChoiceField(queryset = Suppliers.objects.all().order_by("name"), widget=forms.HiddenInput())
    def clean(self):
        super(ChangeDefSupForm, self).clean()
        if self.cleaned_data["old"]==self.cleaned_data["supplier_def"]:
            self.add_error("supplier_def", forms.ValidationError("Previous Supplier Selected. Item Not Changed"))

class ChangeDefTeamForm1(forms.Form):
    name=forms.ModelChoiceField(queryset = Reagents.objects.filter(recipe_id=None).order_by("name"), widget=Select2Widget)

class ChangeDefTeamForm(forms.Form):
    team_def=forms.ModelChoiceField(queryset = Teams.objects.all().exclude(is_active=False).order_by("name"), label=u"Select New Team", widget=Select2Widget)
    old=forms.ModelChoiceField(queryset = Teams.objects.all().order_by("name"), widget=forms.HiddenInput())
    def clean(self):
        super(ChangeDefTeamForm, self).clean()
        if self.cleaned_data["old"]==self.cleaned_data["team_def"]:
            self.add_error("team_def", forms.ValidationError("Previous Team Selected. Item Not Changed"))

class RemoveSupForm(forms.Form):
    supplier=forms.ModelChoiceField(queryset = Suppliers.objects.all().exclude(name="Internal").order_by("name"), widget=Select2Widget)
    def clean(self):
        super(RemoveSupForm, self).clean()
        if len(Inventory.objects.filter(supplier_id=self.data["supplier"]))>0:
           self.add_error("supplier", forms.ValidationError("Unable to Delete Supplier. {} Inventory Items Exist With This Supplier".format(len(Inventory.objects.filter(supplier_id=self.data["supplier"])))))
           self.add_error("supplier", forms.ValidationError("If you no longer need this supplier try using the '(De)Activate Supplier' Page"))
        elif len(Reagents.objects.filter(supplier_def_id=self.data["supplier"]))>0:
            self.add_error("supplier", forms.ValidationError("Unable to Delete Supplier. The Following Items Have This Supplier as Their Default Supplier:"))
            for supplier in Reagents.objects.filter(supplier_def_id=self.data["supplier"]):
                self.add_error("supplier", forms.ValidationError(supplier))
            self.add_error("supplier", forms.ValidationError("If you no longer need this supplier try using the '(De)Activate Supplier' Page"))

class EditSupForm(forms.Form):
    name=ShowActiveModelChoiceField(queryset = Suppliers.objects.all().exclude(name="Internal").order_by("name"), widget=Select2Widget, label=u"Supplier")

    def clean(self):
        super(EditSupForm, self).clean()
        if len(Reagents.objects.filter(supplier_def=self.cleaned_data["name"]))>0 and Suppliers.objects.get(name=self.cleaned_data["name"]).is_active==True:
            self.add_error("name", forms.ValidationError("Unable to Deactivate Supplier: {}. The Following Items Have This Supplier as Their Default Supplier:".format(self.cleaned_data["name"])))
            for reagent in Reagents.objects.filter(supplier_def=self.data["name"]):
                self.add_error("name", forms.ValidationError(reagent))

class EditTeamForm(forms.Form):
    name=ShowActiveModelChoiceField(queryset = Teams.objects.all().order_by("name"), widget=Select2Widget, label=u"Team")

    def clean(self):
        super(EditTeamForm, self).clean()
        if len(Reagents.objects.filter(team_def=self.cleaned_data["name"]))>0 and Teams.objects.get(name=self.cleaned_data["name"]).is_active==True:
            self.add_error("name", forms.ValidationError("Unable to Deactivate Team: {}. The Following Items Have This Team as Their Default Team:".format(self.cleaned_data["name"])))
            for reagent in Reagents.objects.filter(team_def=self.data["name"]):
                self.add_error("name", forms.ValidationError(reagent))

class EditReagForm(forms.Form):
    name=ShowActiveModelChoiceField(queryset = Reagents.objects.all().order_by("name"), widget=Select2Widget, label=u"Reagent")

class EditInvForm(forms.Form):
    item=forms.CharField(label="Stock Number", max_length=4,widget=forms.TextInput(attrs={"autocomplete": "off"}))
    def clean(self):
        super(EditInvForm, self).clean()
        try:
            Inventory.objects.get(internal=Internal.objects.get(batch_number=self.cleaned_data["item"]))
        except:
            self.add_error("item", forms.ValidationError("Internal ID {} is not Linked to an Inventory Item".format(self.cleaned_data["item"])))

class DeleteForm(forms.Form):
    sure=forms.BooleanField(label="Tick this box and click save to proceed with the action")

class UnValForm(forms.Form):
    sure=forms.BooleanField(label="Tick this box and click save to proceed with the action")
    all_type=forms.ChoiceField(label="Remove validation for other items on this run?")

class ChangeMinForm1(forms.Form):
    name=forms.ModelChoiceField(queryset = Reagents.objects.all().order_by("name"), label="Reagent", widget=Select2Widget)

class ChangeMinForm(forms.Form):
    number=forms.IntegerField(min_value=0, label="New Minimum Stock Amount")
    old=forms.IntegerField(min_value=0, widget=forms.HiddenInput())
    def clean(self):
        super(ChangeMinForm, self).clean()
        if int(self.cleaned_data["old"])==int(self.cleaned_data["number"]):
            self.add_error("number", forms.ValidationError("This is the same as the Current Minimum Stock Level"))

class StockReportForm(forms.Form):
    name=forms.ModelChoiceField(queryset = Reagents.objects.filter(count_no__gte=1).exclude(is_active=False, count_no__lt=1).order_by("name"), label="Reagent", widget=Select2Widget)
    rec_range = fields.DateRangeField(required=False, label=u"Received Between", input_formats=['%Y-%m-%d'], widget=widgets.DateRangeWidget(format="%Y-%m-%d", attrs={"style": "width:15em"}))
    open_range = fields.DateRangeField(required=False, label=u"Opened Between",widget=widgets.DateRangeWidget(attrs={"style": "width:15em"}))
    val_range = fields.DateRangeField(required=False, label=u"Validated Between",widget=widgets.DateRangeWidget(attrs={"style": "width:15em"}))
    fin_range = fields.DateRangeField(required=False, label=u"Finished Between",widget=widgets.DateRangeWidget(attrs={"style": "width:15em"}))
    in_stock=forms.ChoiceField(label="Include Finished Items?", choices=[(0,"NO"),(1,"YES")])

class InvReportForm(forms.Form):
    report=forms.ChoiceField(label="Select Report To Generate",
                             choices=[("unval","All Unvalidated Items"),
                                      ("val","All Validated Items"),
                                      ("exp","Items Expiring Soon"),
                                      ("all","All In-Stock Items"),
                                      ("allinc","All In-Stock Items (Including Open Items)"),
                                      ("minstock","All Items Below Minimum Stock Level"),
                                      ("finished","All Finished Items")])
    rec_range = fields.DateRangeField(required=False, label=u"Received Between", input_formats=['%Y-%m-%d'], widget=widgets.DateRangeWidget(format="%Y-%m-%d", attrs={"style": "width:15em"}))
    open_range = fields.DateRangeField(required=False, label=u"Opened Between",widget=widgets.DateRangeWidget(attrs={"style": "width:15em"}))
    val_range = fields.DateRangeField(required=False, label=u"Validated Between",widget=widgets.DateRangeWidget(attrs={"style": "width:15em"}))
    fin_range = fields.DateRangeField(required=False, label=u"Finished Between",widget=widgets.DateRangeWidget(attrs={"style": "width:15em"}))
    team=forms.ModelChoiceField(queryset = Teams.objects.all().order_by("name"), label=u"Team", widget=Select2Widget, required=False)
    def clean(self):
        super(InvReportForm, self).clean()
        if self.cleaned_data["report"]=="minstock":
            queryset=Reagents.objects.filter(count_no__lt=F("min_count"))
            if self.cleaned_data["team"] is not None:
                queryset.filter(team_def=self.cleaned_data["team"])
            if len(queryset)==0:
                self.add_error("report", forms.ValidationError("There are no items with stock levels below their minimum"))

class PWResetForm(forms.Form):
    user = forms.CharField(label="Enter Username", max_length=20, widget=forms.TextInput(attrs={"autocomplete": "off"}))
    def clean(self):
        super(PWResetForm, self).clean()
        try:
            USER=User.objects.get(username=self.cleaned_data["user"])
            if USER.email=="":
                self.add_error("user", forms.ValidationError("User {} does not have an email address entered.\nContact an Admin to reset you password".format(self.cleaned_data["user"])))
        except:
            self.add_error("user", forms.ValidationError("Username {} does not exist".format(self.cleaned_data["user"])))

class PasswordChangeForm(PasswordChangeForm):
    #Blanks help_text, as it messes up formatting/spacing of boxes, re-added using messages.info in views
    PasswordChangeForm.base_fields["new_password1"].help_text=""

class WitnessForm(forms.Form):
    name=forms.ModelChoiceField(queryset = User.objects.filter(is_active=True).exclude(username="Admin").order_by("username"), widget=Select2Widget, label=u"Select Witness")
    team=forms.ModelChoiceField(queryset = Teams.objects.all().order_by("name"), label=u"Team", widget=Select2Widget, required=True)
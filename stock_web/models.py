from django.db import models, transaction, IntegrityError
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F
from django.apps import apps
from django.conf import settings
from calendar import monthrange
import datetime
import itertools


from .email import send, EMAIL


# Check if should be set to True. True would mean that whenever anyone gets an account
# made they will need to change password on first login. Useful as allows accounts
# to be made by admin with e.g "password" but could be annoying if user is there
# when acount gets made and sets their own password...
class ForceReset(models.Model):
    def __str__(self):
        return "Toggle Reset for {}".format(self.user)

    class Meta:
        verbose_name_plural = "Force Password Resets"

    user = models.OneToOneField(User, on_delete=models.PROTECT)
    force_password_change = models.BooleanField(default=True)
    emailed = models.BooleanField(default=False)


# automatically adds user to ForceReset table upon creation
# if not done will give errors when trying to do checks
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        ForceReset.objects.create(user=instance)
    if instance.email != "":
        USER = ForceReset.objects.get(user=instance)
        if USER.emailed == False:
            subject = "Stock Database account created"
            text = "<p>An account on the Stock Database has been created with the following details:<br><br>"
            text += "Username: {}<br><br>".format(instance.username)
            text += "Password: stockdb1<br><br>"
            text += "NOTE - you will be required to change this password when you first log in.<br><br>"
            if EMAIL == True:
                try:
                    send(subject, text, instance.email)
                    USER.emailed = True
                    USER.save()
                except:
                    print("EMAIL ERROR")
                    Emails.objects.create(to=instance.email, subj=subject, text=text)
                    USER.emailed = True
                    USER.save()
                    pass


class Suppliers(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        verbose_name_plural = "Suppliers"

    def show_active(self):
        if self.is_active == True:
            return self.name
        else:
            return "{} - D/A".format(self.name)

    @classmethod
    def create(cls, name):
        supplier = cls.objects.create(name=name)
        return supplier


class Teams(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        verbose_name_plural = "Teams"

    def show_active(self):
        if self.is_active == True:
            return self.name
        else:
            return "{} - D/A".format(self.name)

    @classmethod
    def create(cls, name):
        team = cls.objects.create(name=name)
        return team


class Reagents(models.Model):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Reagents"
        ordering = ["name"]

    name = models.CharField(max_length=100, unique=True)
    cat_no = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Catalogue Number"
    )
    supplier_def = models.ForeignKey(
        Suppliers,
        on_delete=models.PROTECT,
        verbose_name="Default Supplier",
        blank=True,
        null=True,
    )
    team_def = models.ForeignKey(
        Teams, on_delete=models.PROTECT, verbose_name="Default Team"
    )
    # storage = models.ForeignKey(Storage, on_delete=models.PROTECT, blank=True, null=True)
    count_no = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name="Unopened Items",
    )
    open_no = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name="Opened Items",
    )
    min_count = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name="Minimum Stock Level",
    )
    recipe = models.ForeignKey(
        "Recipe", on_delete=models.PROTECT, blank=True, null=True
    )
    track_vol = models.BooleanField(default=False, verbose_name="Volume Tracked")
    is_active = models.BooleanField(default=True)

    @classmethod
    def create(cls, values):
        with transaction.atomic():
            reagent = cls(**values)
            reagent.save()
            return reagent

    def show_active(self):
        if self.is_active == True:
            return self.name
        else:
            return "{} - D/A".format(self.name)


first = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "J",
    "K",
    "L",
    "M",
    "N",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]
second = [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "J",
    "K",
    "L",
    "M",
    "N",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]
third = [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "J",
    "K",
    "L",
    "M",
    "N",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]
fourth = [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "J",
    "K",
    "L",
    "M",
    "N",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]
potentials = [x for x in itertools.product(first, second, third, fourth)]


class Internal(models.Model):
    def __str__(self):
        return self.batch_number

    class Meta:
        verbose_name_plural = "Stock Numbers"

    batch_number = models.CharField(max_length=4, unique=True)

    @classmethod
    def create(cls, number):
        return cls.objects.create(batch_number="".join(potentials[number]))


class Validation(models.Model):
    def __str__(self):
        return "{} {} - {}".format(
            self.val_run, self.val_date.strftime("%d/%m/%y"), self.val_user.username
        )

    val_date = models.DateField(null=True, blank=True, verbose_name="Date")
    val_run = models.CharField(max_length=25, verbose_name="Run Name")
    val_user = models.ForeignKey(
        User,
        limit_choices_to={"is_active": True},
        on_delete=models.PROTECT,
        verbose_name="User",
    )

    @classmethod
    def new(cls, date, run, user):
        try:
            val_id = cls.objects.get(val_date=date, val_run=run, val_user=user)
        except:
            val_id = cls.objects.create(val_date=date, val_run=run, val_user=user)
        return val_id


class Recipe(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=100, unique=True)
    comp1 = models.ForeignKey(
        Reagents,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name="component 1",
        related_name="component1",
    )
    comp2 = models.ForeignKey(
        Reagents,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name="component 2",
        related_name="component2",
    )
    comp3 = models.ForeignKey(
        Reagents,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name="component 3",
        related_name="component3",
    )
    comp4 = models.ForeignKey(
        Reagents,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name="component 4",
        related_name="component4",
    )
    comp5 = models.ForeignKey(
        Reagents,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name="component 5",
        related_name="component5",
    )
    comp6 = models.ForeignKey(
        Reagents,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name="component 6",
        related_name="component6",
    )
    comp7 = models.ForeignKey(
        Reagents,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name="component 7",
        related_name="component7",
    )
    comp8 = models.ForeignKey(
        Reagents,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name="component 8",
        related_name="component8",
    )
    comp9 = models.ForeignKey(
        Reagents,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name="component 9",
        related_name="component9",
    )
    comp10 = models.ForeignKey(
        Reagents,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name="component 10",
        related_name="component10",
    )
    reagent = models.ForeignKey(
        Reagents,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name="Reagent ID",
        related_name="Reagent_ID",
    )
    shelf_life = models.PositiveIntegerField(verbose_name="Shelf Life (Months)")
    track_vol = models.BooleanField(default=False, verbose_name="Volume Tracked")
    witness_req = models.BooleanField(default=False, verbose_name="Witness Required?")

    @classmethod
    def create(cls, values):
        with transaction.atomic():
            minstock = values["min_count"]
            del values["min_count"]
            def_team = values["team_def"]
            del values["team_def"]
            recipe = cls(**values)
            recipe.save()
            try:
                values = {
                    "name": values["name"],
                    "supplier_def": Suppliers.objects.get(name="Internal"),
                    "recipe": recipe,
                    "min_count": minstock,
                    "track_vol": values["track_vol"],
                    "team_def": def_team,
                }
            except:
                values = {
                    "name": values["name"],
                    "supplier_def": Suppliers.create(name="Internal"),
                    "recipe": recipe,
                    "min_count": minstock,
                    "track_vol": values["track_vol"],
                    "team_def": def_team,
                }
            recipe.reagent = Reagents.create(values)
            recipe.save()

    def length(self):
        count = 0
        for k, v in Recipe.objects.filter(pk=self.id).values().first().items():
            if "comp" in k and v is not None:
                count += 1
        return count

    def liststock(self):
        possibles = []
        for k, v in Recipe.objects.filter(pk=self.id).values().first().items():
            if "comp" in k and v is not None:
                inv_id = v
                in_stock = Inventory.objects.select_related(
                    "supplier", "reagent", "internal", "val", "op_user"
                ).filter(reagent_id=inv_id, finished=False)
                for stock in in_stock:
                    possibles += [stock]
        return possibles

    # function to list components, used in admin view
    def list_comp(self):
        comps = []
        for i in range(1, 11):
            if eval("self.comp{}".format(i)) is not None:
                comps += [eval("self.comp{}".format(i))]
        return comps

    # Function to display default team (which is stored in reagent record, not recipe), used in Admin view
    def Default_Team(self):
        team = Reagents.objects.get(recipe=self.id)
        return str(team.team_def)


class Inventory(models.Model):
    def __str__(self):
        return "{}, Lot:{}, Stock Number:{}".format(
            self.reagent.name, self.lot_no, self.internal
        )

    class Meta:
        verbose_name_plural = "Inventory Items"

    reagent = models.ForeignKey(Reagents, on_delete=models.PROTECT)
    GOOD = "GD"
    DAMAGED_OK = "DU"
    UNUSABLE = "UN"
    INHOUSE = "NA"
    CONDITION_CHOICES = [
        (GOOD, "Good"),
        (INHOUSE, "N/A, Made in House"),
        (DAMAGED_OK, "Damaged - Usable"),
        (UNUSABLE, "Damaged - Not Usable"),
    ]
    internal = models.ForeignKey(
        Internal, on_delete=models.PROTECT, verbose_name="Stock Number"
    )
    supplier = models.ForeignKey(Suppliers, on_delete=models.PROTECT)
    team = models.ForeignKey(Teams, on_delete=models.PROTECT)
    lot_no = models.CharField(max_length=50, verbose_name="Lot Number")
    sol = models.ForeignKey(
        "Solutions", on_delete=models.PROTECT, blank=True, null=True
    )
    po = models.CharField(max_length=20, verbose_name="Purchase Order")
    date_rec = models.DateField(
        default=datetime.date.today, verbose_name="Date Received"
    )
    cond_rec = models.CharField(
        max_length=2,
        choices=CONDITION_CHOICES,
        default=GOOD,
        verbose_name="Condition Received",
    )
    rec_user = models.ForeignKey(
        User,
        limit_choices_to={"is_active": True},
        on_delete=models.PROTECT,
        related_name="1+",
    )
    date_exp = models.DateField(verbose_name="Expiry Date")
    date_op = models.DateField(null=True, blank=True)
    is_op = models.BooleanField(default=False)
    op_user = models.ForeignKey(
        User,
        limit_choices_to={"is_active": True},
        on_delete=models.PROTECT,
        related_name="2+",
        blank=True,
        null=True,
        verbose_name="Opened by",
    )
    val = models.ForeignKey(
        Validation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Validation Run",
    )
    date_fin = models.DateField(null=True, blank=True, verbose_name="Date Finished")
    finished = models.BooleanField(default=False)
    fin_user = models.ForeignKey(
        User,
        limit_choices_to={"is_active": True},
        on_delete=models.PROTECT,
        related_name="3+",
        blank=True,
        null=True,
        verbose_name="Finished By",
    )
    fin_text = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Finished Reason"
    )
    vol_rec = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name="Volume Received (µl)",
        blank=True,
        null=True,
    )
    current_vol = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name="Current Volume (µl)",
        blank=True,
        null=True,
    )
    last_usage = models.ForeignKey(
        "VolUsage", blank=True, null=True, on_delete=models.PROTECT
    )
    witness = models.ForeignKey(
        User,
        limit_choices_to={"is_active": True},
        on_delete=models.PROTECT,
        related_name="4+",
        blank=True,
        null=True,
    )
    accept_reason = models.CharField(
        max_length=150, blank=True, null=True, verbose_name="Acceptance Reason"
    )

    def days_remaining(self):
        return (self.date_exp - datetime.date.today()).days

    @classmethod
    def create(cls, values, user):
        if "witness" not in values.keys():
            values["witness"] = None
        values["rec_user"] = user
        if "num_rec" in values.keys():
            amount = values["num_rec"]
            del values["num_rec"]
        else:
            values["current_vol"] = values["vol_rec"]
            amount = 1
        with transaction.atomic():
            try:
                values["val_id"] = (
                    Inventory.objects.filter(
                        reagent=values["reagent"].id,
                        lot_no=values["lot_no"],
                        val_id__gte=0,
                    )
                    .first()
                    .val_id
                )
            except:
                pass
            if "~" in values["reagent"].name and values["reagent"].recipe is None:
                try:
                    values["val_id"] = Validation.objects.get(
                        val_date=values["date_rec"],
                        val_run="NOT_TO_BE_TESTED",
                        val_user_id=user.id,
                    ).pk
                except:
                    values["val_id"] = Validation.objects.create(
                        val_date=values["date_rec"],
                        val_run="NOT_TO_BE_TESTED",
                        val_user_id=user.id,
                    ).pk
            elif values["reagent"].recipe is not None:
                try:
                    values["val_id"] = Validation.objects.get(
                        val_date=values["date_rec"],
                        val_run="INTERNAL",
                        val_user_id=user.id,
                    ).pk
                except:
                    values["val_id"] = Validation.objects.create(
                        val_date=values["date_rec"],
                        val_run="INTERNAL",
                        val_user_id=user.id,
                    ).pk
            internals = []
            for _ in range(amount):
                inventory = cls(**values)
                try:
                    internal_number = Internal.create(Inventory.objects.last().id)
                except:
                    internal_number = Internal.create(0)
                inventory.internal = internal_number
                internals += [inventory.internal.batch_number]
                if inventory.lot_no == "":
                    inventory.lot_no = "N/A"
                inventory.save()
            reagent = Reagents.objects.get(id=values["reagent"].id)
            if "vol_rec" in values.keys():
                reagent.count_no = F("count_no") + values["vol_rec"]
            else:
                reagent.count_no = F("count_no") + amount
            reagent.save()
            return internals

    @classmethod
    def open(cls, values, item, user):
        with transaction.atomic():
            reagent = Inventory.objects.get(id=item).reagent
            if int(reagent.count_no) == 0:
                open_items = Inventory.objects.filter(
                    is_op=True, finished=False, reagent=reagent
                ).count()
                un_open_items = Inventory.objects.filter(
                    is_op=False, finished=False, reagent=reagent
                ).count()
                reagent.open_no = open_items
                reagent.count_no = un_open_items
                reagent.save()
                reagent.refresh_from_db()
            if reagent.track_vol == False:
                reagent.count_no = F("count_no") - 1
            reagent.open_no = F("open_no") + 1
            reagent.save()
            invitem = Inventory.objects.get(id=item)
            invitem.date_op = values["date_op"]
            invitem.op_user = user
            invitem.is_op = True
            invitem.save()

    @classmethod
    def take_out(
        cls, vol, item, user, reason=None, date=datetime.datetime.now().date(), sol=None
    ):
        with transaction.atomic():
            if reason == "":
                reason = None
            invitem = Inventory.objects.get(id=item)
            start_vol = invitem.current_vol
            invitem.current_vol = F("current_vol") - vol
            invitem.save()
            invitem.refresh_from_db()
            if invitem.current_vol == 0:
                values = {"date_fin": date, "fin_text": "", "vol": vol}
                invitem.finish(values, item, user)
            else:
                reagent = Reagents.objects.get(pk=invitem.reagent_id)
                reagent.count_no = F("count_no") - vol
                reagent.save()
                reagent.refresh_from_db()
                if reagent.count_no < 0:
                    open_items = Inventory.objects.filter(
                        is_op=True, finished=False, reagent=reagent
                    )
                    un_open_items = Inventory.objects.filter(
                        is_op=False, finished=False, reagent=reagent
                    )
                    new_vol = 0
                    for inv_item in open_items:
                        new_vol += inv_item.current_vol
                    reagent.count_no = new_vol
                    reagent.save()
            VolUsage.use(
                item, start_vol, invitem.current_vol, vol, user, sol, reason, date
            )

    @classmethod
    def validate(cls, values, reagent_id, lot, user):

        with transaction.atomic():
            val = Validation.new(values["val_date"], values["val_run"].upper(), user)

            Inventory.objects.filter(reagent=reagent_id, lot_no=lot).update(val_id=val)
            return Inventory.objects.filter(reagent=reagent_id, lot_no=lot, val_id=val)

    @classmethod
    def finish(cls, values, item, user):
        with transaction.atomic():
            invitem = Inventory.objects.get(id=item)
            invitem.fin_user = user
            invitem.fin_text = values["fin_text"]
            invitem.date_fin = values["date_fin"]
            invitem.finished = True
            reagent = Inventory.objects.get(id=item).reagent
            if reagent.track_vol == False and invitem.is_op == False:
                reagent.count_no = F("count_no") - 1
                invitem.save()
                reagent.save()

            elif reagent.track_vol == False and invitem.is_op == True:
                reagent.open_no = F("open_no") - 1
                reagent.save()
                invitem.save()

            elif reagent.track_vol == True:
                if invitem.current_vol != 0:
                    use = VolUsage.use(
                        item,
                        invitem.current_vol,
                        0,
                        invitem.current_vol,
                        user,
                        None,
                        values["date_fin"],
                    )
                    invitem.last_usage = use
                if "vol" in values.keys():
                    reagent.count_no = F("count_no") - values["vol"]
                else:
                    reagent.count_no = F("count_no") - invitem.current_vol
                if invitem.is_op == True:
                    reagent.open_no = F("open_no") - 1
                reagent.save()
                invitem.current_vol = 0
                invitem.save()


class VolUsage(models.Model):
    class Meta:
        verbose_name_plural = "Volume Usage"

    item = models.ForeignKey(Inventory, blank=True, null=True, on_delete=models.PROTECT)
    start = models.DecimalField(max_digits=7, decimal_places=2)
    end = models.DecimalField(max_digits=7, decimal_places=2)
    used = models.DecimalField(max_digits=7, decimal_places=2)
    date = models.DateField(default=datetime.date.today)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    reason = models.CharField(max_length=100, blank=True, null=True)
    sol = models.ForeignKey(
        "Solutions", on_delete=models.PROTECT, blank=True, null=True
    )

    @classmethod
    def use(
        cls,
        item,
        start_vol,
        end_vol,
        volume,
        user,
        sol,
        reason,
        date=datetime.datetime.now().date(),
    ):
        print(reason)
        invitem = Inventory.objects.get(pk=int(item))
        use = VolUsage.objects.create(
            item=invitem,
            start=start_vol,
            end=end_vol,
            used=volume,
            date=date,
            user=user,
            sol=sol,
            reason=reason,
        )
        invitem.last_usage = use
        invitem.save()
        return use


class Solutions(models.Model):
    class Meta:
        verbose_name_plural = "Solutions"

    recipe = models.ForeignKey(
        Recipe, on_delete=models.PROTECT, verbose_name="Recipe Name"
    )
    comp1 = models.ForeignKey(
        Inventory,
        blank=True,
        null=True,
        limit_choices_to={"finished": False},
        on_delete=models.PROTECT,
        related_name="comp1",
    )
    comp2 = models.ForeignKey(
        Inventory,
        blank=True,
        null=True,
        limit_choices_to={"finished": False},
        on_delete=models.PROTECT,
        related_name="comp2",
    )
    comp3 = models.ForeignKey(
        Inventory,
        blank=True,
        null=True,
        limit_choices_to={"finished": False},
        on_delete=models.PROTECT,
        related_name="comp3",
    )
    comp4 = models.ForeignKey(
        Inventory,
        blank=True,
        null=True,
        limit_choices_to={"finished": False},
        on_delete=models.PROTECT,
        related_name="comp4",
    )
    comp5 = models.ForeignKey(
        Inventory,
        blank=True,
        null=True,
        limit_choices_to={"finished": False},
        on_delete=models.PROTECT,
        related_name="comp5",
    )
    comp6 = models.ForeignKey(
        Inventory,
        blank=True,
        null=True,
        limit_choices_to={"finished": False},
        on_delete=models.PROTECT,
        related_name="comp6",
    )
    comp7 = models.ForeignKey(
        Inventory,
        blank=True,
        null=True,
        limit_choices_to={"finished": False},
        on_delete=models.PROTECT,
        related_name="comp7",
    )
    comp8 = models.ForeignKey(
        Inventory,
        blank=True,
        null=True,
        limit_choices_to={"finished": False},
        on_delete=models.PROTECT,
        related_name="comp8",
    )
    comp9 = models.ForeignKey(
        Inventory,
        blank=True,
        null=True,
        limit_choices_to={"finished": False},
        on_delete=models.PROTECT,
        related_name="comp9",
    )
    comp10 = models.ForeignKey(
        Inventory,
        blank=True,
        null=True,
        limit_choices_to={"finished": False},
        on_delete=models.PROTECT,
        related_name="comp10",
    )
    creator_user = models.ForeignKey(
        User,
        limit_choices_to={"is_active": True},
        on_delete=models.PROTECT,
        verbose_name="Created By",
    )
    date_created = models.DateField(default=datetime.date.today)

    @classmethod
    def create(cls, rec, comp_ids, vols_used, vol_made, user, witness, team):
        with transaction.atomic():
            ids = set(comp_ids)
            comps = apps.get_model("stock_web", "Inventory").objects.filter(id__in=ids)
            comps_dict = {}
            for i, comp in enumerate(comps, start=1):

                comps_dict["comp{}".format(i)] = comp
                if comp.is_op == False:
                    values = {
                        "date_op": comp.date_rec,
                    }
                    comp.open(values, comp.pk, user)
            solution = cls.objects.create(
                recipe=rec,
                creator_user=user,
                date_created=datetime.datetime.today(),
                **comps_dict,
            )
            solution.save()
            # Shelf life/Expiry calculations
            start_day = int(datetime.datetime.today().strftime("%d"))
            start_month = int(datetime.datetime.today().strftime("%m")) + rec.shelf_life
            start_year = int(datetime.datetime.today().strftime("%Y"))
            # Checks that adding shelf life to current month doesn't go over 12 months, incremements year if it does
            # while not if used as could be longer than 1 year expiry so need to do multiple checks
            while start_month > 12:
                start_year += 1
                start_month -= 12
            # checks that the day is valid, goes to 1st of next month if it is not
            # e.g making something on 30th Jan with 1 month shelf life gives 30th Feb which is not valid,
            # would become 1st March in this case
            if start_day > monthrange(start_year, start_month)[1]:
                start_day = 1
                start_month += 1
                # rechecks that adding 1 to the month for invalid day hasn't ticked over a year
                if start_month > 12:
                    start_year += 1
                    start_month -= 12
            EXP_DATE = datetime.datetime.strptime(
                "{}/{}/{}".format(start_day, start_month, start_year), "%d/%m/%Y"
            )
            # gets earliest expiry date from components lists
            EARLIEST_EXP = min([x.date_exp for x in comps_dict.values()])
            changed = False
            # if the earliest expiry date is before the shelf life expiry date, set expiry date to that earliest date
            # also sets changed to True so a message can be displayed to the user
            if EARLIEST_EXP < EXP_DATE.date():
                changed = True
                EXP_DATE = EARLIEST_EXP
            values = {
                "date_rec": datetime.datetime.today(),
                "cond_rec": "NA",
                "date_exp": EXP_DATE,
                "sol": solution,
                "po": "N/A",
                "reagent": rec.reagent,
                "supplier": Suppliers.objects.get(name="Internal"),
                "witness": witness,
                "team": Teams.objects.get(pk=int(team)),
            }
            if vol_made == "":
                values["num_rec"] = 1
            else:
                values["vol_rec"] = vol_made
            for item, vol in vols_used.items():
                Inventory.take_out(vol, item, user, sol=solution)
            return Inventory.create(values, user), changed, EXP_DATE

    def list_comp(self):
        comps = []
        for i in range(1, 11):
            if eval("self.comp{}".format(i)) is not None:
                comps += [eval("self.comp{}".format(i))]
        return comps

    # Function to display stock number (which is stored in inventory record, not solution), used in Admin view
    def Stock_Number(self):
        stock_number = Inventory.objects.get(sol=self.id)
        return str(stock_number.internal.batch_number)


class Emails(models.Model):
    class Meta:
        verbose_name_plural = "Emails To Send"

    to = models.TextField(verbose_name="Sent To")
    subj = models.TextField(verbose_name="Subject")
    text = models.TextField(verbose_name="Text")
    sent = models.BooleanField(default=False)


class Comments(models.Model):
    class Meta:
        verbose_name_plural = "Item Comments"

    def __str__(self):
        return f"{self.item} - {self.comment} - {self.user.username} - {self.date_made}"

    date_made = models.DateField(default=datetime.date.today, verbose_name="Date Made")
    user = models.ForeignKey(
        User,
        limit_choices_to={"is_active": True},
        on_delete=models.PROTECT,
    )
    comment = models.TextField(max_length=250, verbose_name="comment")
    item = models.ForeignKey(
        Inventory,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

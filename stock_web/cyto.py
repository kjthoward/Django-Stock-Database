from django.db import transaction
from django.contrib.auth.models import User, Group
from .models import (
    ForceReset,
    Suppliers,
    Teams,
    Reagents,
    Internal,
    Validation,
    Recipe,
    Inventory,
    Solutions,
    VolUsage,
    Comments
)
from decimal import Decimal
import datetime
import os


def ADD_CYTO():
    with transaction.atomic():
        items = []
        suppliers = []
        inventory = []
        with open(
            os.path.join(os.path.dirname(__file__), "cyto_reagents.tsv"), "rt"
        ) as f:
            for line in f:
                items.append(line.strip("\n"))
        with open(
            os.path.join(os.path.dirname(__file__), "cyto_inventory.tsv"), "rt"
        ) as f1:
            for line in f1:
                inventory.append(line.strip("\n"))
        suppliers = set([x.split("\t")[2] for x in items])
        suppliers_count = 0
        reagents_count = 0
        inventory_count = 0
        if not User.objects.filter(username="STOCK FOLDER").exists():
            User.objects.create_user("STOCK FOLDER", "", "password")
        for sup in suppliers:
            if not Suppliers.objects.filter(name=sup).exists():
                Suppliers.create(sup)
                suppliers_count += 1
        for reagent in items:
            name, cata, sup, minimum, vol, team = reagent.split("\t")
            name = name.strip('"')
            if vol == "TRUE":
                vol = True
            else:
                vol = False
            values = {}
            values["name"] = name
            values["cat_no"] = cata
            try:
                values["supplier_def"] = Suppliers.objects.get(name=sup)
                values["team_def"] = Teams.objects.get(name=team)
            except Exception as e:
                print(e)
                print(sup)
            values["min_count"] = Decimal(minimum)
            values["track_vol"] = vol
            if not Reagents.objects.filter(name=name).exists():
                try:
                    Reagents.create(values)
                    reagents_count += 1
                except Exception as e:
                    print(e)
                    print(name)
        for item in inventory:
            (
                reagent,
                conditon,
                supplier,
                team,
                lot,
                purchase,
                date_rec,
                user_rec,
                expiry,
                openned,
                date_op,
                vol_rec,
                vol_used,
                date_val,
                val_run,
                comment,
            ) = item.split("\t")
            values = {}
            if int(openned) == 1:
                openned = True
            else:
                openned = False
            username = User.objects.get(username=user_rec)
            reagent=reagent.strip('"')
            values["vol_rec"] = vol_rec
            values["reagent"] = Reagents.objects.get(name=reagent)
            values["lot_no"] = lot
            values["po"] = purchase
            values["cond_rec"] = conditon
            values["date_rec"] = datetime.datetime.strptime(date_rec, "%d/%m/%Y")
            values["date_exp"] = datetime.datetime.strptime(expiry, "%d/%m/%Y")
            values["supplier"] = Suppliers.objects.get(name=supplier)
            values["team"] = Teams.objects.get(name=team)
            id = Inventory.create(values, username)[0]
            if openned == True:
                inv_item = Inventory.objects.get(internal__batch_number=id)
                inv_item.is_op = True
                inv_item.op_user = username
                inv_item.date_op = datetime.datetime.strptime(date_op, "%d/%m/%Y")
                inv_item.save()
                inv_item.refresh_from_db()
                Inventory.take_out(
                    vol_used, inv_item.pk, username, datetime.datetime.today()
                )
            if date_val != "":
                inv_item = Inventory.objects.get(internal__batch_number=id)
                values = {}
                values["val_date"] = datetime.datetime.strptime(date_val, "%d/%m/%Y")
                values["val_run"] = val_run
                Inventory.validate(values, inv_item.reagent, inv_item.lot_no, username)
            if comment != "":
                inv_item = Inventory.objects.get(internal__batch_number=id)
                comment = Comments.objects.create(user=username, date_made=datetime.datetime.today(), comment=comment, item=inv_item)
            inventory_count += 1
        return suppliers_count, reagents_count, inventory_count

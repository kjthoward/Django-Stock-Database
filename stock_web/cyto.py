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
)
from decimal import Decimal
import os


def ADD_CYTO():
    with transaction.atomic():
        items = []
        suppliers = []
        with open(os.path.join(os.path.dirname(__file__), "cyto.tsv"), "rt") as f:
            for line in f:
                items.append(line.strip("\n"))
        suppliers = set([x.split("\t")[2] for x in items])
        suppliers_count = 0
        reagents_count = 0
        for sup in suppliers:
            if not Suppliers.objects.filter(name=sup).exists():
                Suppliers.create(sup)
                suppliers_count += 1
        for reagent in items:
            name, cata, sup, minimum, vol, team = reagent.split("\t")
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
        return suppliers_count, reagents_count

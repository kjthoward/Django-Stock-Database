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
    Comments,
    Teams,
    VolUsage,
)
from decimal import Decimal
import datetime
import os


def ADD_CYTO():
    with transaction.atomic():
        solutions = []
        sol_count = 0
        with open(
            os.path.join(os.path.dirname(__file__), "solutions.tsv"), "rt"
        ) as f:
            for line in f:
                solutions.append(line.strip("\n"))
        for sol in solutions:
            name, comp1, comp1_vol, witness, date_made, date_exp, volume_made = sol.split("\t")
            name = name.strip('"')
            
            recipe=Recipe.objects.get(name=name)
            comps=[Inventory.objects.get(internal__batch_number=comp1).pk]
            vols_used={Inventory.objects.get(internal__batch_number=comp1).pk:comp1_vol}
            user=User.objects.get(username="STOCK FOLDER")
            witness=User.objects.get(username=witness)
            team=Teams.objects.get(name="CYTO").pk
            item=Inventory.objects.get(internal__batch_number=comp1)
            vol_usage=VolUsage.objects.get(item__pk=comps[0])
            new_start=item.vol_rec-int(comp1_vol)
            new_end=item.vol_rec-vol_usage.used
            new_used=vol_usage.used-int(comp1_vol)
            vol_usage.start=new_start
            vol_usage.used=new_used
            vol_usage.end=new_end
            vol_usage.save()
            
            item.current_vol=item.current_vol+int(comp1_vol)
            item.save()
            sol=Solutions.create(recipe,comps,vols_used,"",user,witness,team)[0][0]
            new_inv=Inventory.objects.get(internal__batch_number=sol)
            date_made=datetime.datetime.strptime(date_made, "%d/%m/%Y")
            new_inv.date_rec=date_made
            new_inv.save()
            new_usage=VolUsage.objects.get(item=item, date=datetime.date.today())
            new_usage.date=date_made
            new_usage.start=item.vol_rec
            new_usage.end=item.vol_rec-int(comp1_vol)
            new_usage.save()
            sol_count+=1
        return sol_count

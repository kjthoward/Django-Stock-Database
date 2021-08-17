from stock_web.models import Inventory, Reagents
from django.db import transaction


def update_counts():
    with transaction.atomic():
        open_items = Inventory.objects.filter(is_op=True, finished=False)
        un_open_items = Inventory.objects.filter(is_op=False, finished=False)
        all_reagents = Reagents.objects.all()
        counts = {}
        for reagent in all_reagents:
            num_open = open_items.filter(reagent=reagent)
            num_unopen = un_open_items.filter(reagent=reagent)
            if reagent.track_vol==False:
                reagent.open_no = num_open.count()
                reagent.count_no = num_unopen.count()
                reagent.save()
            else:
                vol=0
                for item in num_unopen:
                    vol+=item.vol_rec
                for item in num_open:
                    vol+=item.current_vol   
                reagent.open_no = num_open.count()
                reagent.count_no = vol
                reagent.save()

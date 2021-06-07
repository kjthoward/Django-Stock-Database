from stock_web.models import Inventory, Reagents
from django.db import transaction


def update_counts():
    with transaction.atomic():
        open_items = Inventory.objects.filter(is_op=True, finished=False)
        un_open_items = Inventory.objects.filter(is_op=False, finished=False)
        all_reagents = Reagents.objects.all()
        counts = {}
        for reagent in all_reagents:
            num_open = open_items.filter(reagent=reagent).count()
            num_unopen = un_open_items.filter(reagent=reagent).count()
            reagent.open_no = num_open
            reagent.count_no = num_unopen
            reagent.save()

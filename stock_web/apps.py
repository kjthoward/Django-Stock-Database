from django.apps import AppConfig


class StockWebConfig(AppConfig):
    name = 'stock_web'
    verbose_name = "Stock Database Tables"

    def ready(self):
        from email_scheduler import scheduler
        scheduler.start()
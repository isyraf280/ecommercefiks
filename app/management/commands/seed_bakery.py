from django.core.management.base import BaseCommand
import seed_bakery

class Command(BaseCommand):
    help = 'Seeder data dummy produk dan kategori Roti & Bakery Lesaffrone'

    def handle(self, *args, **options):
        seed_bakery.seed()


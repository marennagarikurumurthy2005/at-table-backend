from django.core.management.base import BaseCommand
from canteen.models import MenuItem


class Command(BaseCommand):
    help = 'Seed the database with menu items'

    def handle(self, *args, **options):
        menu_items = [
            # Breakfast
            {
                'name': 'Paneer Dosa',
                'description': 'Crispy dosa filled with paneer and spices',
                'category': 'breakfast',
                'price': 120.00,
                'image_url': '/paneer-dosa.jpg',
                'is_available': True,
                'rating': 4.5,
                'reviews_count': 45,
            },
            {
                'name': 'Idli Sambar',
                'description': 'Soft idli served with sambar and chutney',
                'category': 'breakfast',
                'price': 80.00,
                'image_url': '/idli-sambar.png',
                'is_available': True,
                'rating': 4.3,
                'reviews_count': 32,
            },
            # Lunch
            {
                'name': 'Flavorful Biryani',
                'description': 'Aromatic biryani with tender meat and basmati rice',
                'category': 'lunch',
                'price': 250.00,
                'image_url': '/flavorful-biryani.png',
                'is_available': True,
                'rating': 4.7,
                'reviews_count': 78,
            },
            {
                'name': 'Butter Chicken',
                'description': 'Creamy butter chicken with naan bread',
                'category': 'lunch',
                'price': 280.00,
                'image_url': '/placeholder.svg?height=200&width=200',
                'is_available': True,
                'rating': 4.6,
                'reviews_count': 65,
            },
            # Snacks
            {
                'name': 'Samosa',
                'description': 'Crispy samosa with potato and peas filling',
                'category': 'snacks',
                'price': 30.00,
                'image_url': '/placeholder.svg?height=200&width=200',
                'is_available': True,
                'rating': 4.2,
                'reviews_count': 28,
            },
            {
                'name': 'Pakora',
                'description': 'Crispy vegetable pakora with mint chutney',
                'category': 'snacks',
                'price': 50.00,
                'image_url': '/placeholder.svg?height=200&width=200',
                'is_available': True,
                'rating': 4.1,
                'reviews_count': 22,
            },
            # Desserts
            {
                'name': 'Gulab Jamun',
                'description': 'Soft gulab jamun in sugar syrup',
                'category': 'desserts',
                'price': 60.00,
                'image_url': '/gulab-jamun.png',
                'is_available': True,
                'rating': 4.4,
                'reviews_count': 35,
            },
            {
                'name': 'Kheer',
                'description': 'Creamy rice pudding with nuts and cardamom',
                'category': 'desserts',
                'price': 70.00,
                'image_url': '/kheer-dessert.jpg',
                'is_available': True,
                'rating': 4.5,
                'reviews_count': 40,
            },
            # Beverages
            {
                'name': 'Masala Chai',
                'description': 'Hot masala tea with spices',
                'category': 'beverages',
                'price': 20.00,
                'image_url': '/placeholder.svg?height=200&width=200',
                'is_available': True,
                'rating': 4.3,
                'reviews_count': 50,
            },
            {
                'name': 'Mango Lassi',
                'description': 'Refreshing mango yogurt drink',
                'category': 'beverages',
                'price': 40.00,
                'image_url': '/placeholder.svg?height=200&width=200',
                'is_available': True,
                'rating': 4.6,
                'reviews_count': 55,
            },
        ]

        for item_data in menu_items:
            MenuItem.objects.get_or_create(**item_data)

        self.stdout.write(self.style.SUCCESS('Successfully seeded menu items'))

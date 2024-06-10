from django.db import models

day_choice = (
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
)

category_choice = (
    ('breakfast', 'breakfast'),
    ('lunch', 'lunch'),
    ('bar', 'bar'),
    ('snack', 'snack'),
    ('dessert', 'dessert'),
    ('proper nutrition', 'proper nutrition'),
)


class Food(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=100, choices=category_choice, default='breakfast')
    day = models.CharField(max_length=100, choices=day_choice, default='Monday')

    def __str__(self):
        return self.name


class Photo(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='photos')

    def __str__(self):
        return self.food.name

from django.db import models

rating_choice = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
)


class Complaint(models.Model):
    rating = models.IntegerField(choices=rating_choice)
    created_at = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=13, null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.rating

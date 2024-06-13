from django.db import models

from users.models import User

rating_choice = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
)


class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='complaints', null=True)
    rating = models.IntegerField(choices=rating_choice)
    created_at = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=13, null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.rating

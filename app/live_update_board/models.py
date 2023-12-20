from django.db import models, connection
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class TeamScore(models.Model):
    score = models.TextField(default='')
    team = models.TextField(default='')
    def __str__(self):
        return self.team_name

class TeamItems(models.Model):
    team = models.TextField(default='')
    item = models.TextField(default='')
    item_id = models.IntegerField(default=0,unique=True)
    points = models.IntegerField(default=0)
    position = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.team
    
    
# Define a custom function to be called by triggers
# def update_team_score(sender, instance, **kwargs):
#     if kwargs['created']:
#         operation = 'INSERT'
#     else:
#         operation = 'UPDATE'

#     # Execute a custom SQL statement when a new record is inserted or updated
#     with connection.cursor() as cursor:
#         cursor.execute("INSERT INTO live_update_board_teamscoreaudit (operation, team_id, score) VALUES (%s, %s, %s)", [operation, instance.team, instance.score])

# Create a database table to store the audit log
# This table should have fields for operation, team_id, and score, and a timestamp if desired
# This is a simplified example without a timestamp field
class TeamScoreAudit(models.Model):
    operation = models.CharField(max_length=10)
    team_id = models.TextField()
    score = models.TextField()

# Connect the custom function to the post_save signal
#post_save.connect(update_team_score, sender=TeamScore)

# Connect the custom function to the post_delete signal
# @receiver(post_delete, sender=TeamScore)
# def delete_team_score(sender, instance, **kwargs):
#     with connection.cursor() as cursor:
#         cursor.execute("INSERT INTO live_update_board_teamscoreaudit (operation, team_id, score) VALUES ('DELETE', %s, %s)", [instance.team, instance.score])
        

# def update_team_item(sender, instance, **kwargs):
#     if kwargs['created']:
#         operation = 'INSERT'
#     else:
#         operation = 'UPDATE'

#     # Execute a custom SQL statement when a new record is inserted or updated
#     with connection.cursor() as cursor:
#         cursor.execute("INSERT INTO live_update_board_teamitemaudit (operation, team_id, score) VALUES (%s, %s, %s)", [operation, instance.team, instance.points])

# Create a database table to store the audit log
# This table should have fields for operation, team_id, and score, and a timestamp if desired
# This is a simplified example without a timestamp field
class TeamItemAudit(models.Model):
    operation = models.CharField(max_length=10)
    team_id = models.TextField()
    score = models.TextField()

# Connect the custom function to the post_save signal
# post_save.connect(update_team_item, sender=TeamItems)

# # Connect the custom function to the post_delete signal
# @receiver(post_delete, sender=TeamItems)
# def delete_team_score(sender, instance, **kwargs):
#     with connection.cursor() as cursor:
#         cursor.execute("INSERT INTO live_update_board_teamitemaudit (operation, team_id, score) VALUES ('DELETE', %s, %s)", [instance.team, instance.points])
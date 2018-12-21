from django.db import models

import datetime

class File_Browser_Stats(models.Model):

    Rendered_Tree_State= models.TextField(max_length=4000000, default='')
    insertion = models.DateTimeField('date parsed')

    def __init__(self):
        pass

    @staticmethod
    def save_file_browser_status(tree_state):

        save_obj = File_Browser_Stats
        save_obj.Rendered_Tree_State = tree_state
        save_obj.insertion = datetime.now()
        save_obj.save()

    @staticmethod
    def load_filebrowser_status():

        recent_save = File_Browser_Stats.objects.order_by('-insertion')[0]
        return recent_save.Rendered_Tree_State

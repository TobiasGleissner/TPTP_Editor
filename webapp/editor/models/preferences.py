import copy
import json
from django.db import models
from django.conf import settings

# This is for non-user mode only
class Preferences(models.Model):
    preferences = models.TextField()

    @staticmethod
    def load(received_data):
        pref_object = Preferences.objects.last()
        pref_string = None
        if pref_object == None:
            pref_string = '{}'
        else:
            pref_string = pref_object.preferences

        # make sure an entry exists for all preferences
        pref_json = json.loads(pref_string)
        if not 'local_prover' in pref_json: # type(pref_json['local_prover']) != list:
            pref_json['local_prover'] = []
        if not 'embedding' in pref_json: #type(pref_json['embedding']) != list:
            pref_json['embedding'] = []
        if not 'latex_configurations' in pref_json: #type(pref_json['latex_configurations']) != list:
            pref_json['latex_configurations'] = []

        send_data = {}
        send_data['status'] = 'ok'
        send_data['preferences'] = json.dumps(pref_json)
        send_data['predefined'] = json.dumps(Preferences.get_predefined())
        return send_data

    @staticmethod
    def store(received_data):
        # make sure if local provers are allowed
        prefs = json.loads(received_data['preferences'])
        if not settings.CUSTOM['allow_custom_local_provers']:
            prefs['local_prover'] = []

        Preferences.objects.create(preferences=json.dumps(prefs))
        send_data = {}
        send_data['status'] = "ok"
        return send_data

    @staticmethod
    def get_predefined():
        """
        Sends all predefined preferences set by the admin that can not be altered by the user
        :param received_data:
        :return:
        """

        # gather latex export configurations
        latex_export_configurations = []
        for c in settings.CUSTOM['predefined_latex_export_configurations']:
            name = c['name']
            filename = c['file']
            with open(filename, 'r') as fd:
                content = fd.read()
                latex_export_configurations.append({
                    "name": name,
                    "configuration": content
                })

        # mask predefined local provers
        local_predefined_provers = []
        for p in settings.CUSTOM['predefined_local_provers']:
            newp = copy.deepcopy(p)
            newp['cmd'] = ""
            newp['parameters'] = ""
            local_predefined_provers.append(newp)

        # put all predefined settings in a dictionary
        pre = {
            "allow_custom_local_provers": settings.CUSTOM['allow_custom_local_provers'],
            "local_provers": local_predefined_provers,
            "embedding": settings.CUSTOM['predefined_embeddings'],
            "latex_export_configurations": latex_export_configurations
        }
        return pre

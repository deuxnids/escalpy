from mailchimp3 import MailChimp


class Mailchimp:
    def __init__(self, key, username):
        self.key = key
        self.username = username
        self.client = MailChimp(key, username)

    def send_emails(self, listname="Escalp", template="escalp_weekly"):
        list_id = self.get_list_id(listname)
        template_id = self.get_template_id(template)

        campaign_data = {"settings": {"title": "Weekly Escalp",
                                      "subject_line": "Weekly Escalp digest",
                                      "from_name": "Escalp Team",
                                      "template_id" : template_id ,
                                      "reply_to": "denis@metrailler.ch",
                                      },
                         "recipients": {"list_id": list_id},
                         "type": "regular"}

        camp = self.client.campaigns.create(campaign_data)

        data = {}
        result = self.client.campaigns.content.update(campaign_id=camp["id"], data=data)
        self.client.campaigns.actions.send(camp["id"])

    def get_list_id(self, name):

        for list in self.client.lists.all(get_all=True, fields="lists.name,lists.id")["lists"]:
            if list["name"] == name:
                return list["id"]

    def get_template_id(self, name):
        for d in self.client.templates.all()["templates"]:
            if d["name"] == name:
                return d["id"]

    def update_member(self, data, list_id):
        """
        data = {"email@ssad.com": []}
        """
        for email_address in data.keys():
            user_data = {u'merge_fields': {}}
            for i, outing in enumerate(data[email_address]):
                user_data[u'merge_fields']["OUTING_%i" % (i+1)] = outing["txt"]
                user_data[u'merge_fields']["OUTING_L%i" % (i+1)] = outing["link"]
            self.client.lists.members.update(list_id, subscriber_hash=email_address, data=user_data)

import base64
from diffgram.core.core import Project

def create_global_attribute_preprocessing():
    """ pre assign diffgram attribute values """
    return [{

        "type": "global",
        'attribute_groups': {

            125:
                {
                    "display_name": 'Back',
                    "id": 99766,
                    "name": 'Back',
                    "selected": True
                }
        }
    }]


project = Project(
project_string_id = "diffgram-testing-e2e",
client_id = "LIVE__8cufj2fm3yy3sd0euqtu",
client_secret = "pxiypdk47a9wua6fadoy9y25vqayl9y4p4aoy443vtb5a1nn070gtf1284ii"
)

auth = base64.b64encode((diffgram_client.client_id + ":" + diffgram_client.client_secret).encode())

url = f"{diffgram_client.host}/api/walrus/v1/project/{diffgram_client.project_string_id}/input/packet"

import requests

print(create_global_attribute_preprocessing())
payload = {
    'file_id': 44,  # 567121,
    'instance_list': create_global_attribute_preprocessing(),
    'mode': 'update',  # Update will append, use update_with_existing to delete existing instances and replace them.

}
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Basic {auth.decode()}"
}

response = requests.post(url, json = payload, headers = headers)

print(response.text)
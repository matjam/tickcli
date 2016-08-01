import requests
import os
import json

class TickError(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class TickSession:
    task_cache = {}
    config = None
    config_path = None
    user_agent = 'python-tickspot-api-client/0.0.1 (chrome@stupendous.net)'

    def __init__(self, config_path):
        self.config_path = config_path
        if os.path.isfile(self.config_path):
            with open(self.config_path) as config_file:
                self.config = json.load(config_file)
        else:
            email = raw_input('Enter your tickspot login: ')
            password = raw_input('Enter your tickspot password: ')
            try:
                result = self.login(email, password)
            except TickError as e:
                print e
                exit(2)
            self.config = result[0]
            self.save_config()

    def save_config(self):
        with open(self.config_path, 'w') as config_file:
            json.dump(self.config, config_file)

    def login(self, email, password):
        url = 'https://www.tickspot.com/api/v2/roles.json'
        headers = {'User-Agent': self.user_agent}
        r = requests.get (url, headers=headers, auth=(email, password))
        if r.status_code != 200:
            raise TickError('Invalid Credentials')
        return r.json()

    def get_projects(self):
        url = 'https://www.tickspot.com/%d/api/v2/projects.json' % int(self.config['subscription_id'])
        headers = {'User-Agent': self.user_agent,
                   'Authorization': 'Token token=' + self.config['api_token']}
        r = requests.get(url, headers=headers)
        return r.json()

    def get_project(self, project_id):
        url = 'https://www.tickspot.com/%d/api/v2/projects/%d.json' % (int(self.config['subscription_id']), project_id)
        headers = {'User-Agent': self.user_agent,
                   'Authorization': 'Token token=' + self.config['api_token']}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise TickError('Invalid project')
        return r.json()

    def get_tasks(self, project_id=None):
        url = None
        if project_id == None:
            url = 'https://www.tickspot.com/%d/api/v2/tasks.json' % int(self.config['subscription_id'])
        else:
            url = 'https://www.tickspot.com/%d/api/v2/projects/%d/tasks.json' % (int(self.config['subscription_id']), project_id)

        headers = {'User-Agent': self.user_agent,
                   'Authorization': 'Token token=' + self.config['api_token']}

        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise TickError('Invalid project_id')
        return r.json()

    def get_task(self, task_id=None):
        if task_id == None:
            raise TickError('No task_id supplied')

        if task_id in self.task_cache:
            return self.task_cache[task_id]

        url = 'https://www.tickspot.com/%d/api/v2/tasks/%d.json' % (int(self.config['subscription_id']), task_id)

        headers = {'User-Agent': self.user_agent,
                   'Authorization': 'Token token=' + self.config['api_token']}

        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise TickError('Invalid task')

        self.task_cache[task_id] = r.json()
        return r.json()

    def get_users(self):
        url = 'https://www.tickspot.com/%d/api/v2/users.json' % (int(self.config['subscription_id']))
        headers = {'User-Agent': self.user_agent,
                   'Authorization': 'Token token=' + self.config['api_token']}
        r = requests.get(url, headers=headers)
        return r.json()

    def get_entries(self, start_date, end_date):
        page = 1
        entries = None

        while True:
            params = {'start_date': start_date,
                    'end_date': end_date,
                    'page': page}

            url = 'https://www.tickspot.com/%d/api/v2/entries.json' % (int(self.config['subscription_id']))
            headers = {'User-Agent': self.user_agent,
                    'Authorization': 'Token token=' + self.config['api_token']}
            r = requests.get(url, headers=headers, params=params)
            result_entries = r.json()

            if entries is not None:
                for entry in result_entries:
                    entries.append(entry)
            else:
                entries = result_entries

            page += 1
            if len(result_entries) == 0:
                break

        return entries

    def create_entry(self, date, hours, notes, task_id, user_id):
        url = 'https://www.tickspot.com/%d/api/v2/entries.json' % (int(self.config['subscription_id']))
        headers = {'User-Agent': self.user_agent,
                   'Authorization': 'Token token=' + self.config['api_token']}

        payload = {'date': date,
                   'hours': hours,
                   'notes': notes,
                   'task_id': task_id,
                   'user_id': user_id }

        r = requests.post(url, headers=headers, json=payload)
        return r.json()
    def delete_entry(self, entry_id):
        url = 'https://www.tickspot.com/%d/api/v2/entries/%d.json' % (int(self.config['subscription_id']), int(entry_id))
        headers = {'User-Agent': self.user_agent,
                   'Authorization': 'Token token=' + self.config['api_token']}
        r = requests.delete(url, headers=headers)
        if r.status_code != 204:
            raise TickError('Invalid entry')

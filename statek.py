# -*- coding: utf-8 -*-
"""
@author: Ales Podolnik
"""

import requests
import re

# Utility for downloading data from Statek. Uses requests.session to keep itself logged in
class StatekSlave:
    
    # create an instance with login and password
    def __init__(self, login, password):
        self.base_url = "https://statek.seslost.cz/"
        
        # get login page
        # login page contains some useful fields that are needed to log in
        uri_login = "prihlaseni"
        self.session = requests.session()
        login_html = self.Get(uri_login)

        # parse the data out, there should be only one
        pattern = r'<form.+?<input name="utf8" type="hidden" value="(.+?)".+?"authenticity_token".+?value="(.+?)" \/>.+?<\/form>'
        m = re.findall(pattern, login_html)
        server_data = m[0];
        
        login_data = {"utf8": server_data[0], "authenticity_token": server_data[1], 'identification_session[login]': login, 'identification_session[password]': password, 'commit': 'Přihlásit'}

        self.Post(uri_login, login_data)
        
        # if the login has failed, you're screwed, 'cause I'm too lazy to check it
        print "Statek slave at your bidding."
        pass

    # get method
    def Get(self, page_uri):
        url = self.base_url + page_uri
        page = self.session.get(url)
        # return as one line
        return page.text.replace('\n', '').replace('\r', '')

    # set method, obviously
    def Post(self, page_uri, post_data):
        url = self.base_url + page_uri
        page = self.session.post(url, post_data)
        # return as one line        
        return page.text.replace('\n', '').replace('\r', '')
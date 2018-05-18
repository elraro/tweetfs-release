#!/usr/bin/env python

import tweepy

# From your app settings page
CONSUMER_KEY = "0cXCBpiPKGVlVGNYdxwMvX7tv"
CONSUMER_SECRET = "nnsOol1EZi7gyqsF9EO5fDw7ALtjlS1b86AK1VKhUpv3sxdG84"

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.secure = True
auth_url = auth.get_authorization_url()

print 'Please authorize: ' + auth_url

verifier = raw_input('PIN: ').strip()

auth.get_access_token(verifier)

print "ACCESS_KEY = '%s'" % auth.access_token
print "ACCESS_SECRET = '%s'" % auth.access_token_secret

import urllib.request, urllib.error, urllib.parse
import json
from collections import deque

def image_search(self, e):
    searchterm = urllib.parse.quote(e.input)
    key = self.botconfig["APIkeys"]["ischapi"]
    cx = self.botconfig["APIkeys"]["gsearchcx"]
    url = 'https://www.googleapis.com/customsearch/v1?key={}&cx={}&q={}&searchType=image'
    url = url.format(key, cx, searchterm)
    if e.source.name != "nsfw":
        url += "&safe=medium"

    try:
        request = urllib.request.Request(url, None, {'Referer': 'http://irc.00id.net'})
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as err:
        self.logger.exception("Exception in google_url: {}".format(err))
        self.logger.exception("Body is: {}".format(err.read()))

    results_json = json.loads(response.read().decode('utf-8'))
    results = results_json['items']
 #   image_flip.last10.append((e.message.id, results,0))
    image_flip.results[e.message.id] = (results, 0)
    image_flip.current = 0
    e.self_reaction = ['\u2b05', '\u27a1']

    e.output = results[0]['link']
    e.allowembed = True
    return e

image_search.command = "!image"

# this works by checking if the reaction is < or > and going to the next/last result
# the results are based on the line above that sets an attr on this with the last !image search
# this is a bit of a hack... I really need to rewrite some shens to keep state
# that way you can flip any recent !image and the bot will flip the right context
# the method also directly edits itself using the client which is kind of odd 
# instead of going through a common 'out' from the rest of the bot but I'm not even sure how to improve that

async def image_flip(client, reaction, user, was_removed):
    '''paginates the image search based on the last !image command
       Note that we don't actually care if the reaction was added or removed'''
    if user == client.user:
        return


    # get our response to this image request and edit it
    rid = None
    rto = None
    rtolist = []
    for responseto, resp in client.lastresponses:
        # a housecleaning hack to clean our own dict
        rtolist.append(responseto)
        if reaction.message.id == resp.id:
            rid = resp
            rto = responseto
    # a housecleaning hack to clean our own dict
    for key in image_flip.results:
        print(key)
        if key not in rtolist:
            image_flip.results.pop(key, None)
    if not rid:
        return
    images, current = image_flip.results[rto]

    if reaction.emoji == '\u27a1':
        current += 1
    elif reaction.emoji == '\u2b05':
        current -= 1
    current = max(0, min(9, current))
    image_flip.results[rto] = (images, current)
    image = images[current]['link']
    await client.edit_message(rid, image)


#image_flip.last10 = deque((,,), maxlen=10)
image_flip.reaction_listener = True
image_flip.current = 0
image_flip.results = {}




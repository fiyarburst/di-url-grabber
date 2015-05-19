"""

pie dye

source canonical

"""
import requests
import sys
import argparse
import pickle

base_url = 'http://listen.di.fm/'
urls_prem = {'aac': {}, 'mp3': {}}
urls_prem['aac'][40] = 'premium_low'
urls_prem['aac'][64] = 'premium_medium'
urls_prem['aac'][128] = 'premium'
urls_prem['mp3'][256] = 'premium_high'

# Mapping of free URLs
urls_free = {'aac': {}, 'mp3': {}}
urls_free['aac'][40] = 'public2'
urls_free['aac'][64] = 'public1'
urls_free['mp3'][96] = 'public3'


def dump_listing(urls):
    op = []
    for stream_format in urls.keys():
        for bitrate in urls[stream_format].keys():
            op.append(urls[stream_format][bitrate])
    return op

width=16

def tabulate_listing(urls, verbose=False):
    for stream_format in urls.keys():
        for bitrate in urls[stream_format].keys():
            listing = urls[stream_format][bitrate]
            if verbose:
                print "".join(w.ljust(16) for w in [listing, stream_format, str(bitrate), base_url+listing])
            else:
                print listing


def listings(premium_urls=True, free_urls=False, verbose=False):
    """
    enumerates the internal list of urls. TODO: fetch the list externally
    """
    if verbose:
        print "".join(word.ljust(width) for word in ['listing','format','bitrate','url'])
    if premium_urls:
        tabulate_listing(urls_prem, verbose)
    if free_urls:
        tabulate_listing(urls_free, verbose)
    

def fetch_playlists(listing_name):
    """
    gets json data based on listing_name, like 'premium' or 'public3'
    """
    if listing_name is None:
        raise NameError("error 'playlists': no listing name given")
    r = requests.get(base_url+listing_name)
    if r.raise_for_status():
        raise NameError("error: listing " + listing_name)
    else:
        return r.json()

import os
import cPickle as pickle
# inp is currently one variable, probs not the right way to do this. either 
# a less generic cached_urls call or a more generic one that can allow lists
def cached_data(func, inp, refresh):
    cache_path = "cached-urls.pickle"
    if not os.path.exists(cache_path) or refresh:
        result = func(inp)
        cache_file = open (cache_path,'wb')
        pickle.dump(result, cache_file, protocol=1)
        cache_file.close()
    return pickle.load(open(cache_path,'rb'))

def load_key():
    key = None

    if os.path.exists('key'):
        with open('key', 'r') as f:
            key = f.readline().strip()
    return key

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='fetches info and generates URLs over DI.fm playlist listings.')
    url_choices = dump_listing(urls_prem) + dump_listing(urls_free)
#    parser.add_argument('listings', choices=url_choices, help="stream format")
    # TODO: prevent from combining -l and playlist/keyword options?
    # TODO: make sure that it pulls the right stream listing. right now, 
    #    if it caches 'premium', then a search for 'public2' will use the cached premium results.

    parser.add_argument('-l', action="store_true", help='gets you a list of the streams')
    parser.add_argument('-ls', action="store_true", help='gets you a list of the streams and more details')
    parser.add_argument('playlists', choices=url_choices, nargs='?')
    parser.add_argument('keyword', nargs='?')
    parser.add_argument('-r', '--refresh',  help="ignore cached urls and grab new ones from server", action="store_true")
    parser.add_argument('-k', '--key', help="store your key in a local file called 'key'.")
    parser.add_argument('-n', '--names', help="just the names", action="store_true")
    parser.add_argument('-nk', '--no-key', help="just the urls no keys", action="store_true")
    args = parser.parse_args()

    if args.key:
        with open('key','w') as f:
            f.write(args.key+"\n")
    if args.ls or args.l:
        listings(True, True, args.ls)

    if args.playlists:
        # load saved
        
        playlists = {}
        if not args.no_key:
            key = load_key()
        else:
            key = None
        json = cached_data(fetch_playlists, args.playlists, args.refresh)
        for entry in json:
            name = entry['name'].lower()
            url = entry['playlist'].lower()

            playlists[name] = url

            if not args.keyword:

                print url

            elif args.keyword.lower() in name:
                if args.names:
                    print name
                elif 'premium' in args.playlists and key:
                    print url+"?listen_key="+key
                else:
                    print url


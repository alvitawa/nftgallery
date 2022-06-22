#!/bin/env python3

import requests
import json
import glob
import tqdm
import time

key = "coinrankingaedcf868ba2a570d3ccf30bfc92a38b20fa02daed26d86cc"
head = {"x-access-token": key}

def get_page(page=0, limit=100):
    url = "https://api.coinranking.com/v2/nfts"
    querystring = {"orderBy":"priceInDollar", "orderDirection":"desc", "offset":str(page), "limit":str(limit)}

    response = json.loads(requests.request("GET", url, params=querystring, headers=head).text)

    if response['status'] != 'success':
        raise Exception("Error status")

    return response['data']['nfts']

def get_nft_meta(nft):
    url = f"https://api.coinranking.com/v2/nft/{nft['id']}"
    response = json.loads(requests.request("GET", url, headers=head).text)

    if response['status'] != 'success':
        raise Exception("Error status")

    return response['data']['nft']

def get_index(path,name):
    filenames = glob.glob(f"{path}{name}*.json")
    return max((int(f[len(path)+len(name):-5]) for f in filenames), default=-1)

def get_all():
    all = []
    retry = []

    for page in tqdm.tqdm(range(301), desc="Retrieving nfts"):
        try:
            all += get_page(page)
        except Exception as e:
            retry.append(page)
        time.sleep(0.300)
    for page in tqdm.tqdm(retry, desc="Retrying ntfs"):
        try:
            all += get_page(page)
        except Exception as e:
            print(f"Failed to get page {page}: {e}\n\n Not retrying again.")
        time.sleep(0.400)

    return all

def get_meta_all(all):
    
    meta_all = []
    retry = []
    for nft in tqdm.tqdm(all, desc="Retrieving metadata"):
        try:
            meta = get_nft_meta(nft)
            meta_all.append(meta)
        except Exception:
            retry.append(nft)
        time.sleep(0.250)

    for nft in tqdm.tqdm(retry, desc="Retrying metadata"):
        try:
            meta = get_nft_meta(nft)
            meta_all.append(meta)
        except Exception as e:
            print(f"Failed to get meta {nft['id']}: {e}\n\n Not retrying again.")
        time.sleep(0.400)

    return meta_all

def save(all, name):
    i = get_index('data/', name) + 1
    with open(f'data/{name}{i}.json', 'w') as f:
        json.dump(all, f)

def load(name):
    i = get_index('data/', name)
    with open(f'data/{name}{i}.json', 'r') as f:
        return json.load(f)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--noall', action='store_true', help="Set to use the existing list of nft's instead of requesting a new one.")
    parser.add_argument('--nometa', action='store_true', help="Set to use the existing metadata instead of re-requesting it.")
    args = parser.parse_args()

    if not args.noall:
        all = get_all()
        save(all, 'all')
    else:
        all = load('all')

    if not args.nometa:
        meta_all = get_meta_all(all)
        save(meta_all, 'meta')
    else:
        meta_all = load('meta')

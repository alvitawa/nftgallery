#!/bin/env python3

import os
import scraper

from jinja2 import *


def write(path, html):
    with open(f"dev/{path}", "w") as f:
        f.write(html)

print("Building...")

# all_ = (
#     one
#     for one in scraper.load("meta")
#     if "metadata" in one
#     and "image" in one
#     or (
#         "image" in one["metadata"]
#         and one["metadata"]["image"] is not None
#         and one["metadata"]["image"][:4] != "ipfs"
#     )
#     and one["dappName"]
#     not in {
#         "Sorare",
#         "Axie Infinity",
#         "Cryptovoxels Parcel",
#         "Cometh Spaceships",
#         "Unstoppable Domains",
#         "Somnium Space",
#     }
# )


stats = {
    'ipfs': 0,
    'ipfs_still': 0,
    'meta_image': 0,
    'still_image': 0,
}
all = []
img_urls = set()
for i, one in enumerate(scraper.load("meta")):
    if one["dappName"] in {
        "Sorare",
        "Axie Infinity",
        "Cryptovoxels Parcel",
        "Cometh Spaceships",
        "Unstoppable Domains",
        "Somnium Space",
        "Decentraland",
        "CryptoKitties",
        "Rarible",
        "Ethereum Name Service"
    }:
        continue

    if (
        "metadata" in one
        and "image" in one["metadata"]
        and one["metadata"]["image"] is not None
    ):
        if one["metadata"]["image"][:4] != "ipfs":
            url = one["metadata"]["image"]
            stats['meta_image'] += 1
        elif "image" in one and one["image"] is not None:
            continue
            url = one["image"] #+ "?size=autox860"
            stats['ipfs'] += 1
            stats['ipfs_still'] += 1
        else:
            stats['ipfs'] += 1
    elif "image" in one and one["image"] is not None:
        url = one["image"] #+ "?size=autox860"
        stats['still_image'] += 1
    else:
        continue

    if one["name"] is None:
        one["name"] = ""

    if one["dappName"] in {'Autoglyphs'}:
        one["invert"] = True
    else:
        one["invert"] = False

    if url not in img_urls:
        img_urls.add(url)
        one["image_url"] = url
        all.append(one)

print(f"Stats: {stats}")
print(f"{len(all)} nft's")

## Generate all templates first
loader = FileSystemLoader(searchpath="./templates/")
env = Environment(loader=loader)
env.filters["dollarfmt"] = lambda x: f"${int(float(x)):,}"
env.filters["clip"] = lambda x, n=60: x[:n] + ("..." if len(x) > n else "")


nft = env.get_template("nft.html")

lists = []
for page in range(len(all) // 10 + 1):
    lists.append(nft.render(nfts=all[page * 10 : (page + 1) * 10]))


index = env.get_template("index.html").render(total=len(lists))


# Write after everything generated succesfully
os.system("rm -rf dev/*")

for i, list_ in enumerate(lists):
    write(f"list{i}.html", list_)

write("index.html", index)

os.system("cp static/* dev/")

print("Done.")

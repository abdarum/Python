#!/usr/bin/env python2
import json
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("input", help="JSON File from Trello", type=str)
parser.add_argument("output", help="File to output to", type=str)
parser.add_help = True
args = parser.parse_args()


print("Reading Data...")
with open(os.path.abspath(args.input), 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Found {} cards in {} lists.".format(len(data['cards']), len(data['lists'])))
print("Parsing...")

lists = {l['id']: l['name'] for l in data['lists']}
users = {u['id']: u['fullName'] for u in data['members']}
labels = {l['id']: l['name'] for l in data['labels']}

parsed_cards = [{
    "name": c['name'],
    "list": lists[c['idList']],
    "description": c['desc'],
    "members": [u for k, u in users.items() if k in c['idMembers']],
    "labels": [l for k, l in labels.items() if k in c['idLabels']]
} for c in data['cards']]

output = {
    "board_data": {
        "name": data['name'],
        "url": data['shortUrl']
    },
    "cards": parsed_cards
}

with open(os.path.abspath(args.output), 'w', ) as f:
    json.dump(output, f, indent=4)

print("Output to {}!s".format(os.path.abspath(args.output)))
print("Please visit https://json-csv.com/ to convert the output to CSV.")

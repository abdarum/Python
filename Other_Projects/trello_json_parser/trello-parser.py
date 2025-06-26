#!/usr/bin/env python2
import json
import os
import argparse
from typing import Self


class TrelloJsonParser:
    class JSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if hasattr(obj, 'to_json'):
                return obj.to_json()
            if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
                return super().default(obj)
            return obj.__dict__

    class Checklist:
        class CheckItem:
            def __init__(
                self,
                name: str,
                state: str,
                pos: int,
            ):
                self.name = name
                self.state = state
                self.pos = pos

            def to_json(self) -> dict:
                return {
                    "name": self.name,
                    "state": self.state,
                }

            @classmethod
            def parse(cls, raw_data: dict) -> Self:
                return cls(
                    name=raw_data['name'],
                    state=raw_data['state'],
                    pos=raw_data['pos'],
                )

        def __init__(
                self,
                name: str,
                pos: int,
        ):
            self.name = name
            self.pos = pos
            self.items: list[TrelloJsonParser.Checklist.CheckItem] = []

        def to_json(self) -> dict:
            return {
                "name": self.name,
                "items": self.items,
            }

        @classmethod
        def parse(cls, raw_data: dict) -> Self:
            ret_obj = cls(
                name=raw_data['name'],
                pos=raw_data['pos'],
            )
            for raw_check_item in raw_data['checkItems']:
                ret_obj.items.append(cls.CheckItem.parse(raw_check_item))
            ret_obj.items.sort(key=lambda x: x.pos)
            return ret_obj

    class Card:
        def __init__(
            self,
            name: str,
            list_name: str,
            list_id: str,
            pos: int,
            description: str,
            members: list[str],
            labels: list[str],
            checklists: list = [],
        ):
            self.name = name
            self.list_id = list_id
            self.list_name = list_name
            self.pos = pos
            self.description = description
            self.members = members
            self.labels = labels
            self.checklists: list[TrelloJsonParser.Checklist] = checklists

        @classmethod
        def parse(
            cls,
            raw_data: dict,
            list_obj,
            members_dict: dict,
            labels_dict: dict,
            checklists_dict: dict,
        ) -> Self:
            members = [u for k, u in members_dict.items()
                       if k in raw_data['idMembers']]
            labels = [l for k, l in labels_dict.items()
                      if k in raw_data['idLabels']]
            checklists = [cl for k, cl in checklists_dict.items()
                          if k in raw_data['idChecklists']]
            checklists.sort(key=lambda x: x.pos)

            list_id = raw_data['idList']
            assert isinstance(list_obj, TrelloJsonParser.Lists)
            list_name = list_obj.get_name(list_id)

            ret_obj = cls(
                name=raw_data['name'],
                list_id=list_id,
                list_name=list_name,
                pos=raw_data['pos'],
                description=raw_data['desc'],
                members=members,
                labels=labels,
                checklists=checklists,
            )
            return ret_obj

        def to_json(self):
            return {
                "name": self.name,
                "list": self.list_name,
                "description": self.description,
                "members": self.members,
                "labels": self.labels,
                "checklists": self.checklists,
            }

    class Lists:
        class List:
            def __init__(
                self,
                name: str,
                pos: int,
            ):
                self.name = name
                self.pos = pos

            @classmethod
            def parse(
                cls,
                raw_data: dict,
            ) -> Self:
                ret_obj = cls(
                    name=raw_data['name'],
                    pos=raw_data['pos'],
                )
                return ret_obj

        def __init__(
            self,
        ):
            self.lists: dict[str, TrelloJsonParser.Lists.List] = {}

        @classmethod
        def parse(
            cls,
            raw_data: dict,
        ) -> Self:
            ret_obj = cls()
            ret_obj.lists = {l['id']: cls.List.parse(l)for l in raw_data}
            return ret_obj

        def get_list(self, list_id: str):
            return self.lists.get(list_id, None)

        def get_pos(self, list_id: str) -> int:
            list_obj = self.get_list(list_id=list_id)
            if list_obj:
                return list_obj.pos
            return 0

        def get_name(self, list_id: str) -> str | None:
            list_obj = self.get_list(list_id=list_id)
            if list_obj:
                return list_obj.name
            return None

    def __init__(self, trello_json_data: dict):
        self._raw_data = trello_json_data
        self.lists = self.Lists()
        self.users = {}
        self.labels = {}
        self.checklists: dict[str, TrelloJsonParser.Checklist] = {}
        self.cards: list[TrelloJsonParser.Card] = []

    def parse(self):
        self.lists = self.Lists.parse(self._raw_data['lists'])
        self.users = {u['id']: u['fullName']
                      for u in self._raw_data['members']}
        self.labels = {l['id']: l['name'] for l in self._raw_data['labels']}
        self.checklists = {cl['id']: self.Checklist.parse(cl)
                           for cl in self._raw_data['checklists']}
        self.cards = [self.Card.parse(
            raw_data=c,
            list_obj=self.lists,
            checklists_dict=self.checklists,
            labels_dict=self.labels,
            members_dict=self.users
        ) for c in self._raw_data['cards']]
        self.cards.sort(key=lambda x: (self.lists.get_pos(x.list_id), x.pos))

    def get_output_dict(self) -> dict:
        output = {
            "board_data": {
                "name": self._raw_data['name'],
                "url": self._raw_data['shortUrl']
            },
            "cards": self.cards
        }
        return output

    def export_to_json(self, path):
        output = self.get_output_dict()

        with open(os.path.abspath(path), 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4, ensure_ascii=False,
                      cls=self.JSONEncoder)

        print("Output to {}!s".format(os.path.abspath(path)))
        print("Please visit https://json-csv.com/ to convert the output to CSV.")


parser = argparse.ArgumentParser()
parser.add_argument("input", help="JSON File from Trello", type=str)
parser.add_argument("output", help="File to output to", type=str)
parser.add_help = True
args = parser.parse_args()


print("Reading Data...")
with open(os.path.abspath(args.input), 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Found {} cards in {} lists.".format(
    len(data['cards']), len(data['lists'])))
print("Parsing...")

parser = TrelloJsonParser(data)
parser.parse()
parser.export_to_json(args.output)

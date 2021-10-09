#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''retrieve information via Qiita API v2
and calculate simplified Qiita Contribution
Precise definition of Qiita Contribution:
  https://help.qiita.com/ja/articles/qiita-contribution
'''
from __future__ import annotations
from typing import Dict, Optional
import os
import math
import requests
from datetime import datetime, timedelta
from argparse import ArgumentParser, RawTextHelpFormatter

QIITA_APIv2_URL = 'https://qiita.com/api/v2/'
PER_PAGE = 10


class User(object):
    '''retrieve user information

    Args:
        token str: Qiita Personal Access Token
        user_id str: Qiita user ID
        start Optional[datetime]: The day to start counting items
        end Optional[datetime]: The day to finish counting items
    '''
    def __init__(
        self: User,
        token: str,
        user_id: str,
        start: Optional[datetime],
        end: Optional[datetime]
    ) -> None:
        self.token = token
        self.user_id = user_id
        self.start = start
        self.end = end
        self.followees_count = 0
        self.followers_count = 0
        self.items_count = 0
        self.likes_count = 0
        self.stockers_count = 0
        self.comments_count = 0
        self.contribution = 0
        self.items = list()
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}',
        }
        print(f'retrieving user_id: {self.user_id}')
        url = os.path.join(
            QIITA_APIv2_URL, 'users', self.user_id
        )
        user = requests.get(url, headers=self.headers).json()
        self.followees_count = user['followees_count']
        self.followers_count = user['followers_count']
        self._get_items()
        self._calc_contribution()
        return

    def _get_items(self: User) -> None:
        '''retrieve items which was written by this user
        '''
        page = 1
        url = os.path.join(
            QIITA_APIv2_URL, 'users', self.user_id, 'items'
        )
        print('retrieving items', end='', flush=True)
        while True:
            params = {
                'page': str(page),
                'per_page': str(PER_PAGE),
            }
            print(f' {PER_PAGE * page}...', end='', flush=True)
            items = requests.get(
                url, params=params, headers=self.headers
            ).json()
            for item in items:
                self.items.append(Item(
                    token=self.token,
                    item_id=item['id'],
                    start=self.start,
                    end=self.end
                ))
            if len(items) < PER_PAGE:
                break
            page += 1
        print('')
        return

    def _calc_contribution(self: User) -> None:
        '''calculate simplified Qiita Contribution
        '''
        contribution = 0
        for item in self.items:
            self.items_count += 1 if item.is_valid else 0
            self.likes_count += item.likes_count
            self.stockers_count += item.stockers_count
            self.comments_count += item.comments_count
        contribution = self.items_count
        contribution += self.likes_count
        contribution += 0.5 * self.stockers_count
        self.contribution = int(math.floor(contribution + 0.5))
        return

    def get_contribution(self: User) -> Dict:
        '''provide Qiita Contribution and so on
        '''
        return {
            'user_id': self.user_id,
            'followees': self.followees_count,
            'followers': self.followers_count,
            'items': self.items_count,
            'likes': self.likes_count,
            'stockers': self.stockers_count,
            'comments': self.comments_count,
            'contribution': self.contribution,
        }


class Item(object):
    '''retrieve item information

    Args:
        token str: Qiita Personal Access Token
        item_id str: Qiita item ID
        start Optional[datetime]: The day to start counting items
        end Optional[datetime]: The day to finish counting items
    '''
    def __init__(
        self: Item,
        token: str,
        item_id: str,
        start: Optional[datetime],
        end: Optional[datetime]
    ) -> None:
        self.token = token
        self.item_id = item_id
        self.start = start
        self.end = end
        self.is_valid = False
        self.likes_count = 0
        self.stockers_count = 0
        self.comments_count = 0
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}',
        }
        url = os.path.join(
            QIITA_APIv2_URL, 'items', self.item_id
        )
        item = requests.get(url, headers=self.headers).json()
        self.created_at = datetime.strptime(
            item['created_at'][:19],
            '%Y-%m-%dT%H:%M:%S'
        )
        self.updated_at = datetime.strptime(
            item['updated_at'][:19],
            '%Y-%m-%dT%H:%M:%S'
        )
        if self.start is not None and self.updated_at < self.start:
            return
        if self.end is not None and self.created_at > self.end:
            return
        self.is_valid = True
        self.likes_count = item['likes_count']
        self.comments_count = item['comments_count']
        self.stockers_count = self._get_stockers_count()
        return

    def _get_stockers_count(self: Item) -> int:
        '''retrieve the number of stockers who stocks this item
        '''
        stockers_count = 0
        page = 1
        url = os.path.join(
            QIITA_APIv2_URL, 'items', self.item_id, 'stockers'
        )
        while True:
            params = {
                'page': str(page),
                'per_page': str(PER_PAGE),
            }
            stockers = requests.get(
                url, params=params, headers=self.headers
            ).json()
            stockers_count += len(stockers)
            if len(stockers) < PER_PAGE:
                break
            page += 1
        return stockers_count


def main() -> None:
    parser = ArgumentParser(
        description=(
            'Retrieve information via Qiita API v2'
            ' and calculate simplified Qiita Contribution'
        ),
        formatter_class=RawTextHelpFormatter
    )
    parser.add_argument(
        '-t', '--token', type=str, required=True,
        help='Qiita Personal Access Token'
    )
    parser.add_argument(
        '-u', '--users', type=str, required=True,
        help='Qiita User IDs (comma separated)'
    )
    parser.add_argument(
        '-s', '--start', type=str, default=None,
        help=(
            'The day to start counting items (YYYYMMDD)\n'
            '  (default: None = unlimited)'
        )
    )
    parser.add_argument(
        '-e', '--end', type=str, default=None,
        help=(
            'The day to finish counting items (YYYYMMDD)\n'
            '  (default: None = unlimited)'
        )
    )
    parser.add_argument(
        '-o', '--output', type=str, default='qiita_contributions.csv',
        help=(
            'The output CSV filename\n'
            '  (default: "qiita_contributions.csv")'
        )
    )
    args = parser.parse_args()
    token = args.token
    user_ids = [x.strip() for x in args.users.split(',')]
    start = None
    if args.start is not None:
        start = datetime.strptime(args.start, '%Y%m%d')
    end = None
    if args.end is not None:
        end = datetime.strptime(args.end, '%Y%m%d')
        end += timedelta(days=1)
        end -= timedelta(seconds=1)
    contributions = list()
    for user_id in user_ids:
        try:
            user = User(
                token=token,
                user_id=user_id,
                start=start,
                end=end
            )
        except Exception as e:
            print(e)
            continue
        contributions.append(user.get_contribution())
    if len(contributions) < 1:
        raise ValueError('No user was able to get the information')
    columns = [
        'user_id', 'followees', 'followers', 'items',
        'likes', 'stockers', 'comments', 'contribution',
    ]
    with open(args.output, 'wt') as wf:
        wf.write(','.join(['rank'] + columns) + '\n')
        for i, contribution in enumerate(sorted(
            contributions,
            key=lambda x: x['contribution'],
            reverse=True
        )):
            wf.write(','.join([str(i + 1)] + [
                str(contribution[c]) for c in columns
            ]) + '\n')
    return


if __name__ == '__main__':
    main()

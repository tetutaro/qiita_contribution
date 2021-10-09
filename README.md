# qiita_contribution

Retrieve information via Qiita API v2 and calculate simplified Qiita Contribution

## Precise definition of Qiita Contribution

[Contributionとは](https://help.qiita.com/ja/articles/qiita-contribution)

## What this does

[Qiita API v2](https://qiita.com/api/v2/docs) is used as a protocol to retrieve user/item/comment/... information of Qiita.
But, not all information can be retrieved to calculate Qiita Contribution even though via Qiita API v2.
So, this Python script retrieves some information and culculate simplified version of Qiita Contribution.

```
(Simplified Qiita Contribution)
  = (# of items) + (# of LGTMs) + 0.5 * (# of Stocks)
```

## Usage

```
> ./retrieve.py --help
usage: retrieve.py [-h] -t TOKEN -u USERS [-s START] [-e END] [-o OUTPUT]

Retrieve information via Qiita API v2 and calculate simplified Qiita Contribution

optional arguments:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        Qiita Personal Access Token
  -u USERS, --users USERS
                        Qiita User IDs (comma separated)
  -s START, --start START
                        The day to start counting items (YYYYMMDD)
                          (default: None = unlimited)
  -e END, --end END     The day to finish counting items (YYYYMMDD)
                          (default: None = unlimited)
  -o OUTPUT, --output OUTPUT
                        The output CSV filename
                          (default: "qiita_contributions.csv")
```

ex.)

```
> ./retrieve.py --token XXX --users id1,id2,id3 --start 20210401 --end 20210930 --output qiita_contributions.csv
```

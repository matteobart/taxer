# taxer
This repo allows you to experiment with different tax methods for a list of trades. This could give you some insight into the best Lot Instructions based on your previous trades. This information is most useful when you have a lot of different buying transactions and multiple selling transactions (across both long-term and short-term positions).

## How to use
### Pre-requisites
Python 3 is required to run this code - no additional python dependencies. You will also need to feed the data into the script, so you'll need two files:
#### CSV Data File
This should be a csv file of all the transactions to parse through. There are some expectations of this file: transactions should be in ascending order (earliest transactions first) & pricing information must be available on both buy and sell orders.  
This data should be available via your Brokerage's website. For Schwab user's who also recieve RSU's, this infromation is difficult to obtain. Luckily check out the `schwab/` folder for more information. There will be an additional preprocessing step to get this data in a usable format.  
  
Otherwise this repo should be flexible in terms of data format due to the...
#### Configuration JSON file
This file will allow you to pass in the relevant column names and data format, so that taxer can correctly parse the data. An example of this configuration can be found at `config.example.json`  

`date_format` expects the date in Python's datetime format code, more information can be found directly in the [Python Docs](https://docs.python.org/3/library/datetime.html#format-codes)

`ticker_column` and `ticker_to_track` are necessary to exclude other transactions that do not meet this matching. Any other rows with a different value then `ticker_to_track` will be ignored, this means the CSV data file can have more than one ticker's information - but only one will be processed per run.  
  
`transaction_type_column` is used to inform which column the transaction types will be in such as buying and selling. Note that `transaction_buy_values` and `transaction_sell_values` are lists to ensure that taxer can be more flexible. Any other row values that aren't in `transaction_buy_values` or `transaction_sell_values` will be ignored.  
  
`last_date` and `last_price` should be used together. If either is missing, these values will be ignored. When the values are not supplied, the last known price as per the input csv file will be used. `last_date` is expected in `YYYY/MM/DD` format.  
  
`capital_gains_tax_rate` and `income_tax_rate` are integer (whole number) values that should denote your expected tax rates. A value of `30` => `30%`, `22` => `22%`, etc. `income_tax_rate` is your expected federal income tax based on your tax bracket (10%, 12%, ... 37%). `capital_gains_tax_rate` is also based off income (0%, 15%, 20%).  

### Run
```
python3 main.py path/to/data.csv /path/to/config.json
```

## To Do
* Additional error checking to inputs
* Additional unit tests
* Ability to get different tax burdens based on the year (e.g. will also need additional tax rate inputs)
* Get transaction data sets to run this across multiple scenario to find ideal tax method


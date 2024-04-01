# Test Request

Just tries every request for every network to see which ones are implemented.

## Description

Spits out a CSV of the result of testing each method on each network.

## Getting Started

### Dependencies

See requirements.txt

The script takes an Infura API key from environment var INFURA_API_KEY or it can be specified on the command line.

### Installing

Git clone and pip install -r requirements.txt

### Executing program

See
```
./test_request.py --help
```

## Help

These methods need eth in the source account to work properly, or nonce has to be correct, etc.
So they are hard to test generically:
   'eth_call', 'eth_createAccessList', 'eth_estimateGas', 'eth_sendRawTransaction',

They can be used in the --method argument though results may vary.

## Authors

Chris Paterson (https://github.com/cipaterson)


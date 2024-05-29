#!/usr/bin/env python3
import requests
import os
import sys
import json
import argparse
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser(
    description='A test suite to elicit each error for eth_method(s) for every network')
# parser.add_argument('-t', '--tests', nargs='+',
#                     help='Test name(s) to test, e.g. "extra comma" (all tests by default).')
parser.add_argument('-n', '--networks', nargs='+',
                    help='Network subdomain to test (all test networks by default).')
parser.add_argument('-p', '--print', help='print the list of tests',
                    action="store_true")
parser.add_argument('-v', '--verbose', help='output the response for the request',
                    action="store_true")
parser.add_argument('-q', '--quiet', help='Don\'t be verbose',
                    action="store_true")
parser.add_argument('-k', '--api_key', metavar='INFURA_API_KEY', default=None,
                    help='Infura API Key to use (INFURA_API_KEY env var used by default).')

args = parser.parse_args()

InfuraApiKey = args.api_key or os.environ.get(
    "INFURA_API_KEY") or os.environ.get("ETH")
if InfuraApiKey == None:
    print('Error: Use --api_key to provide a valid Infura API key', file=sys.stderr)
    parser.print_help()
    exit(1)

print_tests = args.print
verbose = args.verbose
quiet = args.quiet
if quiet:
    verbose = False

defaultNetworks = [
    "mainnet",
    "sepolia",
    "holesky",
    "polygon-amoy",
    "arbitrum-sepolia",
    "palm-testnet",
    "avalanche-fuji",
    # "starknet-sepolia",  no web3_clientVersion
    "celo-alfajores",
]
theNetworks = args.networks or defaultNetworks

theTests = {
    "No error": '{"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": ["latest", false], "id": 1}',
    "extra comma": '{"jsonrpc": "2.0", "method": "eth_getBlockByNumber",, "params": ["latest", false], "id": 1}',
    "missing id": '{"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": ["latest", false]}',
    "non-numeric id": '{"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": ["latest", false], "id": wrong}',
    "method miss-spelled": '{"jsonrpc": "2.0", "method": "eth_getBlockByNum", "params": ["latest", false], "id": 1}',
    "extra param": '{"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": ["latest", false, "extra"], "id": 1}',
    "missing param": '{"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": ["latest"], "id": 1}',
    "missing 0x": '{"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": ["5BAD55", false], "id": 1}',
    "unsupported method": '{"jsonrpc":"2.0","method":"eth_newFilter","params":[{"topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]}],"id":1}',
    "JSONRPC version": '{"jsonrpc": "0.1", "method": "eth_getBlockByNumber", "params": ["latest", false], "id": 1}',
}

# if --print, list out the tests and exit
if print_tests:
    for t in theTests:
        print(f'{t:20}: {theTests[t]}')
    exit(0)

# Print summary header row
print("test,", ', '.join(theNetworks))

for t in theTests:
    request = theTests[t]
    if verbose:
        print(f'{request=}')
    summary = f'{t:20}'
    for n in theNetworks:
        url = f'https://{n}.infura.io/v3/{InfuraApiKey}'
        try:
            response = requests.post(url, data=request)
        except:
            print(f"Error: Can't connect: {url}", file=sys.stderr)
            exit(1)

        # Print more detailed info if methods are specified on command line with '-m' or if '-v'
        if verbose:
            print(f'{n}: {response.text[:200]}')

        if response.status_code == 401:
            if "invalid" in response.text:
                print(
                    f'Error: use --api_key to provide a valid Infura API key', file=sys.stderr)
                exit(1)
            elif "does not have access" in response.text:
                print(
                    f'Error: "Project ID does not have access to {n}', file=sys.stderr)
                exit(1)
            else:
                print("ERROR: unknown 401 response",
                      response.text, file=sys.stderr)
                exit(1)

        # Ignore 400 because many networks return it together with a valid error response we can interpret later
        # Networks that do this: near, starknet, avalanche, base.
        if response.status_code != 200 and response.status_code != 400:
            print(
                f'Error: {n}, {t}, Status code: {response.status_code}, URL: {url}', file=sys.stderr)
            exit(1)

        if response.text!='':
            jResponse = json.loads(response.text)
        else:
            jResponse= {"result": ""}

        # # Print more detailed info if methods are specified on command line with '-m' or if '-v'
        # if verbose:
        #     if jResponse.get('error') == None:
        #         print(f'{n}: {response.text[:200]}')
        #     else:
        #         print(f'{n}: {jResponse["error"]}')

        if jResponse.get('error') == None:
            if jResponse.get('result') == "":
                summary += f', Empty response ({response.status_code})'
            else:
                summary += f', OK     ({response.status_code})'
        else:
            error_code = jResponse['error']['code']
            summary += f', {error_code} ({response.status_code})'

    print(summary)

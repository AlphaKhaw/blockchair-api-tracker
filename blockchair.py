import os
import sys
import time
import json
import logging
import datetime 
import requests
import numpy as np
import pandas as pd
from urllib.request import urlopen

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', 
                    level=logging.INFO, 
                    datefmt='%H:%M:%S')

class Blockchair:
    def __init__(self, address, file_name, api_key=None):
        self.address = address
        self.file_name = file_name
        self.api_key = api_key
        
        self.check_multiple_addresses()  
    
    def check_multiple_addresses(self):
        if type(self.address) is str:
            self.check_blockchain(self.address)
        elif type(self.address) is tuple or list:
            for add in range(len(self.address)):
                self.check_blockchain(self.address[add])
    
    def check_blockchain(self, add):
        if add[:2] == '0x':
            logging.info(f'Ethereum address: {add}')
            ETH(add, self.file_name, self.api_key)
        elif add[:3] == 'bc1' or add[0] == '1' or '3':
            logging.info(f'Bitcoin address: {add}')
            BTC(add, self.file_name, self.api_key)
        else:
            logging.warning('Please check input address format')
            return

class BTC:
    def __init__(self, btc_address, file_name, api_key=None):
        self.address = btc_address
        self.file_name = f'btc_{file_name}.xlsx'
        self.api_key = api_key
        self.url = f'https://api.blockchair.com/bitcoin/dashboards/address/{btc_address}?limit=10000'
        self.address_endpoint = json.load(urlopen(self.url))
        self.session = requests.Session()
        self.input_df = pd.DataFrame()
        self.output_df = pd.DataFrame()
        
        self.get_address_information()
        self.get_transaction_endpoint()
        self.get_block_information()
        self.extract_transaction_data()
        self.transform_transaction_information()
        self.output_excel()
        
    # Summary information written to DataFrame
    def get_address_information(self):
        self.summary_df = pd.DataFrame(self.address_endpoint['data']
                                       [self.address]['address'], index=[0])
        rename_dict = {'balance': 'Balance (Satoshi)',
                       'balance_btc': 'Balance (BTC)',
                       'balance_usd': 'Balance (USD)',
                       'first_seen_receiving': 'First Seen Receiving',
                       'first_seen_spending': 'First Seen Spending',
                       'last_seen_receiving': 'Last Seen Receiving',
                       'last_seen_spending': 'Last Seen Spending',
                       'transaction_count': 'Transaction Count',                       
                       'output_count': 'Output Count',
                       'unspent_output_count': 'Unspent Output Count',
                       'received': 'Received (Satoshi)',
                       'received_btc': 'Received (BTC)',
                       'received_usd': 'Received (USD)',
                       'spent': 'Spent (Satoshi)',
                       'spent_btc': 'Spent (BTC)',
                       'spent_usd': 'Spent (USD)',
                       'script_hex': 'Script Hex',
                       'scripthash_type': 'Script Hash Type',
                       'type': 'Type'
                        }
        self.summary_df = self.summary_df.rename(columns=rename_dict)
        return self.summary_df
    
    # Block information written to DataFrame
    def get_block_information(self):
        transaction = [self.data[i]['transaction'] 
                       for i in range(len((self.data)))]
        self.block_df = pd.json_normalize([transaction[i] 
                                           for i in range(len(transaction))])
        # Convert satoshi to BTC value
        self.block_df['input_total_btc'] = [amt*pow(10,-8) for amt in 
                                            self.block_df['input_total']]
        self.block_df['output_total_btc'] = [amt*pow(10,-8) for amt in 
                                            self.block_df['output_total']]
        rename_dict = {'block_id': 'Block ID',
                        'id': 'ID',
                        'hash': 'Transaction Hash',
                        'date': 'Date',
                        'time': 'DateTime',
                        'size': 'Size',
                        'weight': 'Weight',
                        'version': 'Version',
                        'lock_time': 'Lock Time',
                        'is_coinbase': 'From Coinbase',
                        'has_witness': 'Has Witness',
                        'input_count': 'Input Count',
                        'output_count': 'Output Count',
                        'input_total': 'Input Total (Satoshi)',
                        'input_total_btc': 'Input Total (BTC)',
                        'input_total_usd': 'Input Total (USD)',
                        'output_total': 'Output Total (Satoshi)',
                        'output_total_btc': 'Output Total (BTC)',
                        'output_total_usd': 'Output Total (USD)',
                        'fee': 'Fee (Satoshi)',
                        'fee_usd': 'Fee (USD)',
                        'fee_per_kb': 'Fee per size (Satoshi)',
                        'fee_per_kb_usd': 'Fee per size (USD)',
                        'fee_per_kwu': 'Fee per weight (Satoshi)',
                        'fee_per_kwu_usd': 'Fee per weight (USD)',
                        'cdd_total': 'CDD (Coin Days Destroyed) Total',
                        'is_rbf': 'Replace-By-Fee (RBF)'
                        }
        self.block_df = self.block_df.rename(columns=rename_dict)
        self.block_df = self.block_df[::-1].reset_index(drop=True)
        return self.block_df
    
    def get_transaction(self, txs, attempt=0):
        if self.api_key is None:
            if attempt == 0:
                url = f'https://api.blockchair.com/bitcoin/dashboards/transactions/{txs}'
                response = self.session.get(url)
            elif attempt == 1:
                url = f'https://api.blockchair.com/bitcoin/dashboards/transactions/{txs}'
                response = self.session.get(url)
                time.sleep(1.5)
        else:
            if attempt == 0:
                url = f'https://api.blockchair.com/bitcoin/dashboards/transactions/{txs}?key={self.api_key}'
                response = self.session.get(url)
        return response
    
    def get_transaction_endpoint(self):
        self.txs_hash_lst = self.address_endpoint['data'][self.address]['transactions']
        i = 0
        joined = []
        while i <= len(self.txs_hash_lst):
            for tx in self.txs_hash_lst:
                joined.append(','.join(self.txs_hash_lst[i:i+10]))
                i += 10
        joined = [string for string in joined if string != ""]
        
        start = datetime.datetime.now()
        logging.info('Start requests session - {} transactions'
                     .format(len(self.txs_hash_lst)))
        
        response = [self.get_transaction(txs) for txs in joined]
        
        try:
            self.data = [response[r].json() for r in range(len(response))]
        except AttributeError:
            logging.info('Exceed API limit - Restarting requests session')
            time.sleep(1)
            response = [self.get_transaction(txs, 1) for txs in joined]
            self.data = [response[r].json() for r in range(len(response))]
        
        joined = [joined[i].split(',') for i in range(len(joined))]
        try:
            self.data = [self.data[i]['data'][j] 
                         for i in range(len(self.data)) for j in joined[i]]
        except TypeError:
            # logging.warning('Exceed API limit - Increase waiting time / Use API key instead')
            raise Exception('Exceed API limit - Increase waiting time / Use API key instead')
        finish = datetime.datetime.now() - start
        logging.info('Total time taken: {}'.format(finish))
        return self.data
        
    def extract_transaction_data(self):
        inputs = [self.data[i]['inputs']
                  for i in range(len((self.data)))]
        outputs = [self.data[i]['outputs'] 
                   for i in range(len((self.data)))]        
        
        for i in range(len(inputs)):
            self.input_df = self.input_df.append(inputs[i], 
                                                 ignore_index=True)
        for i in range(len(outputs)):
            self.output_df = self.output_df.append(outputs[i], 
                                                   ignore_index=True)
            
    # In-depth transaction information written to DataFrame
    def transform_transaction_information(self):
        # Combination of input and output df
        txs_df = pd.merge(self.input_df[['recipient', 'spending_block_id']], 
                          self.output_df, 
                          left_on='spending_block_id',
                          right_on='block_id',
                          how='outer',
                          suffixes=('_x', '')
                          ).rename(columns={'recipient_x':'from', 
                                            'recipient':'to'}
                                            ).filter(regex='^(?!.*_x)')                
        txs_df = txs_df[(txs_df['from']==self.address) | 
                        (txs_df['to']==self.address)]
        
        # Convert satoshi to BTC value
        txs_df['value_btc'] = [amt*pow(10,-8) for amt in txs_df['value']]
        
        rename_dict = {'from': 'From',
                       'to': 'To',
                       'block_id': 'Block ID',
                       'transaction_id': 'Transaction ID',
                       'index': 'Index',
                       'transaction_hash': 'Transaction Hash',
                       'date': 'Date',
                       'time': 'DateTime',
                       'value': 'Value (Satoshi)',
                       'value_btc' : 'Value (BTC)',
                       'value_usd': 'Value (USD)',
                       'type': 'Type',
                       'script_hex': 'Script Hex',
                       'is_from_coinbase': 'From Coinbase',
                       'is_spendable': 'Spendable',
                       'is_spent': 'Spent',
                       'spending_block_id': 'Spending Block ID',
                       'spending_transaction_id': 'Spending Transaction ID',
                       'spending_index': 'Spending Index',
                       'spending_transaction_hash': 'Spending Transaction Hash',
                       'spending_date': 'Spending Date',
                       'spending_time': 'Spending DateTime',
                       'spending_value_usd': 'Spending Value (USD)',
                       'spending_sequence': 'Spending Sequence',
                       'spending_signature_hex': 'Spending Signature Hex',
                       'spending_witness': 'Spending Witness',
                       'lifespan': 'Lifespan',
                       'cdd': 'CDD (Coin Days Destroyed)'
                       }
        self.txs_df = txs_df.rename(columns=rename_dict).fillna(value=np.nan)
        self.txs_df = self.txs_df[::-1].reset_index(drop=True)
        return self.txs_df
    
    def output_excel(self):
        logging.info('Writing data to Excel')
        path = f'{os.path.abspath(os.path.dirname(sys.argv[0]))}\{self.file_name}'
        writer = pd.ExcelWriter(self.file_name, engine='xlsxwriter')
        self.summary_df.to_excel(writer, 
                                 sheet_name='Summary',
                                 index=False)
        self.block_df.to_excel(writer, 
                               sheet_name='Block',
                               index=False)
        self.txs_df.to_excel(writer, 
                             sheet_name='Transaction',
                             index=False)
        writer.save()
        logging.info(f'Exported as {self.file_name}')
        logging.info(f'Saved file path - {path}')

class ETH:   
    def __init__(self, eth_address, file_name, api_key=None):
        self.address = eth_address
        self.file_name = f'eth_{file_name}.xlsx'
        self.api_key = api_key
        self.url = f'https://api.blockchair.com/ethereum/dashboards/address/{eth_address}?limit=10000'
        self.address_endpoint = json.load(urlopen(self.url))
        self.session = requests.Session()
        
        self.get_address_information()
        self.get_block_information()
        self.get_transaction_endpoint()
        self.transform_transaction_information()
        self.output_excel()
            
    # Summary information written to DataFrame
    def get_address_information(self):
        self.summary_df = pd.DataFrame(self.address_endpoint['data']
                                       [self.address.lower()]['address'], 
                                       index=[0])
        # Convert columns in gwei to ETH value 
        self.summary_df['balance_eth'] = [float(value)/pow(10, 9) 
                                          for value in self.summary_df['balance']]
        self.summary_df['fees_approximate_eth'] = [float(value)/pow(10, 9) 
                                                   for value in self.summary_df['fees_approximate']]
        self.summary_df['received_approximate_eth'] = [float(value)/pow(10, 9) 
                                                       for value in self.summary_df['received_approximate']]
        self.summary_df['spent_approximate_eth'] = [float(value)/pow(10, 9) 
                                                    for value in self.summary_df['spent_approximate']]
        rename_dict = {'balance': 'Balance (Gwei)',
                       'balance_eth': 'Balance (ETH)',
                       'balance_usd': 'Balance (USD)',
                       'call_count': 'Call Count',
                       'contract_code_hex': 'Contract Code Hex',
                       'contract_created': 'Contract Created',
                       'contract_destroyed': 'Contract Destroyed',
                       'fees_approximate': 'Fees Approximate (Gwei)',
                       'fees_approximate_eth': 'Fees Approximate (ETH)',
                       'fees_usd': 'Fees (USD)',
                       'first_seen_receiving': 'First Seen Receiving',
                       'first_seen_spending': 'First Seen Spending',
                       'last_seen_receiving': 'Last Seen Receiving',
                       'last_seen_spending': 'Last Seen Spending',
                       'received_approximate': 'Received Approximate (Gwei)',
                       'received_approximate_eth': 'Received Approximate (ETH)',
                       'received_usd': 'Received (USD)',
                       'receiving_call_count': 'Receiving Call Count',
                       'spending_call_count': 'Spending Call Count',
                       'spent_approximate': 'Spent Approximate (Gwei)',
                       'spent_approximate_eth': 'Spending Approximate (ETH)',
                       'spent_usd': 'Spent (USD)',
                       'transaction_count': 'Transaction Count',
                       'type': 'Type'
                        }
        self.summary_df = self.summary_df.rename(columns=rename_dict)
        return self.summary_df
    
    # Block information written to DataFrame
    def get_block_information(self):
        # add_endpoint = json.load(urlopen(self.url))
        self.block_df = pd.json_normalize(self.address_endpoint['data']
                                          [self.address.lower()]['calls'])                          
        # Convert columns in gwei to ETH value
        self.block_df['value_eth'] = [float(value)/pow(10, 9) 
                                      for value in self.block_df['value']]
        rename_dict = {'block_id': 'Block ID',
                        'transaction_hash': 'Transaction Hash',
                        'index': 'Index',
                        'time': 'DateTime',
                        'sender': 'From',
                        'recipient': 'To',
                        'value': 'Value (Gwei)',
                        'value_eth': 'Value (ETH)',
                        'value_usd': 'Value (USD)',
                        'transferred': 'Transferred',
                        }
        self.block_df = self.block_df.rename(columns=rename_dict)
        self.block_df = self.block_df[::-1].reset_index(drop=True)
        return self.block_df
    
    def get_transaction(self, txs, attempt=0):
        if self.api_key is None:
            if attempt == 0:
                url = f'https://api.blockchair.com/ethereum/dashboards/transactions/{txs}'
                response = self.session.get(url)
            elif attempt == 1:
                url = f'https://api.blockchair.com/ethereum/dashboards/transactions/{txs}'
                response = self.session.get(url)
                time.sleep(1.5)
        else:
            if attempt == 0:
                url = f'https://api.blockchair.com/ethereum/dashboards/transactions/{txs}?key={self.api_key}'
                response = self.session.get(url)
        return response
    
    def get_transaction_endpoint(self):
        txs_hash_lst = [self.address_endpoint['data'][self.address.lower()]['calls'][i]['transaction_hash'] 
                        for i in range(len(self.address_endpoint['data'][self.address.lower()]['calls']))]
        i = 0
        joined = []
        while i <= len(txs_hash_lst):
            for tx in txs_hash_lst:
                joined.append(','.join(txs_hash_lst[i:i+10]))
                i += 10
        joined = [string for string in joined if string != ""]
        
        start = datetime.datetime.now()
        logging.info('Start requests session - {} transactions'
                     .format(len(txs_hash_lst)))
        response = [self.get_transaction(txs) for txs in joined]
        
        try:
            self.data = [response[r].json() for r in range(len(response))]
        except AttributeError:
            logging.info('Exceed API limit - Restarting requests session')
            time.sleep(1)
            response = [self.get_transaction(txs, 1) for txs in joined]
            self.data = [response[r].json() for r in range(len(response))]
        
        joined = [joined[i].split(',') for i in range(len(joined))]
        
        try:
            self.data = [self.data[i]['data'][j]['transaction'] 
                         for i in range(len(self.data)) for j in joined[i]]
            self.data = pd.json_normalize(self.data)
        except TypeError:
            raise Exception('Exceed API limit - Increase waiting time / Use API key instead')
        
        finish = datetime.datetime.now() - start
        logging.info('Total time taken: {}'.format(finish))
        return self.data

    # In-depth transaction information written to DataFrame
    def transform_transaction_information(self):
        # Convert columns in gwei to ETH value
        self.data['value_eth'] = [float(value)/pow(10, 9) 
                                  for value in self.data['value']]
        self.data['internal_value_eth'] = [float(value)/pow(10, 9) 
                                           for value in self.data['internal_value']]
        self.data['fee_eth'] = [float(value)/pow(10, 9) 
                                for value in self.data['fee']]
        self.data['gas_price_eth'] = [float(value)/pow(10, 9) 
                                      for value in self.data['gas_price']]
        self.data['effective_gas_price_eth'] = [float(value)/pow(10, 9) 
                                                for value in self.data['effective_gas_price']]
        self.data['max_fee_per_gas_eth'] = [float(value)/pow(10, 9) 
                                            for value in self.data['max_fee_per_gas']]
        self.data['max_priority_fee_per_gas_eth'] = [float(value)/pow(10, 9) 
                                                     for value in self.data['max_priority_fee_per_gas']]
        self.data['base_fee_per_gas_eth'] = [float(value)/pow(10, 9) 
                                             for value in self.data['base_fee_per_gas']]
        rename_dict = {'block_id': 'Block ID',
                       'id': 'ID',
                       'index': 'Index',
                       'hash': 'Transaction Hash',
                       'date': 'Date',
                       'time': 'DateTime',
                       'failed': 'Failed',
                       'type': 'Type',
                       'sender': 'From',
                       'recipient': 'To',
                       'call_count': 'Call Count',
                       'value': 'Value (Gwei)',
                       'value_eth' : 'Value (ETH)',
                       'value_usd': 'Value (USD)',
                       'internal_value': 'Internal Value',
                       'internal_value_eth': 'Internal Value (ETH)',
                       'internal_value_usd': 'Internal Value (USD)',
                       'fee': 'Fee (Gwei)',
                       'fee_eth': 'Fee (ETH)',
                       'fee_usd': 'Fee (USD)',
                       'gas_used': 'Gas Used',
                       'gas_limt': 'Gas Limit',
                       'gas_price': 'Gas Price (Gwei)',
                       'gas_price_eth': 'Gas Price (ETH)',
                       'effective_gas_price': 'Effective Gas Price (Gwei)',
                       'effective_gas_price_eth': 'Effective Gas Price (ETH)',
                       'max_fee_per_gas': 'Max Fee per Gas (Gwei)',
                       'max_fee_per_gas_eth': 'Max Fee per Gas (ETH)',
                       'max_priority_fee_per_gas': 'Max Priority Fee per Gas (Gwei)',
                       'max_priority_fee_per_gas_eth': 'Max Priority Fee per Gas (ETH)',
                       'base_fee_per_gas': 'Base Fee per Gas (Gwei)',
                       'base_fee_per_gas_eth': 'Base Fee per Gas (ETH)',
                       'input_hex': 'Input Hex',
                       'nonce': 'Nonce',
                       'version': 'Version',
                       'burned': 'Burned',
                       'v': 'v',
                       'r': 'r',
                       's': 's',
                       'version': 'Version',
                       'type_2718': 'type_2718'
                       }
        self.txs_df = self.data.rename(columns=rename_dict).fillna(value=np.nan)
        self.txs_df = self.txs_df[::-1].reset_index(drop=True)
        return self.txs_df
    
    def output_excel(self):
        logging.info('Writing data to Excel')
        path = f'{os.path.abspath(os.path.dirname(sys.argv[0]))}\{self.file_name}'
        writer = pd.ExcelWriter(self.file_name, engine='xlsxwriter')
        self.summary_df.to_excel(writer, 
                                 sheet_name='Summary',
                                 index=False)
        self.block_df.to_excel(writer, 
                               sheet_name='Block',
                               index=False)
        self.txs_df.to_excel(writer, 
                             sheet_name='Transaction',
                             index=False)
        writer.save()
        logging.info(f'Exported as {self.file_name}')
        logging.info(f'Saved file path - {path}')

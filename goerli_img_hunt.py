#!/usr/bin/env python3

import time
import json
import binascii
import requests
import datetime
from web3 import Web3
from web3.middleware import geth_poa_middleware

api_url = 'https://api-goerli.etherscan.io/api'
endpoint = 'https://goerli.prylabs.net'

start_date = '2020-07-30'
end_date = '2020-08-01'

start_date_lst = start_date.split('-')
end_date_lst = end_date.split('-')

magic_lst = {
	'jpg_magic': {
		'hex': 'FFD8',
		'ext': 'jpg'
	},
	'png_magic': {
		'hex': '89504E470D0A1A0A',
		'ext': 'png'
	}
}

footer_lst = {
	'jpg_footer': {
		'hex': 'FFD9'
	},
	'png_footer': {
		'hex': '49454E44AE426082'
	}
}

print('\n--------------------------------')
print('--- Detect & Extract JPG/PNG ---')
print('--- Goerli Testnet Blockchain --')
print('--- Created By : thewhiteh4t ---')
print('--------------------------------\n')

print('[>] Start Date : {}'.format(start_date))
print('[>] End Date   : {}\n'.format(end_date))

start_epoch = int(datetime.datetime(int(start_date_lst[0]), int(start_date_lst[1]), int(start_date_lst[2]), 0, 0).timestamp())
end_epoch = int(datetime.datetime(int(end_date_lst[0]), int(end_date_lst[1]), int(end_date_lst[2]), 0, 0).timestamp())

print('[+] Start Epoch : {}'.format(start_epoch))
print('[+] End Epoch   : {}'.format(end_epoch))

def get_block_id(epoch):
	headers = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0' }
	params = {
		'module': 'block',
		'action': 'getblocknobytime',
		'timestamp': epoch,
		'closest': 'before'
	}
	try:
		r = requests.get(api_url, params=params, headers=headers)
	except Exception as exc:
		print('\n[-] Exception : {}'.format(str(exc)))
		exit()
	sc = r.status_code
	if sc == 200:
		data = r.text
		json_data = json.loads(data)
		epoch = int(json_data['result'])
		return epoch
	else:
		print('\n[-] Status Code : {}'.format(str(sc)))

print('\n[!] Fetching Block ID for Start Epoch...')
start_blk = get_block_id(start_epoch)
print('[+] Start Block ID : {}'.format(str(start_blk)))
print('\n[*] Sleeping for 5 Seconds...')
time.sleep(5)
print('\n[!] Fetching Block ID for Ending Epoch...')
end_blk = get_block_id(end_epoch)
print('[+] End Block ID   : {}'.format(str(end_blk)))

total_blks = end_blk - start_blk
print('\n[+] Total Number of Blocks in Range : {}'.format(str(total_blks)))

def save_image(blob, blk_id, tx, ext):
	filename = '{}_{}.{}'.format(str(blk_id), str(tx), ext)
	with open(filename, 'wb') as outfile:
		try:
			outfile.write(binascii.unhexlify(blob))
			print('\n[+] Image Saved : {}'.format(filename))
		except Exception as exc:
			print('\n[-] Exception : {}'.format(str(exc)))
			return

def save_hex(section, blob, blk_id, tx):
	filename = '{}_{}_{}.txt'.format(str(blk_id), str(tx), section)
	with open(filename, 'w') as outfile:
		outfile.write(blob)
	print('[+] Partial Image Hex Saved : {}\n'.format(filename))

def validate(blob, blk_id, tx):
	header = False
	footer = False

	for magic_type in magic_lst.items():
		magic_hex = magic_type[1]['hex']
		file_ext = magic_type[1]['ext']

		if blob.lower().startswith(magic_hex.lower()):
			print('\n\n[+] {} Header Found in Block {}'.format(file_ext, blk_id))
			header = True
			section = 'header'
		else:
			pass

	for footer_type in footer_lst.items():
		footer_hex = footer_type[1]['hex']

		if blob.lower().endswith(footer_hex.lower()):
			print('\n\n[+] Image Footer Found in Block {}'.format(blk_id))
			footer = True
			section = 'footer'
		else:
			pass

	if header == True and footer == False:
		print('[*] Only Header is Present in this Block...')
		save_hex(section, blob, blk_id, tx)
	if header == False and footer == True:
		print('[*] Only Footer is Present in this Block...')
		save_hex(section, blob, blk_id, tx)
	if header == True and footer == True:
		print('[*] Image Validated!')
		save_image(blob, blk_id, tx, file_ext)

def fetch_blks(w3, blk_id, outfile):
	blk_data = w3.eth.getBlock(blk_id, full_transactions=True)
	try:
		txs = blk_data['transactions']
		if txs != 0:
			for tx in txs:
				blob = tx['input']
				blob = blob.replace('0x0', '')
				validate(blob, blk_id, txs.index(tx))

				outfile.write('-' * 5 + ' BLOB START ' + '-' * 5 + '\n')
				outfile.write('Block ID : ' + str(blk_id))
				outfile.write('\n\n')
				outfile.write(blob)
				outfile.write('\n')
				outfile.write('-' * 5 + ' BLOB END ' + '-' * 5 + '\n\n')
		else:
			pass
	except KeyError:
		pass

def fetch_blk_info():
	print('\n[!] Connecting to Goerli Testnet Endpoint...')
	w3 = Web3(Web3.HTTPProvider(endpoint))
	w3.middleware_onion.inject(geth_poa_middleware, layer=0)

	if w3.isConnected() == True:
		print('[+] Connection Established!\n')
		count = 0
		with open('blobs.txt', 'w') as outfile:
			for blk_id in range(start_blk, end_blk):
				count += 1
				fetch_blks(w3, blk_id, outfile)
				print('[!] Fetching Blocks : {} / {} | Current Block : {}'.format(str(count), str(total_blks), str(blk_id)), end='\r')
	else:
		print('\n[-] Failed to Connect...Exiting')
		exit()

try:
	fetch_blk_info()
except KeyboardInterrupt:
	print('\n[-] Keyboard Interrupt.')
	exit()
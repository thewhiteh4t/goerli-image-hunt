# goerli-image-hunt

I wrote this script for solving a CTF challenge...you may find this code useful in some other similar application like threat hunting, give credits if you choose to use it ;)

**Challenge** : Find and extract an image uploaded on Goerli Testnet Blockchain between a range of dates.

---

### How it works

Transactions in each block contains an **input data** section which contains additional information for transactions. In this challenge hex code of an image was added in this section.
Script fetches block ids for timestamps using EtherScan API then it calculates number of blocks in between these dates and fetches full block information using Goerli Testnet RPC API.
The input data is then tested for a **jpg or png** magic bytes and footers, if a match is found it is saved to a file.

---

### Dependencies

```bash
pip3 install requests, web3
```

---

### Usage

**Step 1** : Set `Start` and `End` dates in the script

**Note**
* Start and End dates should be in ascending order and in the past, or the script will break, I have not added proper exception handling yet
* **Date Format** : YYYY-MM-DD [ Example : 2020-08-05]

**Step 2** : Launch the script and wait until it finds a match, it can take a long time depending on the date range, have patience



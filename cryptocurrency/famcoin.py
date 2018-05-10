#author: murguan425
#Create a Cryptocurrency

#import the libraries
import datetime
import hashlib
import json
import requests
from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse

#PART1: Create a Crypto Currency on Blockchain
class BlockChain:
    #Step1: Initalize a empty transaction list
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()
    #Step2: Add a transaction variable in the block and initialize with the transaction list
    def create_block(self, proof, previous_hash):
        block = {"index": len(self.chain) + 1,
                 "timestamp": str(datetime.datetime.now()),
                 "proof": proof,
                 "previous_hash": previous_hash,
                 "transactions": self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block

    def get_prev_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        valid_proof = False
        while valid_proof is False:
            hash_key_number = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_key_number[:4] == '0000':
                valid_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_key_number = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_key_number[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    #Step3: Method used to add a new transaction to the transaction list 
    # and returns the block number in which it will be stored
    def add_transactions(self, sender, receiver, amount):
        self.transactions.append({
                'sender': sender,
                'receiver': receiver,
                'amount': amount
            })
        previous_block = self.get_prev_block()
        return (previous_block['index'] + 1)
    #Step4: Method used to add a new node to the blockchain
    def add_nodes(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    # Step5: Consensus Check done to validate if there is any other node in the 
    # network which has the longest chain than the current node
    # In that case, the longest chain becomes valid and this node will get 
    # updated with that chain, based on the prinicple of blockchain
    # The longest chain in the network always wins
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

#PART2: Mining the Blockchain
app = Flask(__name__)

#Step6: Creating an address for the node on Port 5000. UUID generates random address
node_address = str(uuid4()).replace('-','')
mining_reward = 5

blockchain = BlockChain()

# Mining a new Block
#Step7: Provide reward to the miner by doing a coin transaction from the node to the miner address.
@app.route("/mine_block", methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_prev_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transactions(sender = node_address, receiver = 'Murugan', amount = mining_reward)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'New Block is successfully Mined. Enjoy your reward!',
                "index": block['index'],
                "timestamp": block['timestamp'],
                "proof": block['proof'],
                "previous_hash": block['previous_hash'],
                "transactions": block['transactions']}
    return jsonify(response), 201

# Return the entire full blockchain
@app.route("/get_chain", methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Check if the blockchain is valid
@app.route("/is_valid", methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message' : "The Blockchain is valid."}
    else:
        response = {'message' : "The Blockchain is invalid. Please be cautious."}
    return jsonify(response), 200

#Step8: Adding a new transaction to the blockchain
@app.route("/add_transaction", methods = ['POST'])
def add_transaction():
    transaction = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Tranaction data is invalid. Please check your transaction details', 400
    index = blockchain.add_transactions(transaction['sender'], transaction['receiver'], transaction['amount'])
    response = {'message':f'This transaction will be added in Block#: {index}'}   
    return jsonify(response), 201

#PART3: Decentralizing the blockchain
#Step9: Connecting new nodes to the blockchian
@app.route("/connect_node", methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No node detail provide to connect', 400
    for node in nodes:
        blockchain.add_nodes(node)
    response = {'message':'All the nodes are now connected. The Famcoin Blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

#Step10: Request to perform/trigger a consensus check to replace the chain by the longest one in the blockchain
@app.route("/replace_chain", methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message' : "The nodes had differet longest chain, so the chain was replaced by that one.", 
                    'new_chain': blockchain.chain}
    else:
        response = {'message' : "The chain is the longest one. All Good.", 
                    'new_chain': blockchain.chain}
    return jsonify(response), 200

# Running the app 
app.run(host = '0.0.0.0', port = 5000, debug=True)


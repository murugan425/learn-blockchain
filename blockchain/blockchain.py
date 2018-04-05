#author: murguan425

#import the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify


#PART1: Create a blockchain
class BlockChain:
    def __init__(self):
        self.chain = []
        self.create_block(proof = '1', previous_hash = '0')
        
    def create_block(self, proof, previous_hash):
        block = {"index": len(self.chain) + 1,
                 "timestamp": str(datetime.datetime.now()),
                 "proof": proof,
                 "previous_hash": previous_hash}
        self.chain.append(block)
        return block
    
    def get_prev_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        valid_proof = False
        while valid_proof is False:
            #logic inside the sha256 should be non-symmetrical & complex
            hash_key_number = hashlib.sha256(str(new_proof*3 - previous_proof*2).encode()).hexdigest()
            if hash_key_number[:4] == '0000':
                valid_proof = True
            else:
                new_proof += 1
        return new_proof
        
    def hash(self, block):
        #check the hashkey of the previous block
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            #check the previous hash in each block is equal to the previous block hash key
            if block['previous_hash'] != self.hash(previous_block):
                return False
            #proof of work in each block is valid as per the proof of work pblm
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_key_number = hashlib.sha256(str(proof*3 - previous_proof*2).encode()).hexdigest()
            if hash_key_number[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True


            
        

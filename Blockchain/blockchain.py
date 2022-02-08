# Module 1 - Creamos la Blockchain ------------------------------------------

import datetime, hashlib, json
from flask import  Flask, jsonify

# Parte 1 - Creando la Blockchain

class Blockchain:
    
    # método init siempre que se inicia la clase
    # siempre el mismo argumento self, refiere al objeto blockchain instanciado cuando se ejecuta la clase Blockchain
    # y todas las var/func precedidas por self se referiran a ese objeto blockchain
    def __init__(self):
        
        # la cadena que contiene los bloques, una list
        self.chain = []
        # instancia objeto génesis, siempre el primero
        # arg 1: cada block tiene su proof of work, aqui arbitrario
        # arg 2: al ser el genesis no tiene hash previo
        self.create_block(proof = 1, previous_hash = '0')
    
    # crea el bloque después de su minado y lo añade a la blockchain con el append
    # self xq usa las variables de nuestro objeto blockchain
    # proof basado en el problema propuesto
    # previous hash que une los bloques en la blockchain
    def create_block(self, proof, previous_hash):
        
        # dictionary con las 4 keys esenciales del bloque
        # index tamaño de la blockchain + 1. usa el self porque es el obj blockchain
        # timestamp de la creación del bloque casteado a string
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
        
        # añadimos cloque a la cadena en la que estemos con self.chain 
        self.chain.append(block)
        # necesario para trabajar con ello (postman)
        return block
    
    # método para recuperar el bloque previo de la blockchain
    def get_previous_block(self):
        
        # con el index -1 recuperamos el último bloque de la lista
        return self.chain[-1]
    
    # PROOF OF WORK: dato (0000----) que el minero tiene que encontrar para crear un bloque nuevo
    # self xq lo aplicamos a la instancia de la clase
    # previous_proof xq lo tenemos en cuenta para solucionar el problema y crear la proof actual
    def proof_of_work(self, previous_proof):
        
        # conteo de cuantos loops hace el while
        new_proof = 1
        # false en cada intento para el while de abajo hasta la solución
        check_proof = False
        
        while check_proof is False:
            
            # buscamos el hash string de 64 caracteres usando el new proof y el previous proof
            # la operación debe ser asimétrica para evitar que se repita cada dos bloques (si fuera new_proof + previous_proof)
            # casteado a string y con encode() para que lo acepte el método sha256, y el hexdigest() para que lo saque en formato 64 car
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            
            # chequeamos los cuatro primeros ceros
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
                check_proof = False
            
        return new_proof
    
    # recibe el block y lo devuelve como hash encriptado con SHA256
    def hash(self, block):
        
        # de la lib json hacemos dumps para castear a string el dictionary
        # sort_keys true es que se ordena por las keys
        encoded_block = json.dumps(block, sort_keys = True).encode()
        
        return hashlib.sha256(encoded_block).hexdigest()
    
    # valida que el proof ha hecho cumplir la condición '0000' en el hash de cada bloque de la blockchain
    # y que el previous_hash de bloque actual (1)coincide con el hash del bloque anterior (0)
    # self porque lo aplicamos a la actual instacia blockchain
    # previos_block
    # actual_block
    def is_chain_valid(self, chain):
        
        # primer bloque de la cadena
        previous_block = chain[0]
        # aumenta según hacemos el while
        block_index = 1
        
        while block_index < len(chain):
            
            # usamos el block_index como index del bloque actual
            block = chain[block_index]
            
            # comparamos el previous_hash del actual bloque (1) del while 
            # con el hash del bloque anterior que recorremos (0)
            if block['previous_hash'] != self.hash(previous_block):
                # rompe el while
                return False
            
            previous_proof = previous_block['proof']
            proof = block['proof']
            
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            
            if hash_operation[:4] != '0000':
                
                return False
            
            # todo ok, la cadena ha sido validada
            # bloque previo pasa a ser el actual (1)
            previous_block = block
            # bloque actual pasa a +1 (2)
            block_index += 1
        
        # devuelve el True porque ha validado la blockchain
        return True
    
        
# Parte 2 - Minando la Blockchain
    
# Creamos Web App usando Flask (ya importado)
app = Flask(__name__)
    
# Creamos Blockchain para las pruebas
blockchain = Blockchain()

# Minando un nuevo bloque

# especificamos la URL que vamos a usar para llamar a la función de minado
@app.route('/mine_block', methods = ['GET'])

# implementamos la función de minado
def mine_block():
    
    # conseguimos previous proof
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    
    # minamos el proof del bloque que vamos a crear y añadir a la Blockchain
    # el método de minado recibe proof previo y genera actual
    proof = blockchain.proof_of_work(previous_proof)
    
    # para crear un bloque hace falta el proof actual y el previous hash
    previous_hash = blockchain.hash(previous_block)
    
    # creamos el nuevo bloque que se añade aautomaticamente
    block = blockchain.create_block(proof, previous_hash)
    
    # creamos respuesta como dictionary para mostrarlo en la demo
    response = {'index':block['index'],
                 'timestamp': block['timestamp'],
                 'proof': block['proof'],
                 'previous_hash': block['previous_hash'],
                 'message': 'Contratulations, you just mined a new block!'}
    
    # usamos el código HTTP 200 para decir que el GET ha sido OK
    return jsonify(response), 200
    
# mostramos la blockchain entera
@app.route('/get_chain', methods = ['GET'])

# recupera toda la Blockchain
def get_chain():
    
    response = {'length': len(blockchain.chain),
                'chain': blockchain.chain}
    
    return jsonify(response), 200

# comprobamos si la Blockchain es válida
@app.route('/is_valid', methods = ['GET'])

def is_valid():
    
    # le pasamos el método is_valid_chain
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    
    if is_valid:        
        response = {'message': 'The Blockchain is all good so far!',
                    'length': 'Size: ' + str(len(blockchain.chain))}
    else:
        response = {'message': 'The Blockchain has some issues, please inspect',
                    'failing block': str(len(blockchain.chain))}
    
    return jsonify(response), 200
    
# ejecutamos la app desde la app Flask para hacer requests desde Postman
# dos param: 0.0.0.0 púiblico para usuarios y puerto 5000 en Flask
app.run(host = '0.0.0.0', port = 5000)
    
    
    
    
    
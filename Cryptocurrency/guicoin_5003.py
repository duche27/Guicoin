# Module 2 - Create a Cryptocurrency ------------------------------------------

# necesitaremos libreria requests - CMD - pip install requests==2.18.4

import datetime, hashlib, json
# request para conectar los nodos descentralizados por medio de funcion get de json
from flask import  Flask, jsonify, request
# para coger el nodo correcto con la misma blockchain (consensus)
import requests
# para crear una address para cada nodo
from uuid import uuid4
# para crear la URL de la address de cada nodo
from urllib.parse import urlparse

# Parte 1 - Creando la cryptomoneda

class Blockchain:
    
    # método init siempre que se inicia la clase
    # siempre el mismo argumento self, refiere al objeto blockchain instanciado cuando se ejecuta la clase Blockchain
    # y todas las var/func precedidas por self se referiran a ese objeto blockchain
    def __init__(self):
        
        # la cadena que contiene los bloques, una list
        self.chain = []
        
        # creamos list con las transacciones
        # antes de crear los bloques ya que tienen que añadirse a ellos 
        self.transactions = []
        
        # instancia objeto génesis, siempre el primero
        # arg 1: cada block tiene su proof of work, aquí 1 por ser 1º
        # arg 2: al ser el genesis no tiene hash previo
        self.create_block(proof = 1, previous_hash = '0')
        
        # creamos los nodos para la descentralización
        # es un set xq no admite valores duplicados
        self.nodes = set()
    
    # crea el bloque después de su minado y lo añade a la blockchain con el append
    # self xq usa las variables de nuestro objeto blockchain de nuestra clase blockchain
    # proof basado en el problema propuesto
    # previous hash que une los bloques en la blockchain
    def create_block(self, proof, previous_hash):
        
        # dictionary con las 4 keys esenciales del bloque
        # index tamaño de la blockchain + 1. usa el self porque es el obj blockchain
        # timestamp de la creación del bloque casteado a string
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        
        # una vez añadidas las transacciones al nuevo bloque, vaciamos la lista
        self.transactions = []
        # añadimos bloque a la cadena en la que estemos con self.chain 
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
            # con el hash del bloque anterior al que recorremos (0)
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
    
    # creamos transacciones con formato concreto
    def add_transaction(self, sender, receiver, amount):
        
        # append del dictionary con los datos de la transacción
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        
        # devolvemos el index del block que recibe las transacciones
        previous_block = self.get_previous_block()
        # es el bloque previo último de la blockchain + 1
        return previous_block['index'] + 1
     
    # añadimos nuevo nodo al set de nodos creado en el init
    def add_node(self, address):
        
        # parseamos url a address con el método importado
        parsed_url = urlparse(address)
        
        # añadimos el netloc de la address al set
        self.nodes.add(parsed_url.netloc)
    
    # comienza el consensus
    # self xq llamamos la función en un nodo específico, 
    # ya que cada nodo contiene una versión de la blockchain
    def replace_chain(self):
        
        # toda la red de nodos, el set
        network = self.nodes
    
        # tendrá que sustituir la blockchain del nodo por la más larga
        longest_chain = None        
        max_length = len(self.chain)
        
        # iteramos sobre los nodos para encontrar el de la chain más larga
        for node in network:
            
            # nos la da la librería resquests importada
            # se usa para recuperar esa instrucción GET y poder usarlo en otra GET (replace_chain)
            # cada address se puede conseguir incluyendo el node en el string con la sintaxis f'{x}'
            response = requests.get(f'http://{node}/get_chain')
            
            # si el http status es 200 = OK
            if response.status_code == 200:
                
                # conseguimos el tamaño de la chain
                length = response.json()['length']
                chain = response.json()['chain']
                
                # comprobamos la longitud respecto al resto de chains y si es válida
                if length > max_length and self.is_chain_valid(chain):
                    
                    max_length = length
                    longest_chain = chain
                    
        # en Python esto significa que no es None porque ha sido actualizada
        if longest_chain:
            
            self.chain = longest_chain
            return True
        
        # si hasta aquí no ha cambiado nada, devuelve False
        # significa que estábamos en la chain más larga
        return False
            
            
# Parte 2 - Interactuando con la Blockchain
    
# Creamos Web App usando Flask (ya importado)
app = Flask(__name__)

# Creamos una address para el el nodo del puerto inicial 5000
# uuid4 genera una dirección única de forma random con guiones (los quitamos)
node_address = str(uuid4()).replace('-','')
    
# Creamos Blockchain para las pruebas
blockchain = Blockchain()

# Minando un nuevo bloque

# especificamos la URL que vamos a usar para llamar a la función de minado
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    
    # conseguimos previous proof
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    
    # minamos el proof del bloque que vamos a crear y añadir a la Blockchain
    # el método de minado recibe proof previo y genera actual
    proof = blockchain.proof_of_work(previous_proof)
    
    # para crear un bloque hace falta el proof actual y el previous hash
    previous_hash = blockchain.hash(previous_block)
    
    # recibimos las transacciones de la list para añadirlas al bloque
    # esta trans es para recibir la recompensa de minado, es única por bloque
    blockchain.add_transaction(sender = node_address, receiver = 'Yo', amount = 1)
    
    # creamos el nuevo bloque que se añade aautomaticamente
    block = blockchain.create_block(proof, previous_hash)
    
    # creamos respuesta como dictionary para mostrarlo en la demo
    response = {'index':block['index'],
                 'timestamp': block['timestamp'],
                 'proof': block['proof'],
                 'previous_hash': block['previous_hash'],
                 'message': 'Contratulations, you just mined a new block!',
                 'transactions': block['transactions']}
    
    # usamos el código HTTP 200 para decir que el GET ha sido OK
    return jsonify(response), 200
    
# recuperamos la blockchain entera
@app.route('/get_chain', methods = ['GET'])
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
                    'failing block': 'Ha fallado en el bloque: ' + str(len(blockchain.chain))}
    
    return jsonify(response), 200

# añadimos nueva transaction a la Blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    
    # recibimos el post del json posted en Postman
    json = request.get_json()
    
    # comprobamos el formato del json posteado, que es este
    transaction_keys = ['sender', 'receiver', 'amount']
    
    if not all (key in json for key in transaction_keys):
        
        # informamos y devolvemos un HTTP status de error solicitud
        return 'Faltan elemenos de la transacción!', 401
    
    # si es correcto lo metemos en el bloque actual
    index = blockchain.add_transaction(json['sender'],json['receiver'],json['amount'])
    
    response = {'message': f'La nueva transacción será añadida al bloque: {index}'}

    return jsonify(response), 201

# Parte 3 - Descentralizando nuestra Blockchain
    
# conectamos los nuevos nodos a la red descentralizada
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    
    # saco las direcciones del json (pueden ser varias)
    json = request.get_json()
    nodes = json.get('nodes')
    
    # verificación de los nodos posteados
    if nodes is None:
        
        return 'Falta la dirección del nodo', 401
    
    # si están OK los añadimos al set uno a uno
    for node in nodes:
        
        blockchain.add_node(node)
    
    response = {'message': 'Se añadieron los nodos satisfactoriamente',
                'total_nodes':  'La blockchain de Guicoin ahora tiene ' + str(len(blockchain.nodes)) + ' nodos',
                'nodes_list': list(blockchain.nodes)}
    
    return jsonify(response), 201

# consultamos los nodos presentes en la red
@app.route('/get_network', methods = ['GET'])
def get_network():
    
    # consigo la red
    network = list(blockchain.nodes)
    
    # la muestro
    response = {'network': network}
    
    return jsonify(response), 200

# sustituímos la cadena por la más larga del nodo que sea si es necesario
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    
    # método para reemplazar si procede que devuelve True si lo hace
    is_chain_replaced = blockchain.replace_chain()
    
    if is_chain_replaced:
        
        response = {'message': 'La cadena ha sido actualizada',
                    'new_chain': blockchain.chain}
        
    else:
        
        response = {'message': 'La cadena está ya actualizada',
                    'actual_chain': blockchain.chain}
        
    return jsonify(response), 200
    

# ejecutamos la app desde la app Flask para hacer requests desde Postman
# dos param: 0.0.0.0 público para usuarios y puerto 5000 en Flask
app.run(host = '0.0.0.0', port = 5003)
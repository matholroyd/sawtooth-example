from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory

context = create_context('secp256k1')
private_key = context.new_random_private_key()
signer = CryptoFactory(context).new_signer(private_key)


####################### 
# Encoding Your Payload
####################### 

import cbor

payload = {
    'Verb': 'inc',
    'Name': 'foo',
    'Value': 10}

payload_bytes = cbor.dumps(payload)


# 1. CREATE TRANSACTION HEADER

from hashlib import sha512
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader

txn_header_bytes = TransactionHeader(
    family_name='intkey',
    family_version='1.0',
    inputs=['1cf1266e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7'],
    outputs=['1cf1266e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7'],
    signer_public_key=signer.get_public_key().as_hex(),
    # In this example, we're signing the batch with the same private key,
    # but the batch can be signed by another party, in which case, the
    # public key will need to be associated with that key.
    batcher_public_key=signer.get_public_key().as_hex(),
    # In this example, there are no dependencies.  This list should include
    # an previous transaction header signatures that must be applied for
    # this transaction to successfully commit.
    # For example,
    # dependencies=['540a6803971d1880ec73a96cb97815a95d374cbad5d865925e5aa0432fcf1931539afe10310c122c5eaae15df61236079abbf4f258889359c4d175516934484a'],
    dependencies=[],
    payload_sha512=sha512(payload_bytes).hexdigest()
).SerializeToString()


# 2. CREATE TRANSACTION

from sawtooth_sdk.protobuf.transaction_pb2 import Transaction

signature = signer.sign(txn_header_bytes)

txn = Transaction(
    header=txn_header_bytes,
    header_signature=signature,
    payload=payload_bytes
)


# 3. (optional) Encode the Transaction(s)

# from sawtooth_sdk.protobuf import TransactionList
#
# txn_list_bytes = TransactionList(
#     transactions=[txn1, txn2]
# ).SerializeToString()
#
# txn_bytes = txn.SerializeToString()

####################
# Building the Batch
####################

# 1. Create the BatchHeader

from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader

txns = [txn]

batch_header_bytes = BatchHeader(
    signer_public_key=signer.get_public_key().as_hex(),
    transaction_ids=[txn.header_signature for txn in txns],
).SerializeToString()


# 2. Create the Batch

from sawtooth_sdk.protobuf.batch_pb2 import Batch

signature = signer.sign(batch_header_bytes)

batch = Batch(
    header=batch_header_bytes,
    header_signature=signature,
    transactions=txns
)


# 3. Encode the Batch(es) in a BatchList

from sawtooth_sdk.protobuf.batch_pb2 import BatchList

batch_list_bytes = BatchList(batches=[batch]).SerializeToString()


#####################################
# Submitting Batches to the Validator
#####################################

import urllib.request
from urllib.error import HTTPError

try:
    request = urllib.request.Request(
        'http://localhost:8008/batches',
        batch_list_bytes,
        method='POST',
        headers={'Content-Type': 'application/octet-stream'})
    response = urllib.request.urlopen(request)

except HTTPError as e:
    response = e.file
    
output = open('intkey.batches', 'wb')
output.write(batch_list_bytes)    




import base64
import json



try:
    request = urllib.request.Request(
        'http://localhost:8008/state/1cf1266e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7',
        method='GET',
        headers={'Content-Type': 'application/octet-stream'}
        )

    response = urllib.request.urlopen(request)

except HTTPError as e:
    response = e.file

# print(response)


j = json.loads(response.read().decode('utf-8'))
# print(j)

# print(j['data'])

data = cbor.loads(base64.b64decode(j['data']))

print(data)

# print(data)
print(data['foo'])


# from sawtooth_intkey.intkey_message_factory import IntkeyMessageFactory
# factory = IntkeyMessageFactory()
#
# import base64
#
# def send_get_response(name, value):
#     # received = self.validator.expect(
#     #     factory.create_get_request(
#     #         name))
#
#     # self.validator.respond(
#     #     factory.create_get_response(
#     #         name, value),
#     #     received)
#
#     received = factory.create_get_request(name)
#     print(received)
#
#     result = factory.create_get_response(name, value)
#     print(result)
#
#     data = result.entries[0].data
#
#     print(cbor.loads(data)[name])
#
#     # s = base64.b64decode(result.entries[0].data)
#
# send_get_response('foo', 10)

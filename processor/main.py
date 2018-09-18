from sawtooth_sdk.processor.core import TransactionProcessor
from handler import XoTransactionHandler

def main():
    print("Starting up...")
    
    # In docker, the url would be the validator's container name with
    # port 4004
    processor = TransactionProcessor(url='tcp://127.0.0.1:4004')

    handler = XoTransactionHandler("test_namespace")

    processor.add_handler(handler)

    processor.start()
    
    print("Processor started!!")
    
    
main()
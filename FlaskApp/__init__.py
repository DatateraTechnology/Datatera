from flask import Flask, jsonify, render_template
from ocean_lib.ocean.ocean import Ocean
from ocean_lib.config import Config
from ocean_lib.web3_internal.wallet import Wallet
from ocean_lib.web3_internal.currency import to_wei
from flask_swagger import swagger
from ocean_lib.data_provider.data_service_provider import DataServiceProvider
from ocean_lib.services.service import Service
from ocean_lib.common.agreements.service_types import ServiceTypes
from ocean_lib.assets import trusted_algorithms
from ocean_lib.web3_internal.constants import ZERO_ADDRESS
from ocean_lib.models.compute_input import ComputeInput
import pickle, numpy, time
from matplotlib import pyplot
from azure.storage.blob import BlobClient
import urllib.request, json
import os, uuid

app = Flask(__name__)

@app.route("/")
def index():
    return (
        "Try /hello/Chris for parameterized Flask route.\n"
        "Try /module for module import guidance"
    )

@app.route("/hello/<name>", methods=['GET'])
def hello(name: str):
    return f"hello {name}"

@app.route('/api')
def get_api():
    return render_template('swaggerui.html')

config = Config('config.ini')
ocean = Ocean(config)

print(f"config.network_url = '{config.network_url}'")
print(f"config.metadata_cache_uri = '{config.metadata_cache_uri}'")
print(f"config.provider_url = '{config.provider_url}'")

#Constants
Alice_Wallet_Private_Key = "0x5d75837394b078ce97bc289fa8d75e21000573520bfa7784a9d28ccaae602bf8"
Bob_Wallet_Private_Key = "0xef4b441145c1d0f3b4bc6d61d29f5c6e502359481152f869247c7a4244d45209"

Dataset_Url = "https://raw.githubusercontent.com/trentmc/branin/main/branin.arff"
Algorithm_Url = "https://raw.githubusercontent.com/trentmc/branin/main/gpr.py"

#Create Wallet for Data Provider
alice_wallet = Wallet(ocean.web3, Alice_Wallet_Private_Key, 
config.block_confirmations, config.transaction_timeout)

#Create Wallet for Data Consumer
bob_wallet = Wallet(ocean.web3, Bob_Wallet_Private_Key, 
config.block_confirmations, config.transaction_timeout)

#Create Data Provider Wallet
@app.route("/alpha/createwallet", methods=["GET"], endpoint='create_wallet')
def create_wallet():

    return jsonify(f"alice_wallet.address = '{alice_wallet.address}'")

if __name__ == "__main__":
    app.run()

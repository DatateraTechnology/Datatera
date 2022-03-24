from flask import Flask, jsonify
from ocean_lib.ocean.ocean import Ocean
from ocean_lib.config import Config
from ocean_lib.example_config import ExampleConfig
from ocean_lib.web3_internal.wallet import Wallet
from ocean_lib.web3_internal.currency import to_wei
from flask_swagger import swagger
from flask import Flask, jsonify, render_template

# Creating a new "app" by using the Flask constructor. Passes __name__ as a parameter.
app = Flask(__name__)

@app.route("/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "Datatera Alpha"
    return jsonify(swag)

@app.route('/api/docs')
def get_docs():
    print('sending docs')
    return render_template('swaggerui.html')

# Print Core Ocean Protocol Modules url
config = Config('./config.ini')
#config = ExampleConfig.get_config()
ocean = Ocean(config)

print(f"config.network_url = '{config.network_url}'")
print(f"config.metadata_cache_uri = '{config.metadata_cache_uri}'")
print(f"config.provider_url = '{config.provider_url}'")

# Annotation that allows the function to be hit at the specific URL.
@app.route("/")
# Generic Python function that returns "Hello Datatera!"
def index():
	return "Hello Datatera!"

# Annotation that allows the function to be hit at the specific URL. Indicates a GET HTTP method.
@app.route("/alpha/1.0/publishdataset", methods=["GET"], endpoint='publish_dataset')
# Function that will run when the endpoint is hit.
def publish_dataset():

    alice_wallet = Wallet(ocean.web3, '0x5d75837394b078ce97bc289fa8d75e21000573520bfa7784a9d28ccaae602bf8', 
    config.block_confirmations, config.transaction_timeout)
    print(f"alice_wallet.address = '{alice_wallet.address}'")

    DATA_datatoken = ocean.create_data_token('DATA1', 'DATA1', alice_wallet, blob=ocean.config.metadata_cache_uri)
    DATA_datatoken.mint(alice_wallet.address, to_wei(100), alice_wallet)
    return jsonify(f"DATA_datatoken.address = '{DATA_datatoken.address}'")

# Annotation that allows the function to be hit at the specific URL with a parameter. 
# Indicates a GET HTTP method.
@app.route("/alpha/1.0/publishdataset/<string:wallet_address>", methods=["GET"], endpoint='publish_datasets')
# This function requires a parameter from the URL.
def publish_datasets(wallet_address):

    print(f"wallet_address = '{wallet_address}'")
    alice_wallet = Wallet(ocean.web3, wallet_address, 
    config.block_confirmations, config.transaction_timeout)
    print(f"alice_wallet.address = '{alice_wallet.address}'")

    DATA_datatoken = ocean.create_data_token('DATA1', 'DATA1', alice_wallet, blob=ocean.config.metadata_cache_uri)
    DATA_datatoken.mint(alice_wallet.address, to_wei(100), alice_wallet)
    return jsonify(f"DATA_datatoken.address = '{DATA_datatoken.address}'")

# Checks to see if the name of the package is the run as the main package.
#if __name__ == "__main__":
	# Runs the Flask application only if the publish_dataset.py file is being run.
	#app.run()

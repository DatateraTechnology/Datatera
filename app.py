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

app = Flask(__name__)

@app.route("/")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "v.1.0"
    swag['info']['title'] = "Welcome to Datatera Alpha"
    return jsonify(swag)
    #return 'The value of __name__ is {}'.format(__name__)

@app.route('/api')
def get_docs():
    print('sending docs')
    return render_template('swaggerui.html')

config = Config('config.ini')
ocean = Ocean(config)

print(f"config.network_url = '{config.network_url}'")
print(f"config.metadata_cache_uri = '{config.metadata_cache_uri}'")
print(f"config.provider_url = '{config.provider_url}'")

#Create Data Provider Wallet
@app.route("/alpha/1.0/createwallet/<string:wallet_address>", methods=["GET"], endpoint='create_wallet')
def create_wallet(wallet_address):
   
    alice_wallet = Wallet(ocean.web3, wallet_address, 
    config.block_confirmations, config.transaction_timeout)

    return jsonify(f"alice_wallet.address = '{alice_wallet.address}'")

#Tokenize Dataset
@app.route("/alpha/1.0/tokenizedataset/<string:wallet_address>", methods=["GET"], endpoint='tokenize_dataset')
def tokenize_dataset(wallet_address):
  
    alice_wallet = Wallet(ocean.web3, wallet_address, 
    config.block_confirmations, config.transaction_timeout)

    DATA_datatoken = ocean.create_data_token('DATA1', 'DATA1', alice_wallet, blob=ocean.config.metadata_cache_uri)
    DATA_datatoken.mint(alice_wallet.address, to_wei(100), alice_wallet)

    return jsonify(f"DATA_datatoken.address = '{DATA_datatoken.address}'")
  
#Create Metadata
@app.route("/alpha/1.0/createmetadata/<string:url>", methods=["GET"], endpoint='create_metadata')
def create_metadata(url):

    DATA_metadata = {
    "main": {
        "type": "dataset",
        "files": [
	  {
	    "url": url,
	    "index": 0,
	    "contentType": "text/text"
	  }
	],
	"name": "branin", "author": "Trent", "license": "CC0",
	"dateCreated": "2019-12-28T10:55:11Z"
    }
}

    return jsonify(f"DATA_metadata = '{DATA_metadata}'")

#Create Data Service
@app.route("/alpha/1.0/createdataservice/<string:wallet_address>", methods=["GET"], endpoint='create_dataservice')
def create_dataservice(wallet_address):

    DATA_service_attributes = {
    "main": {
        "name": "DATA_dataAssetAccessServiceAgreement",
        "creator": wallet_address,
        "timeout": 3600 * 24,
        "datePublished": "2019-12-28T10:55:11Z",
        "cost": 1.0,
    }
}
    return jsonify(f"DATA_service_attributes = '{DATA_service_attributes}'")

#Publish Metadata
@app.route("/alpha/1.0/publishmetadata/<string:wallet_address>/<string:url>", methods=["GET"], endpoint='publish_metadata')
def publish_metadata(wallet_address, url):
    
    DATA_metadata = {
    "main": {
        "type": "dataset",
        "files": [
	  {
	    "url": url,
	    "index": 0,
	    "contentType": "text/text"
	  }
	],
	"name": "branin", "author": "Trent", "license": "CC0",
	"dateCreated": "2019-12-28T10:55:11Z"
    }
}

    DATA_service_attributes = {
    "main": {
        "name": "DATA_dataAssetAccessServiceAgreement",
        "creator": wallet_address,
        "timeout": 3600 * 24,
        "datePublished": "2019-12-28T10:55:11Z",
        "cost": 1.0,
    }
}

    provider_url = DataServiceProvider.get_url(ocean.config)

    DATA_compute_service = Service(
        service_endpoint=provider_url,
        service_type=ServiceTypes.CLOUD_COMPUTE,
        attributes=DATA_service_attributes
    )

    alice_wallet = Wallet(ocean.web3, wallet_address, 
    config.block_confirmations, config.transaction_timeout)

    DATA_datatoken = ocean.create_data_token('DATA1', 'DATA1', alice_wallet, blob=ocean.config.metadata_cache_uri)
    DATA_datatoken.mint(alice_wallet.address, to_wei(100), alice_wallet)
 
    DATA_ddo = ocean.assets.create(
    metadata = DATA_metadata,
    publisher_wallet = alice_wallet,
    services = [DATA_compute_service],
    data_token_address = DATA_datatoken.address)

    return jsonify(f"DATA_ddo.did = '{DATA_ddo.did}'")

#Tokenize Algorithm
@app.route("/alpha/1.0/tokenizealgorithm/<string:wallet_address>", methods=["GET"], endpoint='tokenize_algorithm')
def tokenize_algorithm(wallet_address):

    alice_wallet = Wallet(ocean.web3, wallet_address, 
    config.block_confirmations, config.transaction_timeout)

    ALG_datatoken = ocean.create_data_token('ALG1', 'ALG1', alice_wallet, blob=ocean.config.metadata_cache_uri)
    ALG_datatoken.mint(alice_wallet.address, to_wei(100), alice_wallet)

    return jsonify(f"ALG_datatoken.address = '{ALG_datatoken.address}'")

#Publish Algorithm
@app.route("/alpha/1.0/publishalgorithm/<string:wallet_address>", methods=["GET"], endpoint='publish_algorithm')
def publish_algorithm(wallet_address):

    alice_wallet = Wallet(ocean.web3, wallet_address, 
    config.block_confirmations, config.transaction_timeout)

    ALG_datatoken = ocean.create_data_token('ALG1', 'ALG1', alice_wallet, blob=ocean.config.metadata_cache_uri)
    ALG_datatoken.mint(alice_wallet.address, to_wei(100), alice_wallet)
    
    ALG_metadata =  {
    "main": {
        "type": "algorithm",
        "algorithm": {
            "language": "python",
            "format": "docker-image",
            "version": "0.1",
            "container": {
              "entrypoint": "python $ALGO",
              "image": "oceanprotocol/algo_dockers",
              "tag": "python-branin"
            }
        },
        "files": [
	  {
	    "url": "https://raw.githubusercontent.com/trentmc/branin/main/gpr.py",
	    "index": 0,
	    "contentType": "text/text",
	  }
	],
	"name": "gpr", "author": "Trent", "license": "CC0",
	"dateCreated": "2020-01-28T10:55:11Z"
    }
}

    ALG_service_attributes = {
            "main": {
                "name": "ALG_dataAssetAccessServiceAgreement",
                "creator": alice_wallet.address,
                "timeout": 3600 * 24,
                "datePublished": "2020-01-28T10:55:11Z",
                "cost": 1.0,
            }
        }

    provider_url = DataServiceProvider.get_url(ocean.config)

    ALG_access_service = Service(
        service_endpoint = provider_url,
        service_type = ServiceTypes.CLOUD_COMPUTE,
        attributes = ALG_service_attributes
    )

    ALG_ddo = ocean.assets.create(
    metadata=ALG_metadata,
    publisher_wallet=alice_wallet,
    services=[ALG_access_service],
    data_token_address=ALG_datatoken.address)

    return jsonify(f"ALG did = '{ALG_ddo.did}'")

#Authorize Algorithm
@app.route("/alpha/1.0/authorizealgorithm/<string:bob_wallet_address>/<string:alice_wallet_address>/<string:data_url>/<string:algo_url>", methods=["GET"], endpoint='authorize_algorithm')
def authorize_algorithm(bob_wallet_address, alice_wallet_address, data_url, algo_url):

    alice_wallet = Wallet(ocean.web3, alice_wallet_address, 
    config.block_confirmations, config.transaction_timeout)

    DATA_metadata = {
        "main": {
            "type": "dataset",
            "files": [
        {
            "url": data_url,
            "index": 0,
            "contentType": "text/text"
        }
        ],
        "name": "branin", "author": "Trent", "license": "CC0",
        "dateCreated": "2019-12-28T10:55:11Z"
        }
    }

    DATA_service_attributes = {
    "main": {
        "name": "DATA_dataAssetAccessServiceAgreement",
        "creator": alice_wallet_address,
        "timeout": 3600 * 24,
        "datePublished": "2019-12-28T10:55:11Z",
        "cost": 1.0,
    }
}
    DATA_compute_service = Service(
        service_endpoint=provider_url,
        service_type=ServiceTypes.CLOUD_COMPUTE,
        attributes=DATA_service_attributes
    )

    DATA_datatoken = ocean.create_data_token('DATA1', 'DATA1', alice_wallet, blob=ocean.config.metadata_cache_uri)
    DATA_datatoken.mint(alice_wallet.address, to_wei(100), alice_wallet)
 
    DATA_ddo = ocean.assets.create(
    metadata = DATA_metadata,
    publisher_wallet = alice_wallet,
    services = [DATA_compute_service],
    data_token_address = DATA_datatoken.address)

    ALG_datatoken = ocean.create_data_token('ALG1', 'ALG1', alice_wallet, blob=ocean.config.metadata_cache_uri)
    ALG_datatoken.mint(alice_wallet.address, to_wei(100), alice_wallet)
    
    ALG_metadata =  {
    "main": {
        "type": "algorithm",
        "algorithm": {
            "language": "python",
            "format": "docker-image",
            "version": "0.1",
            "container": {
              "entrypoint": "python $ALGO",
              "image": "oceanprotocol/algo_dockers",
              "tag": "python-branin"
            }
        },
        "files": [
	  {
	    "url": algo_url,
	    "index": 0,
	    "contentType": "text/text",
	  }
	],
	"name": "gpr", "author": "Trent", "license": "CC0",
	"dateCreated": "2020-01-28T10:55:11Z"
    }
}

    ALG_service_attributes = {
            "main": {
                "name": "ALG_dataAssetAccessServiceAgreement",
                "creator": alice_wallet.address,
                "timeout": 3600 * 24,
                "datePublished": "2020-01-28T10:55:11Z",
                "cost": 1.0,
            }
        }

    provider_url = DataServiceProvider.get_url(ocean.config)

    ALG_access_service = Service(
        service_endpoint = provider_url,
        service_type = ServiceTypes.CLOUD_COMPUTE,
        attributes = ALG_service_attributes
    )

    ALG_ddo = ocean.assets.create(
    metadata=ALG_metadata,
    publisher_wallet=alice_wallet,
    services=[ALG_access_service],
    data_token_address=ALG_datatoken.address)

    trusted_algorithms.add_publisher_trusted_algorithm(DATA_ddo, ALG_ddo.did, config.metadata_cache_uri)
    ocean.assets.update(DATA_ddo, publisher_wallet = alice_wallet)

    bob_wallet = Wallet(
        ocean.web3,
        bob_wallet_address,
        config.block_confirmations,
        config.transaction_timeout,
    )

    DATA_datatoken.transfer(bob_wallet.address, to_wei(5), from_wallet = alice_wallet)
    ALG_datatoken.transfer(bob_wallet.address, to_wei(5), from_wallet = alice_wallet)

# Checks to see if the name of the package is the run as the main package.
#if __name__ == "__main__":
	# Runs the Flask application only if the publish_dataset.py file is being run.
	#app.run()

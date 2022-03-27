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
import azure.functions as func

app = Flask(__name__)

@app.route("/")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "v.1.0"
    swag['info']['title'] = "Welcome to Datatera Alpha"
    return jsonify(swag)

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

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Each request is redirected to the WSGI handler.
    """
    return func.WsgiMiddleware(app.wsgi_app).handle(req, context)

#Create Data Provider Wallet
@app.route("/alpha/createwallet", methods=["GET"], endpoint='create_wallet')
def create_wallet():

    return jsonify(f"alice_wallet.address = '{alice_wallet.address}'")

#Tokenize Dataset
@app.route("/alpha/tokenizedataset", methods=["GET"], endpoint='tokenize_dataset')
def tokenize_dataset():

    DATA_datatoken = ocean.create_data_token('DATA1', 'DATA1', alice_wallet, blob=ocean.config.metadata_cache_uri)
    DATA_datatoken.mint(alice_wallet.address, to_wei(100), alice_wallet)

    return jsonify(f"DATA_datatoken.address = '{DATA_datatoken.address}'")

#Publish Metadata
@app.route("/alpha/publishmetadata", methods=["GET"], endpoint='publish_metadata')
def publish_metadata():

    DATA_metadata = {
    "main": {
        "type": "dataset",
        "files": [
	  {
	    "url": Dataset_Url,
	    "index": 0,
	    "contentType": "text/text"
	  }
	],
	"name": "branin", "author": "Trent", "license": "CC0",
	"dateCreated": "2019-12-28T10:55:11Z"}
    }

    DATA_service_attributes = {
    "main": {
        "name": "DATA_dataAssetAccessServiceAgreement",
        "creator": Alice_Wallet_Private_Key,
        "timeout": 3600 * 24,
        "datePublished": "2019-12-28T10:55:11Z",
        "cost": 1.0}
    }

    provider_url = DataServiceProvider.get_url(ocean.config)

    DATA_compute_service = Service(
        service_endpoint = provider_url,
        service_type = ServiceTypes.CLOUD_COMPUTE,
        attributes=DATA_service_attributes)

    DATA_datatoken = ocean.create_data_token('DATA1', 'DATA1', alice_wallet, blob=ocean.config.metadata_cache_uri)
    DATA_datatoken.mint(alice_wallet.address, to_wei(100), alice_wallet)
 
    DATA_ddo = ocean.assets.create(
    metadata = DATA_metadata,
    publisher_wallet = alice_wallet,
    services = [DATA_compute_service],
    data_token_address = DATA_datatoken.address)

    return jsonify(f"DATA_ddo.did = '{DATA_ddo.did}'")

#Tokenize Algorithm
@app.route("/alpha/tokenizealgorithm", methods=["GET"], endpoint='tokenize_algorithm')
def tokenize_algorithm():

    ALG_datatoken = ocean.create_data_token('ALG1', 'ALG1', alice_wallet, blob=ocean.config.metadata_cache_uri)
    ALG_datatoken.mint(alice_wallet.address, to_wei(100), alice_wallet)

    return jsonify(f"ALG_datatoken.address = '{ALG_datatoken.address}'")

#Publish Algorithm
@app.route("/alpha/publishalgorithm", methods=["GET"], endpoint='publish_algorithm')
def publish_algorithm():

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
	    "url": Algorithm_Url,
	    "index": 0,
	    "contentType": "text/text",
	  }
	],
	"name": "gpr", "author": "Trent", "license": "CC0",
	"dateCreated": "2020-01-28T10:55:11Z"}
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
        attributes = ALG_service_attributes)

    ALG_ddo = ocean.assets.create(
    metadata = ALG_metadata,
    publisher_wallet = alice_wallet,
    services = [ALG_access_service],
    data_token_address = ALG_datatoken.address)

    return jsonify(f"ALG did = '{ALG_ddo.did}'")

#Authorize Algorithm
@app.route("/alpha/authorizealgorithm", methods=["GET"], endpoint='authorize_algorithm')
def authorize_algorithm():

    DATA_metadata = {
        "main": {
            "type": "dataset",
            "files": [
        {
            "url": Dataset_Url,
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
        "creator": alice_wallet.address,
        "timeout": 3600 * 24,
        "datePublished": "2019-12-28T10:55:11Z",
        "cost": 1.0,
        }
    }

    provider_url = DataServiceProvider.get_url(ocean.config)

    DATA_compute_service = Service(
        service_endpoint = provider_url,
        service_type = ServiceTypes.CLOUD_COMPUTE,
        attributes=DATA_service_attributes)

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
	    "url": Algorithm_Url,
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

    ALG_access_service = Service(
        service_endpoint = provider_url,
        service_type = ServiceTypes.CLOUD_COMPUTE,
        attributes = ALG_service_attributes)

    ALG_ddo = ocean.assets.create(
    metadata = ALG_metadata,
    publisher_wallet = alice_wallet,
    services = [ALG_access_service],
    data_token_address = ALG_datatoken.address)

    trusted_algorithms.add_publisher_trusted_algorithm(DATA_ddo, ALG_ddo.did, config.metadata_cache_uri)
    ocean.assets.update(DATA_ddo, publisher_wallet = alice_wallet)

    DATA_datatoken.transfer(bob_wallet.address, to_wei(5), from_wallet = alice_wallet)
    ALG_datatoken.transfer(bob_wallet.address, to_wei(5), from_wallet = alice_wallet)

    return jsonify(f"DATA_datatoken = '{DATA_datatoken}' ALG_datatoken = '{ALG_datatoken}'")

#Start Compute Job
@app.route("/alpha/computejob", methods=["GET"], endpoint='compute_job')
def compute_job():

    DATA_metadata = {
        "main": {
            "type": "dataset",
            "files": [
        {
            "url": Dataset_Url,
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
        "creator": alice_wallet.address,
        "timeout": 3600 * 24,
        "datePublished": "2019-12-28T10:55:11Z",
        "cost": 1.0,}
    }
    
    provider_url = DataServiceProvider.get_url(ocean.config)
    
    DATA_compute_service = Service(
        service_endpoint=provider_url,
        service_type = ServiceTypes.CLOUD_COMPUTE,
        attributes=DATA_service_attributes)

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
	    "url": Algorithm_Url,
	    "index": 0,
	    "contentType": "text/text",
	  }
	],
	"name": "gpr", "author": "Trent", "license": "CC0",
	"dateCreated": "2020-01-28T10:55:11Z"}
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

    ALG_access_service = Service(
        service_endpoint = provider_url,
        service_type = ServiceTypes.CLOUD_COMPUTE,
        attributes = ALG_service_attributes)

    ALG_ddo = ocean.assets.create(
    metadata = ALG_metadata,
    publisher_wallet = alice_wallet,
    services = [ALG_access_service],
    data_token_address = ALG_datatoken.address)

    trusted_algorithms.add_publisher_trusted_algorithm(DATA_ddo, ALG_ddo.did, config.metadata_cache_uri)
    ocean.assets.update(DATA_ddo, publisher_wallet = alice_wallet)

    DATA_datatoken.transfer(bob_wallet.address, to_wei(5), from_wallet = alice_wallet)
    ALG_datatoken.transfer(bob_wallet.address, to_wei(5), from_wallet = alice_wallet)

    DATA_did = DATA_ddo.did
    ALG_did = ALG_ddo.did
    DATA_DDO = ocean.assets.resolve(DATA_did)
    ALG_DDO = ocean.assets.resolve(ALG_did)

    compute_service = DATA_DDO.get_service('compute')
    algo_service = ALG_DDO.get_service('access')

    dataset_order_requirements = ocean.assets.order(
    DATA_did, bob_wallet.address, service_type = compute_service.type)
    
    DATA_order_tx_id = ocean.assets.pay_for_service(
    ocean.web3,
    dataset_order_requirements.amount,
    dataset_order_requirements.data_token_address,
    DATA_did,
    compute_service.index,
    ZERO_ADDRESS,
    bob_wallet,
    dataset_order_requirements.computeAddress)

    algo_order_requirements = ocean.assets.order(
    ALG_did, bob_wallet.address, service_type = algo_service.type)
    
    ALG_order_tx_id = ocean.assets.pay_for_service(
        ocean.web3,
        algo_order_requirements.amount,
        algo_order_requirements.data_token_address,
        ALG_did,
        algo_service.index,
        ZERO_ADDRESS,
        bob_wallet,
        algo_order_requirements.computeAddress)

    compute_inputs = [ComputeInput(DATA_did, DATA_order_tx_id, compute_service.index)]
    job_id = ocean.compute.start(
    compute_inputs,
    bob_wallet,
    algorithm_did = ALG_did,
    algorithm_tx_id = ALG_order_tx_id,
    algorithm_data_token = ALG_datatoken.address)

    time.sleep(30)

    print(f"Job Status: {ocean.compute.status(DATA_did, job_id, bob_wallet)}")

    time.sleep(30)

    print(f"Job Status: {ocean.compute.status(DATA_did, job_id, bob_wallet)}")

    time.sleep(30)

    print(f"Job Status: {ocean.compute.status(DATA_did, job_id, bob_wallet)}")

    time.sleep(30)

    print(f"Job Status: {ocean.compute.status(DATA_did, job_id, bob_wallet)}")

    result = ocean.compute.result_file(DATA_did, job_id, 0, bob_wallet)
    print(f"Result: {result}")

    model = pickle.loads(result)

    X0_vec = numpy.linspace(-5., 10., 15)
    X1_vec = numpy.linspace(0., 15., 15)
    X0, X1 = numpy.meshgrid(X0_vec, X1_vec)
    b, c, t = 0.12918450914398066, 1.5915494309189535, 0.039788735772973836
    u = X1 - b*X0**2 + c*X0 - 6
    r = 10.*(1. - t) * numpy.cos(X0) + 10
    Z = u**2 + r

    fig, ax = pyplot.subplots(subplot_kw={"projection": "3d"})
    ax.scatter(X0, X1, model, c="r", label="model")
    pyplot.title("Data + model")
    pyplot.show()

    return jsonify(f"Job Status: {ocean.compute.status(DATA_did, job_id, bob_wallet)}")

if __name__ == "__main__":
    app.run()

# Alpha version
Compute-To-Data Flow

Data Provider Private Key: 0x5d75837394b078ce97bc289fa8d75e21000573520bfa7784a9d28ccaae602bf8 <br />
Data Consumer Private Key: 0xef4b441145c1d0f3b4bc6d61d29f5c6e502359481152f869247c7a4244d45209

Dataset url: https://raw.githubusercontent.com/trentmc/branin/main/branin.arff <br />
Algorithm url: https://raw.githubusercontent.com/trentmc/branin/main/gpr.py

For more information about Compute-To-Data flow please visit:<br /> 
https://docs.oceanprotocol.com/references/read-the-docs/ocean-py/READMEs/c2d-flow.md

P.S To be able to test different datasets and algorithms we either need to change it in the source code as swagger cannot encode the url as a parameter properly or we can add parameters by modifiying the apis url not in swagger.

To test other blockchain test networks, we need to change the url for network in config.ini with the respective Infura endpoint and also respective provider endpoint which can be found on: https://docs.oceanprotocol.com/concepts/networks/

We might need to host the API on Azure functions to be able to manage increase the timeouts. The source code for building the Flask App on Azure functions is available on Main branch of the same Alpha repository.

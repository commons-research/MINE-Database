### 

A JSON containing a list.
Each element in the list is a dictionary containing the following keys:
- keys: initial compound SMILES, list of product compound SMILES 
- values: list of reaction SMILES


```json
[
    {
        "initial_compound": 
        {
            "smiles": "CC(=O)O",
            "inchikey": "AAHGHAAGHAHGAHGA"
        },
        "product_compound": [{
            "smiles": "CC(=O)OCC(=O)O",
            "inchikey": "AAHGHAAGHAHGAHGA"
        }, {
            "smiles": "CC(=O)OCC(=O)O",
            "inchikey": "AAHGHAAGHAHGAHGA"
        }],
    },
    {
        "initial_compound": 
        {
            "smiles": "CC(=O)O",
            "inchikey": "AAHGHAAGHAHGAHGA"
        },
        "product_compound": [{
            "smiles": "CC(=O)OCC(=O)O",
            "inchikey": "AAHGHAAGHAHGAHGA"
        }, {
            "smiles": "CC(=O)OCC(=O)O",
            "inchikey": "AAHGHAAGHAHGAHGA"
        }],
    }
]
```


python ./mongo_interact/mongo_npc_fetcher.py



var myABI = [
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_choice",
				"type": "string"
			}
		],
		"name": "addBallot",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "surveys",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "choice",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

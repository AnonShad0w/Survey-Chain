// The object 'Contracts' will be injected here, which contains all data for all contracts, keyed on contract name:
// Contracts['MyContract'] = {
//  abi: [],
//  address: "0x..",
//  endpoint: "http://...."
// }

// Creates an instance of the smart contract, passing it as a property,
// which allows web3.js to interact with it.
function Ballot(Contract) {
  this.web3 = null;
  this.instance = null;
  this.Contract = Contract;
}

// Initializes the `Ballot` object and creates an instance of the web3.js library.
Ballot.prototype.init = function () {
  // We create a new Web3 instance using either the Metamask provider
  // or an independent provider created towards the endpoint configured for the contract.
  this.web3 = new Web3(
    (window.web3 && window.web3.currentProvider) ||
      new Web3.providers.HttpProvider(this.Contract.endpoint)
  );

  // Create the contract interface using the ABI provided in the configuration.
  var contract_interface = this.web3.eth.contract(this.Contract.abi);

  // Create the contract instance for the specific address provided in the configuration.
  this.instance = contract_interface.at(this.Contract.address)
    ? contract_interface.at(this.Contract.address)
    : { choice: () => {} };
};

// Gets the 'choice' value stored on the instance of the contract
Ballot.prototype.getChoice = function (cb) {
  this.instance.choice(function (error, result) {
    cb(error, result);
  });
};

// Update the selected choice on the instance of the contract
// This function is triggered when someone clicks the "Submit" button in the interface
Ballot.prototype.setChoice = function () {
  var that = this;
  var choice = document.querySelector('input[name="choice"]:checked').value;
  this.showLoader(true);

  // Sets choice using the public update function of the smart contract
  this.instance.addBallot(
    choice,
    {
      from: window.web3.eth.accounts[0],
      gas: 100000,
      gasPrice: 100000,
      gasLimit: 100000,
    },
    function (error, txHash) {
      if (error) {
        console.log(error);
        that.showLoader(false);
      }
      // If success, wait for confirmation of transaction,
      // then clear form value
      else {
        that.waitForReceipt(txHash, function (receipt) {
          that.showLoader(false);
          if (receipt.status) {
            console.log({ receipt });
            if (receipt.hasOwnProperty("transactionHash")) {
              $("#txReceipt").text(JSON.stringify(receipt.transactionHash));
            }
            if (receipt.hasOwnProperty("gasUsed")) {
              $("#gasUsed").text(JSON.stringify(receipt.gasUsed));
            }
            document.querySelector('input[name="choice"]:checked').value;
          } else {
            console.log("error");
          }
        });
      }
    }
  );
};

// Waits for receipt from transaction
Ballot.prototype.waitForReceipt = function (hash, cb) {
  var that = this;

  // Checks for transaction receipt using web3.js library method
  this.web3.eth.getTransactionReceipt(hash, function (err, receipt) {
    if (err) {
      error(err);
    }
    if (receipt !== null) {
      // Transaction went through
      if (cb) {
        cb(receipt);
      }
    } else {
      // Try again in 2 seconds
      window.setTimeout(function () {
        that.waitForReceipt(hash, cb);
      }, 2000);
    }
  });
};

// Gets the latest block number by using the web3js 'getTransactionReceipt' function
Ballot.prototype.getTransactionReceipt = function (cb) {
  this.web3.eth.getTransactionReceipt(function (error, receipt) {
    cb(error, receipt);
  });
};

// Gets the latest block number by using the web3js 'getBlockNumber' function
Ballot.prototype.getBlockNumber = function (cb) {
  this.web3.eth.getBlockNumber(function (error, result) {
    cb(error, result);
  });
};

// Hides or displays the loader when performing async operations
Ballot.prototype.showLoader = function (show) {
  document.getElementById("loader").style.display = show ? "block" : "none";
  document.getElementById("submit-button").style.display = show
    ? "none"
    : "block";
};

// Calls the function 'getBlockNumber' defined above,
// then sets the DOM element texts to the values they return or displays
// an error message
Ballot.prototype.updateDisplay = function () {
  var that = this;
  this.getBlockNumber(function (error, result) {
    if (error) {
      $(".error").show();
      return;
    }
    $("#blocknumber").text(result);
    setTimeout(function () {
      that.updateDisplay();
    }, 1000);
  });
};

// Binds buttons to specific functions
Ballot.prototype.bindButtons = function () {
  var that = this;

  $(document).on("click", "#submit-button", function () {
    that.setChoice();
  });
};

// Display the main content.
// Called once a contract has been deployed
Ballot.prototype.updateDisplayContent = function () {
  this.showMainContent();
};

// A contract will not have its address set until it has been deployed
Ballot.prototype.hasContractDeployed = function () {
  return this.instance && this.instance.address;
};

Ballot.prototype.showMainContent = function () {
  $("#blockchain-container").removeClass("hidden");
};

// JavaScript boilerplate to create the instance of the 'Ballot' object
// defined above, and show the HTML elements on the page:
Ballot.prototype.main = function () {
  $(".blocknumber").show();
  $(".txReceipt").show();
  $(".gasUsed").show();
  this.updateDisplay();
};

Ballot.prototype.onReady = function () {
  this.init();
  if (this.hasContractDeployed()) {
    this.updateDisplayContent();
    this.bindButtons();
  }
  this.main();
};

if (typeof Contracts === "undefined") var Contracts = { Ballot: { abi: [] } };
var ballot = new Ballot(Contracts["Ballot"]);

$(document).ready(function () {
  ballot.onReady();
});

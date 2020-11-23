// "wss://ropsten.infura.io/ws/v3/60ccb3c382e44f5b87d4ce6ce0306e57"

function startApp() {
  contractAddress = '0x070f7B6de5e5453FaCD01dA8cFf382BC6ACd4d9b';
  nodeProvider = new Web3.providers.WebsocketProvider('wss://ropsten.infura.io/ws/v3/60ccb3c382e44f5b87d4ce6ce0306e57');
  ballot = new web3js.eth.Contract(myABI, contractAddress);
  console.log(web3js);
}

window.addEventListener('load', function() {

  // Checking if Web3 has been injected by the browser (Mist/MetaMask)
  if (typeof web3 !== 'undefined') {
    // Use Mist/MetaMask's provider
    web3js = new Web3(web3.currentProvider);
  } else {
    // Handle the case where the user doesn't have web3. Probably
    // show them a message telling them to install Metamask in
    // order to use our app.
  }

  // Now you can start your app & access web3js freely:
  startApp();
  console.log('starting app');
})

/*
let balance = document.getElementById('wallet-balance');

document.querySelector("#wallet-addr-btn").addEventListener('click', function(e) {
  if (balance.textContent.length > 6) {
    balance.setAttribute('visibility', 'visible');
  }
}); 
*/


// const algosdk = require('algosdk');
import algosdk from 'algosdk';

const keypress = async () => {
	process.stdin.setRawMode(true);
	return new Promise<void>((resolve) =>
		process.stdin.once('data', () => {
			process.stdin.setRawMode(false);
			resolve();
		})
	);
};

// Create an account and add funds to it. Copy the address off
// The Algorand TestNet Dispenser is located here:
// https://dispenser.testnet.aws.algodev.network/
const createAccount = function () {
	try {
		const myaccount = algosdk.generateAccount();
		console.log('Account Address = ' + myaccount.addr);
		let account_mnemonic = algosdk.secretKeyToMnemonic(myaccount.sk);
		console.log('Account Mnemonic = ' + account_mnemonic);
		console.log('Account created. Save off Mnemonic and address');
		console.log('Add funds to account using the TestNet Dispenser: ');
		console.log('https://dispenser.testnet.aws.algodev.network?account=' + myaccount.addr);

		return myaccount;
	} catch (err) {
		console.log('err', err);
	}
};

/**
 * utility function to wait on a transaction to be confirmed
 * the timeout parameter indicates how many rounds do you wish to check pending transactions for
 */
async function waitForConfirmation(algodclient, txId, timeout) {
	// Wait until the transaction is confirmed or rejected, or until 'timeout'
	// number of rounds have passed.
	//     Args:
	// txId(str): the transaction to wait for
	// timeout(int): maximum number of rounds to wait
	// Returns:
	// pending transaction information, or throws an error if the transaction
	// is not confirmed or rejected in the next timeout rounds
	if (algodclient == null || txId == null || timeout < 0) {
		throw new Error('Bad arguments.');
	}
	const status = await algodclient.status().do();
	if (typeof status === 'undefined') throw new Error('Unable to get node status');
	const startround = status['last-round'] + 1;
	let currentround = startround;

	/* eslint-disable no-await-in-loop */
	while (currentround < startround + timeout) {
		const pendingInfo = await algodclient.pendingTransactionInformation(txId).do();
		if (pendingInfo !== undefined) {
			if (pendingInfo['confirmed-round'] !== null && pendingInfo['confirmed-round'] > 0) {
				// Got the completed Transaction
				return pendingInfo;
			}

			if (pendingInfo['pool-error'] != null && pendingInfo['pool-error'].length > 0) {
				// If there was a pool error, then the transaction has been rejected!
				throw new Error(`Transaction Rejected pool error${pendingInfo['pool-error']}`);
			}
		}
		await algodclient.statusAfterBlock(currentround).do();
		currentround += 1;
	}
	/* eslint-enable no-await-in-loop */
	throw new Error(`Transaction not confirmed after ${timeout} rounds!`);
}

/**
 * Wait for confirmation — timeout after 2 rounds
 */
async function verboseWaitForConfirmation(client, txnId) {
	console.log('Awaiting confirmation (this will take several seconds)...');
	const roundTimeout = 2;
	const completedTx = await waitForConfirmation(client, txnId, roundTimeout);
	console.log('Transaction successful.');
	return completedTx;
}

//
const fs = require('fs');
// import teal file
const approvalTeal = fs.readFileSync('./approval.teal', 'utf8');
// console.log('approvalTeal', approvalTeal);

async function getBasicProgramBytes(client) {
	// const program = '#pragma version 2\nint 1';
	const program = approvalTeal;

	// use algod to compile the program
	const compiledProgram = await client.compile(program).do();
	return new Uint8Array(Buffer.from(compiledProgram.result, 'base64'));
}

// main
async function main() {
	try {
		let myAccount = createAccount();
		console.log('Press any key when the account is funded');
		await keypress();

		// Connect your client
		const algodToken = '2f3203f21e738a1de6110eba6984f9d03e5a95d7a577b34616854064cf2c0e7b';
		const algodServer = 'https://academy-algod.dev.aws.algodev.network/';
		const algodPort = '';
		let algodClient = new algosdk.Algodv2(algodToken, algodServer, algodPort);

		//Check your balance
		let accountInfo = await algodClient.accountInformation(myAccount.addr).do();
		console.log('Account balance: %d microAlgos', accountInfo.amount);
		let startingAmount = accountInfo.amount;
		// Construct the transaction
		let params = await algodClient.getTransactionParams().do();
		// comment out the next two lines to use suggested fee
		params.fee = 1000;
		params.flatFee = true;

		//
		// const SENDER = {
		// 	// mnemonic: process.env.SENDER_MNEMONIC,
		// 	mnemonic: process.env.SENDER_MNEMONIC,
		// };
		// const sender = algosdk.mnemonicToSecretKey(SENDER.mnemonic);

		// ------------------------------
		// > Create application
		// ------------------------------

		// define application parameters
		// const from = sender.addr;
		const from = myAccount.addr;
		const onComplete = algosdk.OnApplicationComplete.NoOpOC;
		const approvalProgram = await getBasicProgramBytes(algodClient);
		const clearProgram = await getBasicProgramBytes(algodClient);
		const numLocalInts = 0;
		const numLocalByteSlices = 0;
		const numGlobalInts = 1;
		const numGlobalByteSlices = 0;
		const appArgs = [];

		// get suggested params
		const suggestedParams = await algodClient.getTransactionParams().do();

		// create the application creation transaction
		const createTxn = algosdk.makeApplicationCreateTxn(
			from,
			suggestedParams,
			onComplete,
			approvalProgram,
			clearProgram,
			numLocalInts,
			numLocalByteSlices,
			numGlobalInts,
			numGlobalByteSlices,
			appArgs
		);

		// send the transaction
		console.log('Sending application creation transaction.');
		// const signedCreateTxn = createTxn.signTxn(sender.sk);
		const signedCreateTxn = createTxn.signTxn(myAccount.sk);
		const { txId: createTxId } = await algodClient.sendRawTransaction(signedCreateTxn).do();
		console.log('sent off tx: ', createTxId);

		// wait for confirmation
		const completedTx = await verboseWaitForConfirmation(algodClient, createTxId);
		// const completedTx = await waitForConfirmation(algodClient, createTxId);
		console.log('completedTx:'); // , completedTx);
	} catch (err) {
		console.log('err', err);
	}
	process.exit();
}

main();

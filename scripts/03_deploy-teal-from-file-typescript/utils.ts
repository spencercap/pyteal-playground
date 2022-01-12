import algosdk from 'algosdk';

export const keypress = async () => {
	process.stdin.setRawMode(true);
	return new Promise<void>((resolve) =>
		process.stdin.once('data', () => {
			process.stdin.setRawMode(false);
			resolve();
		})
	);
};

export const createAlgodClient = (net = 'testnet') => {
	// Connect your client
	let algodToken: string, algodServer: string, algodPort: string;

	if (net == 'testnet') {
		algodToken = '2f3203f21e738a1de6110eba6984f9d03e5a95d7a577b34616854064cf2c0e7b';
		algodServer = 'https://academy-algod.dev.aws.algodev.network/';
		algodPort = '';
	} else if (net == 'betanet') {
		//
	} else if (net == 'mainnet') {
		//
	} else {
		console.error('which net now..?');
		return;
	}

	const algodClient = new algosdk.Algodv2(algodToken, algodServer, algodPort);
	return algodClient;
};

// Create an account and add funds to it. Copy the address off
// The Algorand TestNet Dispenser is located here:
// https://dispenser.testnet.aws.algodev.network/
export const createAccount = function () {
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
export async function waitForConfirmation(algodclient, txId, timeout) {
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
export async function verboseWaitForConfirmation(client, txnId) {
	console.log('Awaiting confirmation (this will take several seconds)...');
	const roundTimeout = 2;
	const completedTx = await waitForConfirmation(client, txnId, roundTimeout);
	console.log('Transaction successful.');
	return completedTx;
}

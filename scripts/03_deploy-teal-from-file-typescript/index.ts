import algosdk from 'algosdk';
import { createAccount, createAlgodClient, keypress, verboseWaitForConfirmation } from './utils';

//
import fs = require('fs');
const approvalTeal = fs.readFileSync('./approval.teal', 'utf8'); // import teal file
async function getBasicProgramBytes(client: algosdk.Algodv2) {
	// const program = '#pragma version 2\nint 1'; // inline
	const program = approvalTeal; // from file

	// use algod to compile the program teal to teal bytecode
	const compiledProgram = await client.compile(program).do();
	return new Uint8Array(Buffer.from(compiledProgram.result, 'base64'));
}

async function main() {
	try {
		const sender = createAccount();
		console.log('Press any key when the account is funded');
		await keypress();

		const algodClient = createAlgodClient();

		//Check your balance
		let accountInfo = await algodClient.accountInformation(sender.addr).do();
		console.log('Account balance: %d microAlgos', accountInfo.amount);
		// Construct the transaction
		let params = await algodClient.getTransactionParams().do();
		// comment out the next two lines to use suggested fee
		params.fee = 1000;
		params.flatFee = true;

		// ------------------------------
		// > Create application
		// ------------------------------

		// define application parameters
		const from = sender.addr;
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
		const signedCreateTxn = createTxn.signTxn(sender.sk);
		const { txId: createTxId } = await algodClient.sendRawTransaction(signedCreateTxn).do();
		console.log('sent off tx: ', createTxId);

		// wait for confirmation
		const completedTx = await verboseWaitForConfirmation(algodClient, createTxId);
		console.log('completedTx'); // , completedTx);
	} catch (err) {
		console.log('err', err);
	}
	process.exit();
}
main();

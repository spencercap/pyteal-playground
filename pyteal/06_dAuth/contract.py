# general
import os
from typing import Optional, Type, List

# pyteal
from pyteal import *
from pytealutils.strings import *
# from pytealutils.inline import *


class AbiMethodClass:
    def __init__(self, signature, method):
        # expects "echo(uint64)string"
        self.selector = MethodSignature(signature)

        # logic
        self.method = method

    def myfunc(self):
        print(self.method)

    def genHandler(self):
        # print('genHandler for', self.selector)
        # selector = Txn.application_args[0]

        # TODO make router + check for NoOp
        # [Txn.on_completion() == OnComplete.NoOp, Cond( appRouter.generateHandler() ) ],

        # define abi handler + route based on method selector
        return [
            Txn.application_args[0] == self.selector,
            self.method
        ]

    def generateJsonDef():
        # reference, one method of: https://github.com/algorand/smart-contracts/blob/master/devrel/ABI/demo-abi/contract.json
        print('TODO')


# abi method class test
abiMethod1 = AbiMethodClass(
    # selector
    "bewmer(uint64)void",
    # logic
    Seq([
        Log( Bytes("bewm") ),
        Approve()
    ])
)

# abiMethod1Handler = abiMethod1.genHandler()
# print("abiMethod1Handler")
# print(abiMethod1Handler)





# These are the 2 methods we want to expose, calling MethodSignature creates the 4 byte method selector as described in arc-0004
echo_selector = MethodSignature("echo(uint64)string")

# @Subroutine(TealType.bytes) #, "echo_sender_label")
# @Subroutine(TealType.none) #, "echo_sender_label") # TODO make subroutine annotation work...
def echo_sender():
    val = Concat(
        Bytes("sender: "),
        itoa(Txn.sender()),
    )

    return Seq([
        Log( val ),
        Approve()
    ])

abiMethod2 = AbiMethodClass(
    "echo_sender(uint64)void", # selector
    echo_sender() # logic
)
abiMethod2Handler = abiMethod2.genHandler()
# print("abiMethod2Handler")
# print(abiMethod2Handler)





# abiMethod3 = AbiMethodClass(
#     'mintAccount(uint64)void', # selector
#     # logic
#     Seq([
#         Log( Bytes('mintAccount - TODO') ),
#         Approve()
#     ])
# )





# ROUTER
class AbiRouter:
    methods: List[AbiMethodClass] = [] # list/arr of methodClasses
    selector = ''

    # def __init__(self, methods[]): # optionally init w some methods
    def __init__(self):
        print('making AbiRouter')

    def generateHandler(self):
        print('return all handlers for use in approval Cond')
        handlers = []
        for m in self.methods:
            h = m.genHandler()
            handlers.append(h)
        return handlers

    def generateJsonAbiSpec(self):
        # reference: https://github.com/algorand/smart-contracts/blob/master/devrel/ABI/demo-abi/contract.json
        # would still need to manually insert app ID for testnet + mainnet after JSON is saved
        # ben@algo's router: https://github.com/algorand-devrel/demo-abi/blob/02765c87958e1a607e45df70d3cae4a0547828cc/contract.py#L166
        print('compile all method specs into single object + save as JSON')

    def add(self, abiClass: Type[AbiMethodClass]):
        self.methods.append(abiClass)

# define all routes (before approval)
appRouter = AbiRouter()
appRouter.add(abiMethod1)
appRouter.add(abiMethod2)
# appRouter.add(abiMethod3)



# APPROVAL
def approval():
    is_app_creator = Return( Txn.sender() == Global.creator_address() )

    return Cond(
        # basics
        [Txn.application_id() == Int(0), Approve()],
        [Txn.on_completion() == OnComplete.DeleteApplication, is_app_creator],
        [Txn.on_completion() == OnComplete.UpdateApplication, is_app_creator],
        [Txn.on_completion() == OnComplete.CloseOut, Approve()],
        [Txn.on_completion() == OnComplete.OptIn, Approve()],

        # manual methods
        [Txn.application_args[0] == Bytes("log_bewm"), Seq([
            Log( Bytes("bewm") ),
            Approve()
        ])],

        # TODO rename to mintAccount
        [Txn.application_args[0] == Bytes('mintAccount'), Seq([
            Log( Bytes('mintAccount started') ),

            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.AssetConfig,

                    TxnField.config_asset_manager: Txn.sender(), # the user
                    TxnField.config_asset_reserve: Txn.sender(), # user
                    TxnField.config_asset_freeze: Global.current_application_address(), # contract generator as creator
                    TxnField.config_asset_clawback: Global.current_application_address(), # contract generator as creator

                    TxnField.config_asset_default_frozen: Int(1), # true

                    # TxnField.config_asset_name: Bytes('space-dapp/user2'),
                    TxnField.config_asset_name: Concat(
                        # appcode
                        Txn.application_args[1],
                        Bytes('/'),
                        # username
                        Txn.application_args[2]
                    ),
                    TxnField.config_asset_unit_name: Bytes('DATH'),
                    TxnField.config_asset_total: Int(1),
                    TxnField.config_asset_decimals: Int(0),
                    # TxnField.config_asset_url: Bytes(''),
                    # TxnField.config_asset_metadata_hash: Bytes(''),

                    TxnField.note: Txn.note(),

                    # Set fee to 0 so caller has to cover it (block irulan debugging however)
                    TxnField.fee: Int(0),
                }
            ),
            InnerTxnBuilder.Submit(),
            # InnerTxn.created_asset_id(),

            Log( Concat(
                Bytes('mintAccount/createdAsset/'),
                itoa( InnerTxn.created_asset_id() )
            ) ),

            # Suffix(
            #     # Get the 'return value' from the logs of the last inner txn
            #     InnerTxn.logs[0],
            #     Int(
            #         6
            #     ),  # TODO: last_log should give us the real last logged message, not in pyteal yet
            # ),  # Trim off return (4 bytes) Trim off string length (2 bytes)



            # InnerTxnBuilder.Begin(),
            # InnerTxnBuilder.SetFields(
            #     {
            #         TxnField.type_enum: TxnType.ApplicationCall,
            #         # access the actual id specified by the 2nd app arg
            #         TxnField.application_id: Txn.applications[ Btoi(Txn.application_args[1]) ],
            #         # Pass the selector as the first arg to trigger the `echo` method
            #         TxnField.application_args: [echo_selector],
            #         # Set fee to 0 so caller has to cover it
            #         TxnField.fee: Int(0),
            #     }
            # ),
            # InnerTxnBuilder.Submit(),
            # Suffix(
            #     # Get the 'return value' from the logs of the last inner txn
            #     InnerTxn.logs[0],
            #     Int(
            #         6
            #     ),  # TODO: last_log should give us the real last logged message, not in pyteal yet
            # ),  # Trim off return (4 bytes) Trim off string length (2 bytes)

            Approve()
        ])],



        # TODO check for NoOp, THEN give router
        # [Txn.on_completion() == OnComplete.NoOp, Cond( appRouter.generateHandler() ) ],

        # abi methods
        # insert all method handlers
        # *appRouter.generateHandler(),
    )

def get_approval():
    return compileTeal(approval(), mode=Mode.Application, version=6)


# CLEAR
def clear():
    return Return(Int(1))
def get_clear():
    return compileTeal(clear(), mode=Mode.Application, version=6)


# MAIN
if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(path, "compiled", "approval.teal"), "w") as f:
        f.write(get_approval())

    with open(os.path.join(path, "compiled", "clear.teal"), "w") as f:
        f.write(get_clear())

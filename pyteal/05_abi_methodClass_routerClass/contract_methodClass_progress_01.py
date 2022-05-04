import os
from pyteal import *
from pytealutils.strings import *
# from pytealutils.inline import *



# ben@algo utils:
# from inspect import *
# # from inspect import signature
# from typing import Callable, List
# def typeString(a):
#     typedict = {
#         TealType.uint64: "uint64",
#         TealType.bytes: "string",
#         # TealType.anytype: "",
#         # TealType.none: "",
#         # TODO add all types: https://github.com/algorandfoundation/ARCs/blob/main/ARCs/arc-0004.md#types
#     }
#     return typedict[a]

# # ben@algo method, feature coming soon: https://github.com/algorand/pyteal/pull/170
# # Utility function to turn a subroutine callable into its selector
# # It produces the method signature `name(type1,type2,...)returnType`
# # which is passed to the `hashy` method to be turned into the method selector
# def get_method_selector(f: Callable) -> str:
#     sig = signature(f)
#     print(sig)
#     args = [typeString(p[1].annotation) for p in sig.parameters.items()]
#     print(args)
#     ret = typeString(f.__closure__[0].cell_contents.returnType)
#     print(ret)
#     method = "{}({}){}".format(f.__name__, ",".join(args), ret)
#     print(method)
#     return MethodSignature(method)
#     # return hashy(method)



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

        return [
            Txn.application_args[0] == self.selector,
            self.method
        ]

    def generateJsonDef():
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

abiMethod1Handler = abiMethod1.genHandler()
# print("abiMethod1Handler")
# print(abiMethod1Handler)





# These are the 2 methods we want to expose, calling MethodSignature creates the 4 byte method selector as described in arc-0004
echo_selector = MethodSignature("echo(uint64)string")

# @Subroutine(TealType.bytes) #, "echo_sender_label")
# @Subroutine(TealType.none) #, "echo_sender_label")
def echo_sender():
    val = Concat(
        Bytes("sender: "),
        itoa(Txn.sender()),
    )

    return Seq([
        Log( val ),
        Approve()
    ])

abiMethodEchoS = AbiMethodClass(
    "echo_sender(uint64)void", # selector
    echo_sender() # logic
)
abiMethodEchoSHandler = abiMethodEchoS.genHandler()
# print("abiMethodEchoSHandler")
# print(abiMethodEchoSHandler)




# ROUTER
class AbiRouter:
    handlers = []
    selector = ''

    def __init__(self, allRoutes):
        print('making AbiRouter')

    def generateHandler(self):
        print('return all handlers for use in approval Cond')
        return self.handlers # TODO map the list so return val is [ handler.genHandler() ]

    def generateJsonAbiSpec(self):
        print('compile all method specs into single object + save as JSON')

    def add(self, abiClass):
        self.handlers.push(abiClass)




# APPROVAL
def approval():
    is_app_creator = Return( Txn.sender() == Global.creator_address() )
    selector = Txn.application_args[0]

    # define abi handlers, route based on method selector
    handlers = [
        # [
        #     # Txn.application_args[0] == echo_selector,
        #     selector == echo_selector,
        #     Return(Seq(ret_log(echo()), Int(1))),
        # ],
        abiMethod1.genHandler(),
        abiMethodEchoS.genHandler(),
    ]

    return Cond(
        # basics
        [Txn.application_id() == Int(0), Approve()],
        [Txn.on_completion() == OnComplete.DeleteApplication, is_app_creator],
        [Txn.on_completion() == OnComplete.UpdateApplication, is_app_creator],
        [Txn.on_completion() == OnComplete.CloseOut, Approve()],
        [Txn.on_completion() == OnComplete.OptIn, Approve()],

        # manual methods
        # [Txn.application_args[0] == Bytes("log_bewm"), Seq([ Log( Bytes("bewm") ), Approve() ])],

        # TODO make router + check for NoOp
        # [Txn.on_completion() == OnComplete.NoOp, router],
        # insert all method handlers
        *handlers,
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

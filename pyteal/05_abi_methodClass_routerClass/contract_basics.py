import os
from pyteal import *
# from pytealutils.inline import InlineAssembly
from pytealutils.strings import itoa


# This may be provided as a constant in pyteal, for now just hardcode
prefix = Bytes("base16", "151f7c75")

# These are the 2 methods we want to expose, calling MethodSignature creates the 4 byte method selector as described in arc-0004
echo_selector = MethodSignature("echo(uint64)string")
# This is called from the other application, just echos some stats
@Subroutine(TealType.bytes)
def echo():
    return Concat(
        Bytes("In app id "),
        itoa(Txn.application_id()),
        Bytes(" which was called by app id "),
        itoa(Global.caller_app_id()),
    )


# Util to add length to string to make it abi compliant, will have better interface in pyteal
@Subroutine(TealType.bytes)
def string_encode(str: Expr):
    return Concat(Extract(Itob(Len(str)), Int(6), Int(2)), str)


# Util to log bytes with return prefix
@Subroutine(TealType.none)
def ret_log(value: Expr):
    return Log(Concat(prefix, string_encode(value)))


# simplest val
# value = Concat(
#     Bytes("bewm")
# )

value = Concat(
    Bytes("sender: "),
    itoa(Txn.sender()),
)

call_log = Seq([
    # Log(Concat(prefix, string_encode(value))),
    Log(Txn.sender()),
    Approve()
])


class AbiHelper:
    def __init__(self, signature, method):
        # expects "echo(uint64)string"
        self.selector = MethodSignature(signature)

        # logic
        self.method = method

    def myfunc(self):
        print(self.method)

    def genHandler(self):
        # print('genHandler', self.selector)
        return [
            Txn.application_args[0] == self.selector,
            self.method
        ]

    def generateJson():
        print('TODO')


# abi method class test
abiMethod1 = AbiHelper(
    # selector
    "bewmer(uint64)void",
    # logic
    Seq([
        Log( Bytes("bewm") ),
        Approve()
    ])
)

x = abiMethod1.genHandler()
print("x")
print(x)


# APPROVAL
def approval():
    is_app_creator = Return( Txn.sender() == Global.creator_address() )
    selector = Txn.application_args[0]

    # define abi handlers, route based on method selector
    handlers = [
        [
            # Txn.application_args[0] == echo_selector,
            selector == echo_selector,
            Return(Seq(ret_log(echo()), Int(1))),
        ],
        abiMethod1.genHandler()
    ]

    return Cond(
        # basics
        [Txn.application_id() == Int(0), Approve()],
        [Txn.on_completion() == OnComplete.DeleteApplication, is_app_creator],
        [Txn.on_completion() == OnComplete.UpdateApplication, is_app_creator],
        [Txn.on_completion() == OnComplete.CloseOut, Approve()],
        [Txn.on_completion() == OnComplete.OptIn, Approve()],

        # manual methods
        [Txn.application_args[0] == Bytes("log"), call_log],
        [Txn.application_args[0] == Bytes("log_bewm"), Seq([ Log( Bytes("bewm") ), Approve() ])],
        [Txn.application_args[0] == Bytes("log_sender"), Seq([ Log( Txn.sender() ), Approve() ])],

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

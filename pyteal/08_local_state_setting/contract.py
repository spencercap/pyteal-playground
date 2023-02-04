from pyteal import *

# APPROVAL
def approval():
    # scratchCount = ScratchVar(TealType.uint64)
    # seller_key = Bytes("seller")

    handle_creation = Seq([
        App.globalPut(Bytes("Count"), Int(0)),
        # App.localPut(Bytes("lvar1"), Int(0)),
        Return(Int(1))
    ])

    handle_optin = Return(Int(1))

    handle_closeout = Return(Int(0))

    handle_updateapp = Return(Int(1))

    handle_deleteapp = Return(Int(0))

    scratchCount = ScratchVar(TealType.uint64)

    add = Seq([
        scratchCount.store(App.globalGet(Bytes("Count"))),
        App.globalPut(Bytes("Count"), scratchCount.load() + Int(1)),
        # App.globalPut(Bytes("Count"), Add(scratchCount.load() + Int(1)) ),
        # App.globalPut(Bytes("streams"), Add(current_streams, Int(1))),
        Return(Int(1))
    ])

    deduct = Seq([
        scratchCount.store(App.globalGet(Bytes("Count"))),
            If(scratchCount.load() > Int(0),
                App.globalPut(Bytes("Count"), scratchCount.load() - Int(1)),
            ),
            Return(Int(1))
    ])

    setLocalInt = Seq([
        # scratchCount.store(App.globalGet(Bytes("Count"))),
        # If(scratchCount.load() > Int(0),
        #     App.globalPut(Bytes("Count"), scratchCount.load() - Int(1)),
        # ),

        App.localPut(Txn.sender(), Bytes("lvar1"), App.globalGet(Bytes("Count"))),
        Return(Int(1))
    ])

    handle_noop = Cond(
        [And(
            Global.group_size() == Int(1),
            Txn.application_args[0] == Bytes("add")
        ), add],
        [And(
            Global.group_size() == Int(1),
            Txn.application_args[0] == Bytes("deduct")
        ), deduct],
        [And(
            Global.group_size() == Int(1),
            Txn.application_args[0] == Bytes("setLocalInt")
        ), setLocalInt],
    )


    program = Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.OptIn, handle_optin],
        [Txn.on_completion() == OnComplete.CloseOut, handle_closeout],
        [Txn.on_completion() == OnComplete.UpdateApplication, handle_updateapp],
        [Txn.on_completion() == OnComplete.DeleteApplication, handle_deleteapp],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop]
    )

    return program

def get_approval():
    return compileTeal(approval(), mode=Mode.Application, version=6)


# CLEAR
def clear():
    return Approve()

def get_clear():
    return compileTeal(clear(), mode=Mode.Application, version=6)


# MAIN
if __name__ == "__main__":
    with open("compiled/approval.teal", "w") as f:
        f.write(get_approval())

    with open("compiled/clear.teal", "w") as f:
        f.write(get_clear())
from os import mkdir, path
from pyteal import *
from pyteal.ast import asset, InnerTxn


def magic():

    on_creation = Seq([
        App.globalPut(Bytes("admin"), Txn.sender()),
        # App.globalPut(Bytes("winners"), Txn.sender()),
        Approve()
    ])

    is_admin = App.globalGet(Bytes("admin")) == Txn.sender()

    opt_in = Seq([
        # App.localPut(
        #     Txn.sender(), Bytes('numero'),
        #     Btoi(Txn.application_args[0])
        # ),
        Approve()
    ])

    # update_numero = Seq([
    #     App.localPut(Txn.sender(), Bytes('numero'),
    #                  Btoi(Txn.application_args[1])),
    #     Approve()
    # ])

    # set_magic_numero = Seq([
    #     Assert(is_admin),
    #     App.globalPut(Bytes('magic_numero'), Txn.application_args[1]),
    #     App.globalPut(Bytes('winner'), Bytes('')),
    #     Approve()
    # ])

    # set_winners = Seq([
    #     Assert(is_admin),
    #     App.globalPut(Bytes('winners'), Bytes(Txn.accounts[1], Txn.accounts[2])),
    #     Approve()
    # ])

    set_winner = Seq([
        Assert(is_admin),
        App.globalPut(Bytes('winner'), Txn.accounts[1]),
        Approve()
    ])

    set_winner_2 = Seq([
        Assert(is_admin),
        App.globalPut(Bytes('winner2'), Txn.accounts[1]),
        Approve()
    ])

    reset_winners = Seq([
        Assert(is_admin),
        # App.globalDel()
        App.globalPut(Bytes('winner'), Bytes('')),
        App.globalPut(Bytes('winner2'), Bytes('')),
        Approve()
    ])



    # this expects caller to be admin and
    # the RECEIVER to be in accounts[1]
    # award_winner = Seq([
    #     Assert(is_admin),
    #     InnerTxnBuilder.Begin(),
    #     InnerTxnBuilder.SetFields({
    #         TxnField.type_enum: TxnType.Payment,
    #         TxnField.sender: Global.current_application_address(),
    #         TxnField.amount: Balance(Global.current_application_address()) - Int(101000),
    #         TxnField.receiver: Txn.accounts[1]
    #     }),
    #     InnerTxnBuilder.Submit(),
    #     App.globalPut(Bytes('winner'), Txn.accounts[1]),
    #     Approve()
    # ])

    # note that all statements in a Cond must call Return() with a value!
    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_admin)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(is_admin)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(is_admin)],
        [Txn.on_completion() == OnComplete.OptIn, opt_in],

        # [Txn.application_args[0] == Bytes("update_numero"), update_numero],
        # [Txn.application_args[0] == Bytes(
        #     "set_magic_numero"), set_magic_numero],
        # [Txn.application_args[0] == Bytes(
        #     "award_winner"), award_winner],
        # [Txn.application_args[0] == Bytes(
        #     "set_winners"), set_winners]
        [Txn.application_args[0] == Bytes("set_winner"), set_winner],
        [Txn.application_args[0] == Bytes("set_winner_2"), set_winner_2],
        [Txn.application_args[0] == Bytes("reset_winners"), reset_winners]
    )

    return program


if __name__ == "__main__":

    with open('./compiled/approval.teal', 'w') as f:
        compiled = compileTeal(
            magic(), mode=Mode.Application, version=5)

        f.write(compiled)

    # print result for Algob
    print(compileTeal(magic(), mode=Mode.Application, version=5))

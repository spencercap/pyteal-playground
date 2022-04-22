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

    set_winner_1 = Seq([
        Assert(is_admin),
        App.globalPut(Bytes('winner1'), Txn.accounts[1]),
        Approve()
    ])

    set_winner_2 = Seq([
        Assert(is_admin),
        App.globalPut(Bytes('winner2'), Txn.accounts[1]),
        Approve()
    ])

    set_winner_3 = Seq([
        Assert(is_admin),
        App.globalPut(Bytes('winner3'), Txn.accounts[1]),
        Approve()
    ])

    # too lazy to figure out winners: Account[] global or proper close out code
    reset_winners = Seq([
        Assert(is_admin),
        App.globalDel(Bytes('winner1')),
        App.globalDel(Bytes('winner2')),
        App.globalDel(Bytes('winner3')),
        Approve()
    ])

    set_amount_per_drop = Seq([
        Assert(is_admin),
        App.globalPut(Bytes('amount_per_drop'), Btoi(Txn.application_args[1])),
        Approve()
    ])

    set_drop_id = Seq([
        Assert(is_admin),
        App.globalPut(Bytes('drop_id'), Btoi(Txn.application_args[1])),
        Approve()
    ])

    # drop = Seq([
    #     Approve()
    # ])

    # note that users must OPT IN to this contract to receive a drop
    # we set a local val to mark them as unable to get more
    drop = Seq([
        Assert(App.localGet(Txn.sender(), Bytes('has_drop')) == Int(0)),
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.xfer_asset: App.globalGet(Bytes("drop_id")),
            TxnField.asset_amount: App.globalGet(Bytes("amount_per_drop")),
            TxnField.asset_receiver: Txn.sender()
        }),
        InnerTxnBuilder.Submit(),
        App.localPut(Txn.sender(), Bytes('has_drop'), Int(1)),
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
        [Txn.application_args[0] == Bytes("set_winner_1"), set_winner_1],
        [Txn.application_args[0] == Bytes("set_winner_2"), set_winner_2],
        [Txn.application_args[0] == Bytes("set_winner_3"), set_winner_3],
        [Txn.application_args[0] == Bytes("reset_winners"), reset_winners],
        #
        [Txn.application_args[0] == Bytes("set_amount_per_drop"), set_amount_per_drop],
        [Txn.application_args[0] == Bytes("set_drop_id"), set_drop_id],
        [Txn.application_args[0] == Bytes("drop"), drop]

        # global byte vars = 6
        # local bye vars = 1
    )

    return program


if __name__ == "__main__":

    with open('./compiled/approval.teal', 'w') as f:
        compiled = compileTeal(
            magic(), mode=Mode.Application, version=5)

        f.write(compiled)

    # print result for Algob
    print(compileTeal(magic(), mode=Mode.Application, version=5))

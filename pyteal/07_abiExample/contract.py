# modified from: https://developer.algorand.org/articles/improved-contract-debugging/
# call abi method: [ "raise(uint64,uint64)uint64", 2, 4 ]

from pyteal import *

print("method sig")
sig = MethodSignature("raise(uint64,uint64)uint64")
# gives:
# 7a6e99005c0213cab84d855cf83192f5e7c9b1a7611477623982f0b2c9966d2f
# 7a6e9900

# print( sig.__str__ )
# meth = Method("raise", [Argument("uint64"), Argument("uint64")], Returns("uint64"))


args = Txn.application_args

on_complete = lambda oc: Txn.on_completion() == oc

isCreate = Txn.application_id() == Int(0)
isOptIn = on_complete(OnComplete.OptIn)
isClear = on_complete(OnComplete.ClearState)
isClose = on_complete(OnComplete.CloseOut)
isUpdate = on_complete(OnComplete.UpdateApplication)
isDelete = on_complete(OnComplete.DeleteApplication)
isNoOp = on_complete(OnComplete.NoOp)

return_prefix = Bytes("base16", "0x151f7c75")  # Literally hash('return')[:4]

@Subroutine(TealType.uint64)
def raise_to_power(x, y):
    i = ScratchVar(TealType.uint64)
    a = ScratchVar(TealType.uint64)
    return Seq(
        a.store(x),
        For(i.store(Int(1)), i.load() <= y, i.store(i.load() + Int(1))).Do(
           a.store(a.load()*x)
        ),
        Log(Concat(return_prefix, Itob(a.load()))),
        a.load(),
    )

@Subroutine(TealType.uint64)
def log_arg0(z):
    # a = Txn.application_args[1]
	w = ScratchVar(TealType.uint64)

	# works:
	# Seq([ Log( Txn.application_args[1] ), Approve() ]

	return Seq(
		w.store(z),
		Log( Concat(return_prefix, Itob( w.load() ) ) ),
		w.load()
	)

    # return Seq(
	# 	Log( z ),
	# 	# Log(Concat(return_prefix, Itob(a.load()))),
	# 	# Approve()
	# 	w.load()
	# )


# @Subroutine(TealType.uint64)
# def log_sender():
# 	w = ScratchVar(TealType.uint64)

# 	return Seq(
# 		# w.store( Btoi(Bytes("test")) ),
# 		Log( Txn.sender() ),
# 		# Log( Txn.sender() ),
# 		w.load()
# 	)

def approval():

    router = Cond(
        [args[0] == MethodSignature("raise(uint64,uint64)uint64"), raise_to_power(Btoi(args[1]), Btoi(args[2])-Int(1))],
		# [args[0] == MethodSignature("logA(uint64)uint64"), log_arg0( Btoi( args[1] ) ) ],
		# [args[0] == MethodSignature("logsender()uint64"), log_sender( ) ],
    )

    return Cond(
        [isCreate, Approve()],
        [isOptIn, Approve()],
        [isClear, Approve()],
        [isClose, Approve()],
        [isUpdate, Approve()],
        [isDelete, Approve()],
        [isNoOp, Return(router)]
    )

def clear():
    return Approve()

def get_approval():
    return compileTeal(approval(), mode=Mode.Application, version=6)


def get_clear():
    return compileTeal(clear(), mode=Mode.Application, version=6)


if __name__ == "__main__":
    with open("compiled/approval.teal", "w") as f:
        f.write(get_approval())

    with open("compiled/clear.teal", "w") as f:
        f.write(get_clear())
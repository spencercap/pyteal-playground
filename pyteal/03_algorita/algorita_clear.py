# Contract Account

# Add directory to path so that algobpy can be imported
# import sys
# sys.path.insert(0,'.')

from os import mkdir, path

#from algobpy.parse import parse_params
from pyteal import *



def clear_state_program():
    is_admin = App.globalGet(Bytes("admin")) == Txn.sender()

    program = Seq([
        Assert(is_admin),
        # App.globalPut(Bytes("admin"), Bytes('')),
        # App.globalPut(Bytes("magic_numero"), Bytes('')),
        # App.globalPut(Bytes("winners"), Bytes('')),
        App.globalPut(Bytes("winner"), Bytes('')),
        App.globalPut(Bytes("winner2"), Bytes('')),

        Return(Int(1))
    ])

    return program


if __name__ == "__main__":

    with open('./compiled/clear.teal', 'w') as f:
        compiled = compileTeal(clear_state_program(),
                               mode=Mode.Application, version=5)
        f.write(compiled)

    print(compileTeal(clear_state_program(), mode=Mode.Application, version=5))

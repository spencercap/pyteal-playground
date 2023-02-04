# a super simple delegated account

from pyteal import *

def delegated_acct_simple(
    # tmpl_fee=tmpl_fee,
    # tmpl_period=tmpl_period,
    # tmpl_dur=tmpl_dur,
    # tmpl_lease=tmpl_lease,
    # tmpl_amt=tmpl_amt,
    # tmpl_rcv=tmpl_rcv,
    # tmpl_timeout=tmpl_timeout,
):
	return Int(1)

if __name__ == "__main__":
	print(compileTeal(delegated_acct_simple(), mode=Mode.Signature, version=6))
    # print(compileTeal(delegated_acct_simple(), mode=Mode.Signature, version=2))
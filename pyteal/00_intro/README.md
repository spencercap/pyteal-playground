# how to

## getting into GOAL env

1. `cd github/sandbox`
2. `./sandbox up` or `./sandbox up testnet`
3. `./sandbox enter algod`
    - exit: `exit`
4. then you can run goal cmds without "`./sandbox` prefix"
5. keeping docker files in `root@cac57194db0b:/opt/testnetwork/Node/ncc/contracts`
    - outside of env, use `docker cp . cac57194db0b:/opt/testnetwork/Node/ncc/contracts/01` to copy files in/out of docker env

---

## deploy

format:
`goal app create --creator <OWNER> --global-byteslices 1 --global-ints 1 --local-byteslices 0 --local-ints 0 --approval-prog approval_program.teal --clear-prog clear_program.teal`

example:
`goal app create --creator 7ZTZIA7WUNAXS4I5WJXRBMZORVMDKSA4EDIF6KQWE234U63NWFP2YQSXTE --global-byteslices 1 --global-ints 1 --local-byteslices 0 --local-ints 0 --approval-prog contract_approval.teal --clear-prog contract_clear_state.teal`

---

## make an account

`goal account new`

## FYI

-   testnet accounts: [name / pass / addr]
    -   `spaceman-01` / `123` / `7ZTZIA7WUNAXS4I5WJXRBMZORVMDKSA4EDIF6KQWE234U63NWFP2YQSXTE`
-   faucet: https://dispenser.testnet.aws.algodev.network/?account=GVXPJYH7APIDJZT4TO7VDSMNRILOBOW3MYJEJPNTOZLACD7ZJZIDBQOUBY

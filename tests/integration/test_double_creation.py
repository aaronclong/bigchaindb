import time
import pytest
import rethinkdb as r
from bigchaindb import exceptions


@pytest.fixture
def inputs(b, user_vk):
    # 1. create transactions for `USER` to spend
    for i in range(40):
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        tx_signed = b.sign_transaction(tx, b.me_private)
        b.write_transaction(tx_signed)
    time.sleep(2)


@pytest.mark.usefixtures('processes')
def test_fast_double_create(b, user_vk):
    tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
    tx = b.sign_transaction(tx, b.me_private)

    # write everything fast
    b.write_transaction(tx)
    b.write_transaction(tx)

    time.sleep(2)
    tx_returned = b.get_transaction(tx['id'])

    # test that the tx can be queried
    assert tx_returned == tx
    # test the transaction appears only once
    assert len(list(r.table('bigchain')
                    .get_all(tx['id'], index='transaction_id')
                    .run(b.conn))) == 1


@pytest.mark.usefixtures('processes')
def test_double_create(b, user_vk):
    tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
    tx = b.sign_transaction(tx, b.me_private)

    b.write_transaction(tx)
    time.sleep(2)
    b.write_transaction(tx)
    time.sleep(2)
    tx_returned = b.get_transaction(tx['id'])

    # test that the tx can be queried
    assert tx_returned == tx
    # test the transaction appears only once
    assert len(list(r.table('bigchain')
                    .get_all(tx['id'], index='transaction_id')
                    .run(b.conn))) == 1


@pytest.mark.usefixtures('processes', 'inputs')
def test_get_owned_ids_works_after_double_spend(b, user_vk, user_sk):
    """See issue 633."""
    input_valid = b.get_owned_ids(user_vk).pop()
    tx_valid = b.create_transaction(user_vk, user_vk, input_valid, 'TRANSFER')
    tx_valid_signed = b.sign_transaction(tx_valid, user_sk)
    b.write_transaction(tx_valid_signed)

    time.sleep(2)

    # create another transaction with the same input
    tx_double_spend = b.create_transaction(user_vk, user_vk,
                                           input_valid, 'TRANSFER')
    tx_double_spend_signed = b.sign_transaction(tx_double_spend, user_sk)
    with pytest.raises(exceptions.DoubleSpend) as excinfo:
        b.validate_transaction(tx_double_spend_signed)

    assert excinfo.value.args[0] == 'input `{}` was already spent' \
        .format(input_valid)
    assert b.is_valid_transaction(tx_double_spend) is False

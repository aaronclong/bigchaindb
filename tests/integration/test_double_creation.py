import time
import pytest
import rethinkdb as r


@pytest.fixture
def inputs(b, user_vk):
    # 1. create blocks with transactions for `USER` to spend
    prev_block_id = b.get_last_voted_block()['id']
    for block in range(4):
        transactions = []
        for i in range(10):
            tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
            tx_signed = b.sign_transaction(tx, b.me_private)
            transactions.append(tx_signed)

        block = b.create_block(transactions)
        b.write_block(block, durability='hard')

        # 2. vote the blocks valid, so that the inputs are valid
        vote = b.vote(block['id'], prev_block_id, True)
        prev_block_id = block['id']
        b.write_vote(vote)


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

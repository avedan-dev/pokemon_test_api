import factory
import pytest


def utbb():
    def unfilled_transaction_bakery_batch(n):
        utbb = factory.make(
            'transaction.Transaction',
            amount_in_cents=1032000, # --> Passes min. payload restriction in every currency
            _fill_optional=[
                'name',
                'email',
                'currency',
                'message'
            ],
            _quantity=n
        )
        return utbb
    return unfilled_transaction_bakery_batch

@pytest.fixture
def ftbb():
    def filled_transaction_bakery_batch(n):
        utbb = factory.make(
            'transaction.Transaction',
            amount_in_cents=1032000, # --> Passes min. payload restriction in every currency
            _quantity=n
        )
        return utbb
    return filled_transaction_bakery_batch

@pytest.fixture
def ftb():
    def filled_transaction_bakery():
        utbb = factory.make(
            'transaction.Transaction',
            amount_in_cents=1032000, # --> Passes min. payload restriction in every currency
            currency=factory.make('transaction.Currency')
        )
        return utbb
    return filled_transaction_bakery
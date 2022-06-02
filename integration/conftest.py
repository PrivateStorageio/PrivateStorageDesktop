# in conftest.py
def pytest_addoption(parser):
    parser.addoption(
        "--grid-flavour", dest="grid-flavour", help="local, production or staging",
        choices=("local", "production", "staging"),
        default="local",
    )
    parser.addoption(
        "--payment-server-exe", dest="payment-server-exe", help="path to PaymentServer-exe",
    )
    parser.addoption(
        "--pay-for-voucher-exe", dest="pay-for-voucher-exe", help="path to PaymentServer-pay-for-voucher",
    )
    parser.addoption(
        "--tahoe-exe", dest="tahoe-exe", help="path to tahoe",
    )

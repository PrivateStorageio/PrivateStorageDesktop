from shutil import which

def pytest_addoption(parser):
    payment_server_exe = which("PaymentServer-exe")
    pay_for_voucher_exe = which("PaymentServer-pay-for-voucher")
    tahoe_exe = which("tahoe")

    parser.addoption(
        "--grid-flavour", dest="grid-flavour", help="local, production or staging",
        choices=("local", "production", "staging"),
        default="local",
    )
    parser.addoption(
        "--payment-server-exe",
        dest="payment-server-exe",
        help=f"path to PaymentServer-exe (default {payment_server_exe})",
        default=payment_server_exe,
        required=payment_server_exe == None,
    )
    parser.addoption(
        "--pay-for-voucher-exe",
        dest="pay-for-voucher-exe",
        help=f"path to PaymentServer-pay-for-voucher (default {pay_for_voucher_exe})",
        default=pay_for_voucher_exe,
        required=pay_for_voucher_exe == None,
    )
    parser.addoption(
        "--tahoe-client-exe",
        dest="tahoe-client-exe",
        help=f"path to tahoe for both client nodes (default {tahoe_exe})",
        default=tahoe_exe,
        required=tahoe_exe == None,
    )
    parser.addoption(
        "--tahoe-server-exe",
        dest="tahoe-server-exe",
        help=f"path to tahoe for server nodes (default {tahoe_exe})",
        default=tahoe_exe,
        required=tahoe_exe == None,
    )

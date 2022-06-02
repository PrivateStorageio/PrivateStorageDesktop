# * What info do you want?
#   * All stdout, stderr of all processes running
#   * The


# ```sh
# # run the whole suite but use this tahoe executable for all tahoe client nodes
# $ pytest integration --client-tahoe-exe tahoe-venv/bin/tahoe

# #
# $ pytest integration --server-tahoe-exe tahoe-venv/bin/tahoe --old-tahoe ...1.17.1/tahoe
# $ pytest integration \
#     --server-tahoe-exe server-venv/bin/tahoe \
#     --client-tahoe-exe client-venv/bin/tahoe
# $ build-gridsync-pyinstaller
# $ pytest integration \
#     --client-tahoe-exe dist/GridSync/tahoe/bin/tahoe \

# ```


# def tahoe_exe():
#     flavour = pytest_get_cli_arg("flavour")
#     match flavour on:
#       case "bundle":
#           return gridsync_api.tahoe_bundle_path()
#       case "ambient":
#           return "tahoe"
#       case ...: ...

# def old_tahoe_exe():
#     #
#     return tahoe_exe()

# def tahoe_exe_1_18_0():
#     download_1_18_0()
#     return path_to_that

# def tahoe_exe_1_17_1():
#     download_1_17_1()
#     return path_to_that

import pytest_twisted
import gridsync.cli as gridsync_api
from gridsync.supervisor import Supervisor
from pytest import fixture
from attrs import define, Factory
from pathlib import Path

@fixture(scope="session")
def payment_server_exe(request):
    return request.config.getoption("payment-server-exe")

@fixture(scope="session")
def pay_for_voucher_exe(request):
    return request.config.getoption("pay-for-voucher-exe")

@fixture(scope="session")
def tahoe_exe(request):
    return request.config.getoption("tahoe-exe")

@fixture(scope="session")
def signing_key():
    # You can get a string like this from PaymentServer's PaymentServer-generate-key
    return "NAQBkEEUKPDtq8af5anlHvWMjeSVoH56RnpCTy70QwA="


@define
class PaymentServer:
    exe: Path
    pay_for_voucher_path: Path
    db_path: Path
    signing_key_path: Path
    supervisor: Supervisor = Factory(Supervisor)

    async def start(self):
        await self.supervisor.start([
            self.exe,
            "--issuer", "ristretto",
            "--signing-key-path", self.signing_key_path,
            "--database", "sqlite3",
            "--database-path", self.db_path,
            "--stripe-key-path", "/dev/null",
        ])

    def pay_for_voucher(self, voucher):
        check_call([pay_for_voucher_path, self.db_path, voucher, "made-up-charge-id"])

@fixture(scope="session")
def payment_server_root(tmp_path_factory):
    return tmp_path_factory.mktemp("paymentserver")

@fixture(scope="session")
def payment_server_database_path(payment_server_root):
    return payment_server_root / "paymentserver.sqlite3"

@fixture(scope="session")
def payment_server(payment_server_database_path, pay_for_voucher_exe, payment_server_exe, signing_key, cheat_code, payment_server_root): # -> IPaymentServer:
    # run payment_server_exe and return abstraction around it
    if cheat_code == "local":
        signing_key_path = payment_server_root / "signing-key.ristretto"
        with open(signing_key_path, "wt") as f:
            f.write(signing_key)
        return PaymentServer(payment_server_exe, pay_for_voucher_exe, payment_server_database_path, signing_key_path)
    else:
        raise NotImplementedError("Do something with Selenium maybe")

@fixture(scope="session")
def cheat_code(request):
    return request.config.getoption("grid-flavour")



def create_settings_from_local_grid(storage_server, payment_server):
    return {
        "version": 2,
        "nickname": "local",
        "newscap": None,
        "zkap_unit_name": "GB-month",
        "zkap_unit_multiplier": 0.001,
        "zkap_payment_url_root": "https://localhost/you-are-not-running-a-payment-website",
        "shares-needed": "1",
        "shares-happy": "1",
        "shares-total": "1",
        "storage": {
            storage_server.node_id: {
                "anonymous-storage-FURL": "pb://@tcp:/",
                "nickname": "storage001",
                "storage-options": [{
                    "name": storage_server.plugin_name,
                    "ristretto-issuer-root-url": payment_server.api_root,
                    "storage-server-FURL": storage_server.storage_furl,
                    "pass-value": 1000000,
                    "default-token-count": 50000,
                    "lease.crawl-interval.mean": 3600,
                    "lease.crawl-interval.range": 60,
                    "lease.min-time-remaining": 2592000,
                    "allowed-public-keys": payment_server.ristretto_public_key,
                }],
            }
        }
    }

@fixture(scope="session")
# @pytest.parmetrize(cheat_code=["0-staging-grid", "0-production-grid", "local"])
def grid_configuration(cheat_code, payment_server):
    if cheat_code == "local":
        # Spin up a grid, including payment server, and return config
        # describing it
        return create_settings_from_local_grid(some_storage_servers, payment_server)
    else:
        return load_settings_from_cheatcode(cheat_code)

@fixture(scope="session")  #(scope="module")
def tahoe_client(grid_configuration, tahoe_exe, tmp_path):
    return pytest_twisted.blockon(
        Deferred.fromCoroutine(
            gridsync_api.provision_tahoe(
                grid_configuration,
                tahoe_exe,
                tmp_path,
            ),
        ),
    )

@fixture(scope="function")
def provision_tahoe_client(grid_configuration, tahoe_exe):
    def provision(nodedir):
        return gridsync_api.provision_tahoe(
            grid_configuration,
            tahoe_exe,
            nodedir,
        )
    return provision


async def test_recovery_cleartext(
    tahoe_client,
    provision_tahoe_client,
    grid_configuration,
    payment_server,
    tmp_path_factory,
):
    voucher = await gridsync_api.add_voucher(tahoe_client)
    await payment_server.pay_for_voucher(voucher)
    await gridsync_api.wait_for_redemption(voucher)

    filename = mktemp()
    await gridsync_api.create_recovery_key(
        tahoe_client.nodedir,
        filename,
        passphrase=None,
    )
    application_data = b"Hello, world!" * 20
    appdata_cap = await tahoe_client.upload(application_data)

    target_tahoe_client = provision_tahoe_client(
        tmp_path_factory.mktemp("target-tahoe"),
    )
    gridsync_api.restore_from_recovery_key(
        target_tahoe_client,
        filename,
        passphrase=None,
    )
    assert (await target_tahoe_client.download(appdata_cap)) == application_data
    newcap = await target_tahoe_client.upload(b"some other application data that is long enough" * 5)
    assert newcap_is_really_a_thing

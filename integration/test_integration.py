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

from pytest_twisted import blockon, ensureDeferred
import gridsync.cli as gridsync_api
from pytest import fixture
from twisted.internet.defer import Deferred
from .lib import IPaymentServer, PaymentServer, provision_tahoe_storage, LocalGrid, RemoteGrid, provision_running_payment_server

def blockOnCoroutine(coro):
    return blockon(Deferred.fromCoroutine(coro))

@fixture(scope="session")
def payment_server_exe(request):
    return request.config.getoption("payment-server-exe")

@fixture(scope="session")
def pay_for_voucher_exe(request):
    return request.config.getoption("pay-for-voucher-exe")

@fixture(scope="session")
def tahoe_client_exe(request):
    return request.config.getoption("tahoe-client-exe")

@fixture(scope="session")
def tahoe_server_exe(request):
    return request.config.getoption("tahoe-server-exe")

@fixture(scope="session")
def signing_key():
    # You can get a string like this from PaymentServer's PaymentServer-generate-key
    return "NAQBkEEUKPDtq8af5anlHvWMjeSVoH56RnpCTy70QwA="

@fixture(scope="session")
def client_root(tmp_path_factory):
    return tmp_path_factory.mktemp("client")

@fixture(scope="session")
def grid_root(tmp_path_factory):
    return tmp_path_factory.mktemp("grid")

@fixture(scope="session")
def payment_server_root(grid_root):
    root = grid_root / "grid"
    root.mkdir()
    return root

@fixture(scope="session")
def payment_server(pay_for_voucher_exe, payment_server_exe, signing_key, cheat_code, payment_server_root) -> IPaymentServer:
    # run payment_server_exe and return abstraction around it
    if cheat_code == "local":
        return blockOnCoroutine(provision_running_payment_server(
            payment_server_root, signing_key, payment_server_exe, pay_for_voucher_exe,
        ))
    else:
        raise NotImplementedError("Do something with Selenium maybe")

@fixture(scope="session")
def cheat_code(request):
    return request.config.getoption("grid-flavour")

@fixture(scope="session")
def grid(cheat_code, tahoe_server_exe, payment_server, grid_root):
    if cheat_code == "local":
        storage = blockOnCoroutine(provision_tahoe_storage(
            grid_root / "storage",
            tahoe_server_exe,
        ))
        return LocalGrid(storage, payment_server)
    else:
        return RemoteGrid.from_cheat_code(cheat_code)

@fixture(scope="session")  #(scope="module")
def tahoe_client(grid, tahoe_client_exe, client_root):
    # XXX If provision_tahoe runs the wrong tahoe command and tahoe exits with
    # an error status, provision_tahoe raises an exception, gives a gross
    # stack trace going through many layers of Twisted and pytest, and then
    # dumps a *truncated* argv and the tahoe process output into the pytest
    # failure report.  Report such failures better.  For example, it would be
    # cool if we could extract a complete list of commands executed so far.
    # This might reveal simple errors all by itself or, by letting a developer
    # run those commands directly, might make it easier to reproduce the
    # problem in an easily-inspected environment (or share those commands with
    # another developer in another environment, compare them to what's run on
    # CI, etc)

    async def provision_running_client():
        tahoe = await gridsync_api.provision_tahoe(
            grid.settings,
            tahoe_client_exe,
            client_root / "tahoe-client",
        )

        # XXX This *very* easily leaks the started processes if something goes
        # wrong (and maybe even if it doesn't!).
        await gridsync_api.run_tahoe(tahoe)
        return tahoe

    return blockOnCoroutine(provision_running_client())

@fixture(scope="function")
def provision_tahoe_client(grid, tahoe_client_exe):
    def provision(nodedir):
        return gridsync_api.provision_tahoe(
            grid.settings,
            tahoe_client_exe,
            nodedir,
        )
    return provision

# XXX There's no easy way to see how the test is progressing through its many
# time-consuming steps.
@ensureDeferred
async def test_recovery_cleartext(
    tahoe_client,
    provision_tahoe_client,
    payment_server,
    tmp_path_factory,
):
    print("Adding voucher")
    voucher = await gridsync_api.add_voucher(tahoe_client)
    print("Paying for voucher")
    await payment_server.pay_for_voucher(voucher)
    print("Waiting for redemption")
    await gridsync_api.wait_for_redemption(tahoe_client, voucher)

    print("Creating recovery key")
    filename = tmp_path_factory.mktemp("recovery-key")
    await gridsync_api.create_recovery_key(
        tahoe_client.nodedir,
        filename,
        passphrase=None,
    )
    print("Uploading data")
    application_data = b"Hello, world!" * 20
    appdata_cap = await tahoe_client.upload(application_data)

    print("Provisioning tahoe client")
    target_tahoe_client = await provision_tahoe_client(
        tmp_path_factory.mktemp("target-tahoe"),
    )

    gridsync_api.restore_from_recovery_key(
        target_tahoe_client,
        filename,
        passphrase=None,
    )
    assert (await target_tahoe_client.download(appdata_cap)) == application_data
    newcap = await target_tahoe_client.upload(b"some other application data that is long enough" * 5)
    assert isinstance(newcap, str)

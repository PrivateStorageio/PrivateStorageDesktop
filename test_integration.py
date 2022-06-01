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


def tahoe_exe():
    flavour = pytest_get_cli_arg("flavour")
    match flavour on:
      case "bundle":
          return gridsync_api.tahoe_bundle_path()
      case "ambient":
          return "tahoe"
      case ...: ...

def old_tahoe_exe():
    #
     return tahoe_exe()

def tahoe_exe_1_18_0():
    download_1_18_0()
    return path_to_that

def tahoe_exe_1_17_1():
    download_1_17_1()
    return path_to_that


def staging_grid():
    return staging_grid_config


def get_payment_server(payment_server_exe, signing_key):
    def payment_server():
        # run payment_server_exe and return abstraction around it
        return PaymentServer(...)
    return payment_server

@pytest.fixture
@pytest.parmetrize(cheat_code=["0-staging-grid", "0-production-grid", "local"])
def grid_configuration(cheat_code, get_payment_server):
    if cheat_code == "local":
        # Spin up a grid, including payment server, and return config
        # describing it
        payment_server = get_payment_server()
        return create_settings_from_local_grid(some_storage_servers, payment_server)
    else:
        return load_settings_from_cheatcode(cheat_code)

def create_tahoe_client(grid_configuration):
    nodedir = Path(mktemp())
    tahoe = gridsync_api.get_tahoe_client(nodedir, tahoe_exe)
    pytest_twisted_blockon(tahoe.create_node(**grid_configuration))
    return tahoe


def tahoe_storage_a(...):
   # like tahoe_client_a
   return ...





async def create_tahoe_client(gridsync):
    gridsync_api.provision_tahoe()




tahoe_exe_versions = [tahoe_exe_1_17_1, tahoe_exe_1_18_0]

@pytest.fixture
@pytest.parmetrize(
    client_versions=tahoe_exe_versions,
    server_versions=tahoe_exe_versions,
)
def matrix_gridsync(tahoe_exe, magic_folder_exe, grid):
     return Gridsync(tahoe_exe, magic_folder_exe, grid)

@pytest.fixture(scope="session")
def tahoe_client(...):
     t = pytest_twisted.blockon(create_tahoe_client(...))
     return t

@pytest.fixture
#@pytest.parmetrize(servers=[1, 5])
#def grid(num_servers):
def grid():
    num_servers = pytest_get_cli_arg("num-servers")
    flavour = ["local", "staging", "production"]
    if flavour == "local":
        return create_grid(num_servers)
    elif flavour == "staging":
	return staging_grid()


async def test_recovery_cleartext(gridsync_api, tahoe_exe, grid_configuration):
    tahoe = create_tahoe_client(grid_configuration)

    # XXX or maybe this is pest.pay_for_voucher?
    await gridsync_api.pay_for_voucher(tahoe)
    # XXX wait for redemption to complete and gridsync to create the rootcap

    filename = mktemp()
    await gridsync_api.create_recovery_key(filename, passphrase=None)
    application_data = b"Hello, world!" * 20
    appdata_cap = await tahoe.upload(application_data)

    # XXX wipe all the tahoe state

    gridsync_api.restore_from_recovery_key(filename, passphrase=None)
    tahoe = gridsync_api.get_tahoe_client()
    assert (await tahoe.download(appdata_cap)) == application_data

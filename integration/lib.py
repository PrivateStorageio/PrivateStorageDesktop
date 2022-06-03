from gridsync.supervisor import Supervisor
from hyperlink import DecodedURL
from pathlib import Path
from attrs import define, Factory
from gridsync.zkapauthorizer import PLUGIN_NAME as ZKAPAUTHZ_PLUGIN_NAME
from gridsync.tahoe import Tahoe
from gridsync import load_settings_from_cheatcode
from twisted.internet.utils import getProcessOutputAndValue
from challenge_bypass_ristretto import SigningKey, PublicKey

class IPaymentServer:
    api_root: DecodedURL
    ristretto_public_key: str

@define
class PaymentServer:
    exe: Path
    pay_for_voucher_path: Path
    db_path: Path
    signing_key_path: Path
    api_root: DecodedURL = DecodedURL.from_text("http://localhost:44441")
    supervisor: Supervisor = Factory(Supervisor)

    @property
    def ristretto_public_key(self):
        return PublicKey.from_signing_key(
            SigningKey.decode_base64(self.signing_key_path.read_bytes()),
        ).encode_base64().decode("ascii")

    async def start(self):
        print(f"Starting {self.exe}")
        # XXX If PaymentServer exits with an error we never notice and
        # anything that depends on PaymentServer probably hangs indefinitely
        # waiting for it to show up.
        await self.supervisor.start([
            str(self.exe),
            "--issuer", "Ristretto",
            "--signing-key-path", str(self.signing_key_path),
            "--database", "SQLite3",
            "--database-path", str(self.db_path),
            "--stripe-key-path", "/dev/null",
            "--http-port", str(self.api_root.port),
        ])
        print(f"Started {self.exe}")

    async def pay_for_voucher(self, voucher):
        (out, err, code) = await getProcessOutputAndValue(
            str(self.pay_for_voucher_path),
            [str(self.db_path), voucher, "made-up-charge-id"],
        )
        if code != 0:
            raise Exception(code, out + err)



async def provision_running_payment_server(root, signing_key, exe, pay_for_voucher):
    signing_key_path = root / "signing-key.ristretto"
    database_path = root / "paymentserver.sqlite3"

    with open(signing_key_path, "wt") as f:
        f.write(signing_key)

    payment = PaymentServer(
        exe,
        pay_for_voucher,
        database_path,
        signing_key_path,
    )
    await payment.start()
    return payment

@define
class LocalGrid:
    _storage: Tahoe
    _payment: IPaymentServer

    @property
    def settings(self):
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
                self._storage.long_nodeid: {
                    "anonymous-storage-FURL": "pb://@tcp:/",
                    "nickname": self._storage.name,
                    "storage-options": [{
                        "name": ZKAPAUTHZ_PLUGIN_NAME,
                        "ristretto-issuer-root-url": self._payment.api_root.to_text(),
                        "storage-server-FURL": self._storage.storage_furl,
                        "pass-value": 1000000,
                        "default-token-count": 50000,
                        "lease.crawl-interval.mean": 3600,
                        "lease.crawl-interval.range": 60,
                        "lease.min-time-remaining": 2592000,
                        "allowed-public-keys": self._payment.ristretto_public_key,
                    }],
                }
            }
        }


@define
class RemoteGrid:
    settings: dict

    @classmethod
    def from_cheat_code(cls, cheat_code):
        return cls(load_settings_from_cheatcode(cheat_code))


async def provision_tahoe_storage(nodedir, tahoe_exe):
    # XXX This very easily leaks the long-running tahoe process.
    tahoe = Tahoe(nodedir, tahoe_exe)
    await tahoe.create_node(
        nickname="storage001",
        location="tcp:localhost:44440",
        port="tcp:44440",
    )
    await tahoe.start()
    return tahoe

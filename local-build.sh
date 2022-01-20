export NIV_OVERRIDE_gridsync=/home/exarkun/Work/python/gridsync
export NIV_OVERRIDE_tahoe_lafs=/home/exarkun/Work/python/tahoe-lafs
export NIV_OVERRIDE_magic_folder=/home/exarkun/Work/python/magic-folder
export NIV_OVERRIDE_zkapauthorizer=/home/exarkun/Work/PrivateStorage/ZKAPAuthorizer

nix-build -A desktopclient

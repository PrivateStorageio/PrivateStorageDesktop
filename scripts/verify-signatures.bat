set PATH=%PATH%;C:\Program Files (x86)\Windows Kits\10\bin\x64;C:\Program Files (x86)\Windows Kits\10\bin\10.0.17763\x64
signtool verify /v .\dist\PrivateStorage\Tahoe-LAFS\tahoe.exe
signtool verify /v .\dist\PrivateStorage\PrivateStorage.exe
signtool verify /v .\dist\PrivateStorage\PrivateStorage-setup.exe

set PATH=%PATH%;C:\Program Files (x86)\Windows Kits\10\bin\x64;C:\Program Files (x86)\Windows Kits\10\bin\10.0.17763\x64
signtool sign /n "PrivateStorage.io, LLC" /sha1 CC63B794E96D9CAE28585D700173A0812812ED96 /tr http://timestamp.digicert.com /td sha256 /fd sha256 /a .\dist\PrivateStorage-setup.exe
copy .\dist\PrivateStorage-setup.exe .\dist\PrivateStorage-setup-signed.exe
::start signtool sign /n "PrivateStorage.io, LLC" /sha1 CC63B794E96D9CAE28585D700173A0812812ED96 /tr http://timestamp.digicert.com /td sha256 /fd sha256 /a .\dist\PrivateStorage-setup.exe && exit /b 0
::ping 127.0.0.1 -n 181>nul
::taskkill /im signtool.exe /f
::echo WARNING: Not signed

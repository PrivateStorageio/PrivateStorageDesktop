@echo off

if "%1"=="clean" call :clean
if "%1"=="source" call :source
if "%1"=="" call :source
goto :eof

:clean
call rmdir /s /q .\privatestorage
goto :eof

:source
call git clone --depth 1 -b 290.new-magic-folder https://github.com/gridsync/gridsync .\privatestorage
call copy .\assets\PrivateStorage* .\privatestorage\images\
call copy .\assets\PrivateStorage* .\privatestorage\gridsync\resources\
call copy .\assets\PrivateStorage.png .\privatestorage\gridsync\resources\tahoe-lafs.png
call copy .\privatestorage\gridsync\resources\laptop.png .\privatestorage\gridsync\resources\laptop-with-icon.png
call copy .\credentials\*.json .\privatestorage\gridsync\resources\providers\
call copy .\build\config.txt .\privatestorage\gridsync\resources\
call copy .\scripts\* .\privatestorage\
goto :eof

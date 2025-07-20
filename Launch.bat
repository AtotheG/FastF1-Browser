@echo off
REM Build and start containers detached
docker compose up -d --build

for /L %%i in (3,-1,1) do (
    echo Opening browser in %%i...
    timeout /t 1 > NUL
)
start http://localhost:5173

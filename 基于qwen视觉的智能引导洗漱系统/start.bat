@echo off
echo 启动智能洗漱台系统...
echo.

REM 检查Python环境
if not exist "D:\Do\Codes\PythonProject\PythonENV\Tool\python.exe" (
    echo 错误：找不到Python环境
    echo 请确保Python环境路径正确
    pause
    exit /b 1
)

REM 启动程序
"D:\Do\Codes\PythonProject\PythonENV\Tool\python.exe" main.py

REM 如果程序异常退出，显示错误信息
if %ERRORLEVEL% neq 0 (
    echo.
    echo 程序异常退出，错误代码：%ERRORLEVEL%
    echo 请检查配置文件和依赖包是否正确安装
    pause
)
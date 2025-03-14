import subprocess
import os
import time
import requests

# 公告信息
ANNOUNCEMENT = """
\033[91m=== 刷机工具公告 ===

1. 驱动下载（确保设备连接正常）：
   https://www.123912.com/s/S96sjv-umCD

2. 作者主网盘链接（获取更多工具和资源）：
   https://www.123912.com/s/S96sjv-pesD

3. 注意事项：
   - **数据备份**：
     解锁Bootloader会清除设备上的所有数据，请务必提前备份重要数据。
   - **OEM解锁选项**：
     在解锁Bootloader之前，请确保已在设备的开发者选项中启用“OEM解锁”选项。
   - **设备支持**：
     该功能仅适用于支持 `fastboot oem unlock` 命令的设备（如一加手机）。其他品牌设备可能需要不同的命令。

4. 反馈联系：
   - 酷安: @抠脚大汉小哲

5. 当前版本：
   - V2.0.0

请确保设备已正确连接，并仔细阅读公告内容后再进行操作。
\033[0m
"""

# 当前版本号
CURRENT_VERSION = "V2.0.0"

# 作者信息
AUTHOR = "@酷安抠脚大汉小哲"

# 日志文件路径
LOG_FILE = "flash_tool.log"

# 记录日志
def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    print(message)

# 执行命令并返回输出
def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        log(f"命令执行成功: {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        log(f"命令执行失败: {command}")
        log(f"错误信息: {e.stderr}")
        return None

# 检查设备是否连接
def check_device():
    log("检查设备连接...")
    output = run_command("adb devices")
    if output and "device" in output:
        log("设备已通过ADB连接。")
        return "adb"
    else:
        output = run_command("fastboot devices")
        if output and "fastboot" in output:
            log("设备已通过Fastboot连接。")
            return "fastboot"
        else:
            # 检查是否进入9008模式
            output = run_command("lsusb")  # Linux
            if "Qualcomm HS-USB QDLoader 9008" in output:
                log("设备已进入9008模式。")
                return "9008"
            else:
                log("未检测到设备。")
                return None

# 提取根目录文件
def extract_root_file(remote_path, local_path):
    log(f"提取文件: {remote_path} -> {local_path}")
    if run_command(f"adb pull {remote_path} {local_path}"):
        log(f"文件已提取到: {local_path}")
    else:
        log("文件提取失败。")

# 修补boot文件
def patch_boot(boot_image_path):
    log("开始修补boot文件...")
    magisk_path = "/path/to/magisk"  # 替换为Magisk工具的实际路径
    if not os.path.exists(magisk_path):
        log("未找到Magisk工具，请确保已正确安装Magisk。")
        return
    
    if run_command(f"{magisk_path} --patch {boot_image_path}"):
        log("boot文件修补成功！")
    else:
        log("boot文件修补失败。")

# 投屏功能
def screen_mirroring():
    log("启动手机投屏...")
    if run_command("scrcpy"):
        log("投屏已启动。")
    else:
        log("投屏启动失败，请确保已安装scrcpy。")

# 获取手机信息
def get_device_info():
    log("获取手机信息...")
    device_model = run_command("adb shell getprop ro.product.model")
    android_version = run_command("adb shell getprop ro.build.version.release")
    kernel_version = run_command("adb shell uname -r")
    system_version = run_command("adb shell getprop ro.build.display.id")
    
    log(f"手机型号: {device_model.strip()}")
    log(f"安卓版本: {android_version.strip()}")
    log(f"内核版本: {kernel_version.strip()}")
    log(f"系统版本: {system_version.strip()}")

# 检查设备状态
def check_device_state():
    log("检查设备状态...")
    state = check_device()
    if state:
        log(f"设备当前处于 {state} 模式。")
    else:
        log("设备未连接。")

# 检查A/B分区
def check_ab_partition():
    log("检查设备是否是A/B分区...")
    slot_a = run_command("adb shell getprop ro.boot.slot_suffix")
    if slot_a:
        log(f"设备是A/B分区，当前槽位: {slot_a.strip()}")
    else:
        log("设备不是A/B分区。")

# 解一加手机BL锁
def unlock_bootloader():
    log("开始解一加手机BL锁...")
    log("警告：解锁Bootloader会清除设备上的所有数据，请提前备份重要数据！")
    confirm = input("确认解锁Bootloader吗？(y/n): ").strip().lower()
    if confirm != "y":
        log("取消解锁Bootloader。")
        return
    
    log("重启设备到Fastboot模式...")
    run_command("adb reboot bootloader")
    time.sleep(10)  # 等待设备进入Fastboot模式

    log("解锁Bootloader...")
    output = run_command("fastboot oem unlock")
    if output and "OKAY" in output:
        log("Bootloader解锁成功！")
    else:
        log("Bootloader解锁失败，请检查设备是否支持解锁或是否已启用OEM解锁选项。")

# 检查更新
def check_for_updates():
    log("正在检查更新...")
    try:
        # 从远程获取最新版本号
        response = requests.get("https://example.com/version.txt")
        response.raise_for_status()
        latest_version = response.text.strip()

        if latest_version > CURRENT_VERSION:
            print(f"\033[93m[提示] 发现新版本: {latest_version}\033[0m")
            print(f"\033[93m[提示] 当前版本: {CURRENT_VERSION}\033[0m")
            print(f"\033[93m[提示] 请前往作者网盘下载最新版本: https://www.123912.com/s/S96sjv-pesD\033[0m")
        else:
            print(f"\033[92m[提示] 当前已是最新版本: {CURRENT_VERSION}\033[0m")
    except Exception as e:
        log(f"检查更新失败: {e}")

# 显示作者信息
def show_author():
    print(f"\n=== 刷机工具 by {AUTHOR} ===")
    print("欢迎使用刷机工具，请确保设备已连接并处于正确模式。\n")

# 显示公告信息
def show_announcement():
    print(ANNOUNCEMENT)

# 主菜单
def main_menu():
    while True:
        print("\n=== 刷机工具菜单 ===")
        print("1. 备份 boot 分区")
        print("2. 备份 recovery 分区")
        print("3. 刷入 boot 分区")
        print("4. 刷入 recovery 分区")
        print("5. 重启到系统")
        print("6. 重启到 Recovery 模式")
        print("7. 重启到 Bootloader 模式")
        print("8. 进入9008模式")
        print("9. 9008模式刷机")
        print("10. 访问手机根目录")
        print("11. 提取根目录文件")
        print("12. 修补boot文件")
        print("13. 投屏功能")
        print("14. 获取手机信息")
        print("15. 检查设备状态")
        print("16. 检查A/B分区")
        print("17. 解一加手机BL锁")
        print("18. 检查更新")  # 新增选项
        print("0. 退出")
        choice = input("请选择一个选项: ")

        if choice == "1":
            backup_partition("boot")
        elif choice == "2":
            backup_partition("recovery")
        elif choice == "3":
            image_path = input("请输入 boot 镜像路径: ")
            flash_partition("boot", image_path)
        elif choice == "4":
            image_path = input("请输入 recovery 镜像路径: ")
            flash_partition("recovery", image_path)
        elif choice == "5":
            reboot_device("system")
        elif choice == "6":
            reboot_device("recovery")
        elif choice == "7":
            reboot_device("bootloader")
        elif choice == "8":
            reboot_device("9008")
        elif choice == "9":
            firmware_path = input("请输入9008模式固件路径: ")
            flash_9008(firmware_path)
        elif choice == "10":
            access_root_directory()
        elif choice == "11":
            remote_path = input("请输入手机上的文件路径: ")
            local_path = input("请输入保存到电脑的路径: ")
            extract_root_file(remote_path, local_path)
        elif choice == "12":
            boot_image_path = input("请输入boot镜像路径: ")
            patch_boot(boot_image_path)
        elif choice == "13":
            screen_mirroring()
        elif choice == "14":
            get_device_info()
        elif choice == "15":
            check_device_state()
        elif choice == "16":
            check_ab_partition()
        elif choice == "17":
            unlock_bootloader()
        elif choice == "18":  # 新增功能
            check_for_updates()
        elif choice == "0":
            log("退出刷机工具。")
            break
        else:
            log("无效的选项，请重新选择。")

if __name__ == "__main__":
    log("启动刷机工具...")
    show_announcement()  # 显示公告信息
    show_author()  # 显示作者信息
    check_for_updates()  # 检查更新
    device_mode = check_device()
    if device_mode:
        main_menu()
    else:
        log("请连接设备并重试。")
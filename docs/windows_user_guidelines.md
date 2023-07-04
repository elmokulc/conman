# Windows User Guidelines

## Requirements

- Install Git SCM

## WSL2 and Docker Desktop

1 - Install WSL2 (source [here](https://learn.microsoft.com/en-us/windows/wsl/install))

        wsl --install
        wsl --set-default-version 2

2 - Install Ubuntu-20.04 with WSL2 set

        wsl --install -d Ubuntu-20.04

3 - Install Docker desktop

- After installation

  - Use WSL2 instead Hyper-V (Settings > General)
  - Goto Settings > Ressources > WSL integration, then select "Ubuntu-20.04" in Enable integration with additional distros.

4 - Update wsl :

        wsl --update

---

## Enabling Usb device for wsl

Some ressources are available [here](https://learn.microsoft.com/en-us/windows/wsl/connect-usb)

### USB device

1 - On Windows, Install the USBIPD-WIN project:
    -> Download and install [usbipd-win_x.msi file](https://github.com/dorssel/usbipd-win/releases)

2 - On Ubuntu-20.04, Install the USBIP tools and hardware database in Linux:

        sudo apt install linux-tools-generic hwdata
        sudo update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools/*-generic/usbip 20

3 - Attach a USB device

- On Windows, list all usb device:

            usbipd wsl list

- Select the bus ID of the device you’d like to attach to WSL:

        usbipd wsl attach --busid <busid>

- Open Ubuntu-20.04, and run (you should see the device you just attached):

        lsusb
- If you need to detach run the following command in Windows:

        usbipd wsl detach --busid <busid>

### Camera

1 - Run the following commands in your Ubuntu-20.04 distro:

    VERSION=$(uname -r | awk -F'[.-]' '{print $1"."$2"."$3}')
    sudo apt update
    sudo apt upgrade -y
    sudo apt install -y build-essential flex bison libgtk2.0-dev libelf-dev libncurses-dev autoconf libudev-dev libtool zip unzip v4l-utils libssl-dev python3-pip cmake git iputils-ping net-tools dwarves
    sudo mkdir /usr/src
    cd /usr/src
    sudo git clone -b linux-msft-wsl-${VERSION} https://github.com/microsoft/WSL2-Linux-Kernel.git ${VERSION}-microsoft-standard && cd ${VERSION}-microsoft-standard
    sudo cp /proc/config.gz config.gz
    sudo gunzip config.gz
    sudo mv config .config

2 - Maximize your terminal window, then run:

    sudo make menuconfig

Enabling the following features:

- Goto **Device Drivers** [HIT ENTER]

- Goto **Multimedia support** and include it [HIT DOUBLE SPACE] (You should see '*' appear), then [HIT ENTER]

- Include **Filter media drivers** [HIT DOUBLE SPACE]

- Goto **Media device types** [HIT ENTER], then include **Cameras and video grabbers** [HIT DOUBLE SPACE] and go back to **Multimedia support** by exiting

- Goto **Video4Linux options** [HIT ENTER], Include **V4L2 sub-device userspace API** [HIT DOUBLE SPACE] and go back to **Multimedia support** by exit

- Goto **Media drivers** [HIT ENTER] and include **Media USB Adapters** [HIT DOUBLE SPACE] then [HIT ENTER]
- In **Media USB Adapters**, include **USB Video class** [HIT DOUBLE SPACE] and **GSPCA based webcams** [HIT DOUBLE SPACE]

- Fully exit the installer wizard and **save your configuration**, a .config file should be written.

3 - Then run:

    sudo make -j$(nproc)
    sudo make modules_install -j$(nproc)
    sudo make install -j$(nproc)

A **vmlinux** file is then create, you can copy it to a source folder, here we choose the folder Sources at the root of C: hardrive

    sudo cp -rf vmlinux /mnt/c/Sources/

4 - Shutdown wsl, run in windows terminal:

    wsl --shudown

5 - Create or update you .wslconfig file (this is typcally locate at C://user/\<username\>/.wslconfig), by adding the following lines:

        [wsl2]
        kernel=C:\\Source\\vmlinux
        kernelCommandLine = usbcore.usbfs_memory_mb=256

*usbcore.usbfs_memory_mb* is used in case you are counting to use USB3 vision cameras [source-matrix-vision.com](https://www.matrix-vision.com/manuals/mvBlueFOX3/UseCases_section_mvBF3_in_docker.html) . By the way, you may also want to start udev service using :

    sudo /etc/init.d/udev start

<!-- In this case you can update /etc/wsl.conf inside your Ubuntu-20.04 container like : 

        [boot]
        systemd=true
        command=" -->
6 - Restart your Ubuntu-20.04 distro

        wsl --start

7 - Attach you camera using usbipd (Windows side):

        usbipd wsl attach --busid <your_requested>

8 - You should bind the folowing volumes in order to be use in Docker container :

    - /dev:/dev
    - /run/udev:/run/udev:ro

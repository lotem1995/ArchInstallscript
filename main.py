import os
import pacmanWrapper

BlockDevices=[]
Install_device=""

for entry in os.listdir("/sys/block"):
    BlockDevices.append(entry)
BlockDevices.sort()
print("""The next script will delete a disk and will install ArchLinux with luks.
    Select a device
    NOT for dual-boot, or deleting any other OS installed.
    First choose your desired block device
""")
for block_Device in BlockDevices:
    os.system("fdisk -l "+"/dev/"+block_Device)
    x=''
    while x not in ['y','n']:
        x = input("should I choose this disk? [Y,n]")
    if x=='y':
        Install_device="/dev/"+block_Device
        break
os.system(f"""parted --script "{Install_device}" -- mklabel gpt \
  mkpart ESP fat32 1Mib 512MiB \
  set 1 boot on \
  mkpart primary btrfs 512MiB 100%""")

EFI_Partition=Install_device+"1"
mnt_Partition=Install_device+"2"

os.system(f"mkfs.vfat -F32 {EFI_Partition}")
os.system(f"mkfs.btrfs -L system {mnt_Partition}")
os.system("lsblk")
shouldContinue=input("is that ok? [y/n] ")
if shouldContinue not in ['y','n']:
    print("Ctrl C to exit")
if not shouldContinue == 'n':
    os.system(f"mount {mnt_Partition} /mnt")
    os.system(f"mkdir /mnt/boot")
    os.system(f"mount {EFI_Partition} /mnt/boot")
    Pac = pacmanWrapper.pacman(None,"pacman")
    Pac.pacstrap(['base','linux','linux-firmware','vim','xf86-video-intel','xorg-server','plasma','plasma-wayland-session','firefox','vlc','git','base-devel','grub','bootmgr'],"/mnt")
    os.system("genfstab -U /mnt >> /mnt/etc/fstab")
    archCH="arch-chroot /mnt"
    os.system(f"{archCH} timedatectl set-timezone Asia/Jerusalem;{archCH} hwclock --systohc;cp -f /etc/locale.gen /mnt/etc/locale.gen;{archCH} locale-gen; echo Lang=en_US.UTF-8 >> /mnt/etc/locale.conf")
    hostname=input("Choose a hostname: ")
    os.system(f"echo {hostname} >> /mnt/etc/hostname;{archCH} mkinitcpio -P; {archCH} passwd;{archCH} systemctl enable sddm;{archCH} grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=ARCHLINUX;{archCH} grub-mkconfig -o /boot/grub/grub.cfg")
    os.system(f"{archCH} useradd -m lotem;")
    print("enter password:")
    os.system("echo lotem:password | chpasswd")
    os.system("umount -R /mnt")
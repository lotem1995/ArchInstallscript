#!/bin/bash

hostname=$(dialog --stdout --inputbox "Enter hostname" 0 0) || exit 1
clear
: ${hostname:?"hostname cannot be empty"}

user=$(dialog --stdout --inputbox "Enter admin username" 0 0) || exit 1
clear
: ${user:?"user cannot be empty"}

password=$(dialog --stdout --passwordbox "Enter admin password" 0 0) || exit 1
clear
: ${password:?"password cannot be empty"}
password2=$(dialog --stdout --passwordbox "Enter admin password again" 0 0) || exit 1
clear
[[ "$password" == "$password2" ]] || ( echo "Passwords did not match"; exit 1; )

devicelist=$(lsblk -dplnx size -o name,size | grep -Ev "boot|rpmb|loop" | tac)
device=$(dialog --stdout --menu "Select installation disk" 0 0 0 ${devicelist}) || exit 1
clear

timedatectl set-ntp true

parted --script "${device}" -- mklabel gpt \
  mkpart ESP fat32 1Mib 512MiB \
  set 1 boot on \
  mkpart primary btrfs 512 100%

part_boot="$(ls ${device}* | grep -E "^${device}p?1$")"
part_root="$(ls ${device}* | grep -E "^${device}p?3$")"

mkfs.vfat -F32 "${part_boot}"
mkfs.btrfs -L system "${part_root}"
mount "${part_root}" /mnt
mkdir /mnt/boot
mount "${part_boot}" /mnt/boot

pacstrap /mnt base linux linux-firmware vim xf86-video-intel xorg-server plasma plasma-wayland-session firefox vlc git base-devel grub bootmgr
genfstab -U /mnt >> /mnt/etc/fstab
echo "${hostname}" > /mnt/etc/hostname


arch-chroot /mnt timedatectl set-timezone Asia/Jerusalem
arch-chroot /mnt hwclock --systohc
echo "en_IL UTF-8" >> /mnt/etc/locale.gen

arch-chroot /mnt locale-gen
echo Lang=en_IL.UTF-8 >> /mnt/etc/locale.conf

arch-chroot /mnt mkinitcpio -P
arch-chroot /mnt useradd -m "$user"
echo "$user:$password" | chpasswd --root /mnt
echo "root:$password" | chpasswd --root /mnt
echo "ermanno ALL=(ALL) ALL" >> /mnt/etc/sudoers.d/ermanno
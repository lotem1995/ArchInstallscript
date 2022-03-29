import subprocess
from os import system as sys

class pacman:
    def __init__(self,sysroot,wrapper='pacman'):
        self.cmd=[wrapper,'--needed','--noconfirm','--sysroot'+' '+sysroot if sysroot is not None else '']
    def __pacman(self,cmdLine):
        try:
            p = subprocess.Popen(cmdLine,stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError or subprocess.TimeoutExpired:
            print("Error")
            return 1
        return 0

    def pacstrap(self,pkgs=None, mnt='/mnt'):
        output=0
        if pkgs is None:
            pkgs = ['base', 'linux', 'linux-firmware', 'vim']
        cmdLine=['pacstrap',mnt,'--noconfirm'].extend(pkgs)
        try:
            p=subprocess.Popen(cmdLine,stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError or subprocess.TimeoutExpired:
            print("Error")
            output=1
        return output

    def install(self,pkgs,):
        if pkgs is None:
            raise TypeError("Enter pkgs to install")
        cmdLine=self.cmd+['-S']+pkgs
        output=self.__pacman(cmdLine)
        return output
    def remove(self,pkgs):
        if pkgs is None:
            raise TypeError("Enter pkgs to install")
        cmdLine=self.cmd+['-R']+pkgs
        output = self.__pacman(cmdLine)
        return output

    def update(self):
        cmdLine=self.cmd+['-Syu']
        return self.__pacman(cmdLine)

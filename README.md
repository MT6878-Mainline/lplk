# lplk
#### Let's Patch LK!
lplk is a simple utility to de-quirk the stock Nothing LK for the CMF Phone 1, to allow for easier booting of postmarketOS and other mainline Linux distros.

It takes advantage of fenrir, an exploit found by **[Roger](https://github.com/R0rt1z2)** - thank you so much!

**WARNING** lplk replaces the stock bootloader. If something goes wrong, there may be *catastrophic* consequences. It's fairly well tested, but I'm NOT responsible for ANYTHING that happens to your device! Windows is required to unbrick (use tools found on xda) 

## Usage
Either download a **[release]([https://github.com/MT6878-Mainline/lplk/releases)**, or patch your bootloader, like so:
```
# first install a newer liblk
pip3 install --upgrade git+https://github.com/bengris32/liblk
<...>
# then patch your lk.img that's in the directory of lplk
python3 lplk.py
```
and then, flash it:
```
fastboot flash lk lplk_out.img reboot
```

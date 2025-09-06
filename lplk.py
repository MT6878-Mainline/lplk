# let's patch lk!
# for nothing cmf phone 1 (tetris)

from liblk import LkImage

# Snippet credits: https://github.com/R0rt1z2/liblk/blob/master/examples/apply_binary_patch.py
def validate_patch_input(needle: str, patch: str) -> tuple[bytes, bytes]:
    """
    Validate and convert patch inputs.

    Args:
        needle: Byte sequence to replace (hex string)
        patch: Replacement byte sequence (hex string)

    Returns:
        Tuple of needle and patch as bytes
    """
    try:
        needle_bytes = bytes.fromhex(needle)
        patch_bytes = bytes.fromhex(patch)
    except ValueError as e:
        raise ValueError(f'Invalid hex input: {e}')

    return needle_bytes, patch_bytes

def patch(lk: LkImage, target: str, patch: str):
    try:
        target_bytes, patch_bytes = validate_patch_input(target, patch)
        
        lk.apply_patch(target_bytes, patch_bytes)

    except NeedleNotFoundException as e:
        log.error(f'Bytes for patch not found! ({e})')
        raise ValueError(f'Bytes to patch were not found!')

def patch_string(lk: LkImage, target: str, _patch: str):
    if len(target) != len(_patch):
        raise ValueError(f"Target string length does not match patched string length!")

    target_bytes = target.encode("utf-8").hex()
    patch_bytes  = _patch.encode("utf-8").hex()

    patch(lk, target_bytes, patch_bytes)

def disable_lk_self_verify(lk: LkImage):
    # NOTE: Without this, the device will BRICK!!!
    # Disable image verification for every partition in lk, except dtbo and main_dtb
    # Credits for the discovery: https://github.com/R0rt1z2/fenrir/blob/main/injector/devices.py
    lk_exec = lk.partitions.__len__() - 2

    for n in range(lk_exec):
        print(f"Disabling verification in {list(lk.partitions.keys())[n]}")
        patch(lk, '000100b4fd7bbfa9', '00008052c0035fd6')

def autoboot_fastboot(lk: LkImage):
    # Skip the boot menu and only boot to fastboot mode.
    print("Skipping boot menu selection")

    # Always return 99 on bootmenu query
    patch(lk, '0004003622020094', '00040036600c8052')

def remove_avb_warnings(lk: LkImage):
    # Remove the "Orange state" warnings, as well as the 5 second delay on boot.
    print("Removing Orange State warnings")
    patch(lk, '6804009008a144b9', '680400902b000094')

def dont_overlay_dtbo(lk: LkImage):
    # Disable overlays, and DTBO
    print("Disabling DTBO \"Fixups\"")

    # Force-disable dtbo (HACK)
    patch(lk, "06680194d4010035", "06680194d4010034")

def dont_depend_on_weird_nodes(lk: LkImage):
    # Disable set_fdt hooks (they require some questionable nodes to be present)
    print("Disabling ALL set_fdt hooks")

    # Force-disable set_fdt (HACK)
    patch(lk, "1f0116eb40020054", "1f0116eb41020054")

def dont_map_framebuffer_memory(lk: LkImage):
    # Set framebuffer mblock reserved to a no-map
    print("NOT mapping framebuffer memory region")

    # This is the most complex of all. But, we're simply replacing this printf block:
    #   00013d64 e0 03 16 aa     mov        x0=>s_%s:%d:_mblock-R[%d].start:_0x%ll_000b95a
    #   00013d68 e1 03 17 aa     mov        x1=>s_mblock_show_internal_000c7693,x23
    #   00013d6c c2 13 80 52     mov        w2,#0x9e
    #   00013d70 e3 03 15 2a     mov        w3,w21
    #   00013d74 e5 03 18 aa     mov        x5,x24
    #   00013d78 51 56 01 94     bl         printf
    # with this:
    #   00013d64 1f 20 03 d5     nop
    #   00013d68 69 13 40 b9     ldr        w9,[x27, #0x10]
    #   00013d6c 0a 00 80 52     mov        w10,#0x0
    #   00013d70 bf 52 00 71     cmp        w21,#0x14
    #   00013d74 49 01 89 1a     csel       w9,w10,w9,eq
    #   00013d78 69 13 00 b9     str        w9,[x27, #0x10]
    patch(lk, "e00316aae10317aac2138052e303152ae50318aa51560194", "1f2003d5691340b90a008052bf5200714901891a691300b9")

def patch_for_mlk(lk: LkImage):
    print("- Applying quirks for booting mainline kernel -")
    dont_overlay_dtbo(lk)
    dont_depend_on_weird_nodes(lk)
    dont_map_framebuffer_memory(lk)

def main():
    lk = LkImage("lk.img")

    # 0. Booting tweaks
    disable_lk_self_verify(lk)

    # 1. Fastboot menu tweaks
    autoboot_fastboot(lk)

    # 2. Quality of life
    remove_avb_warnings(lk)

    # 3. LK un-quirking
    patch_for_mlk(lk)

    lk.save("lplk_out.img")
    
if __name__=="__main__":
    main()

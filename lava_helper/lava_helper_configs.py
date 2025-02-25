#!/usr/bin/env python3

""" lava_job_generator_configs.py:

    Default configurations for lava job generator """

from __future__ import print_function

__copyright__ = """
/*
 * SPDX-FileCopyrightText: Copyright The TrustedFirmware-M Contributors
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """

__author__ = "tf-m@lists.trustedfirmware.org"
__project__ = "Trusted Firmware-M Open CI"
__version__ = "1.4.0"


import os


tf_downloads="https://downloads.openci.arm.com"
coverage_trace_plugin=tf_downloads + "/coverage-plugin/qa-tools/coverage-tool/coverage-plugin/coverage_trace.so"


# LAVA test-monitor definition for configs without regression tests.
# "Non-Secure system starting..." is expected to indicate
# that TF-M has been booted successfully.
no_reg_tests_monitors_cfg = {
    'name': 'NS_SYSTEM_BOOTING',
    'start': 'Non-Secure system',
    'end': r'starting\\.{3}',
    'pattern': r'Non-Secure system starting\\.{3}',
    'fixup': {"pass": "!", "fail": ""},
}

# LAVA test-monitor definitions for configs with tests.
# Results of each test case is parsed separately, capturing test case id.
# Works across any test suites enabled.
mcuboot_tests_monitor_cfg = {
    'name': 'mcuboot_suite',
    'start': 'Execute test suites for the MCUBOOT area',
    'end': 'End of MCUBOOT test suites',
    'pattern': r"TEST: (?P<test_case_id>.+?) - (?P<result>(PASSED|FAILED|SKIPPED))",
    'fixup': {"pass": "PASSED", "fail": "FAILED", "skip": "SKIPPED"},
}

s_reg_tests_monitors_cfg = {
    'name': 'secure_regression_suite',
    'start': 'Execute test suites for the Secure area',
    'end': 'End of Secure test suites',
    'pattern': r"TEST: (?P<test_case_id>.+?) - (?P<result>(PASSED|FAILED|SKIPPED))",
    'fixup': {"pass": "PASSED", "fail": "FAILED", "skip": "SKIPPED"},
}

ns_reg_tests_monitors_cfg = {
    'name': 'non_secure_regression_suite',
    'start': 'Execute test suites for the Non-secure area',
    'end': 'End of Non-secure test suites',
    'pattern': r"TEST: (?P<test_case_id>.+?) - (?P<result>(PASSED|FAILED|SKIPPED))",
    'fixup': {"pass": "PASSED", "fail": "FAILED", "skip": "SKIPPED"},
}

bl1_1_reg_tests_monitors_cfg = {
    'name': 'BL1_1_regression_suite',
    'start': 'Execute test suites for the BL1_1 area',
    'end': 'End of BL1_1 test suites',
    'pattern': r"TEST: (?P<test_case_id>.+?) - (?P<result>(PASSED|FAILED|SKIPPED))",
    'fixup': {"pass": "PASSED", "fail": "FAILED", "skip": "SKIPPED"},
}

bl1_2_reg_tests_monitors_cfg = {
    'name': 'BL1_2_regression_suite',
    'start': 'Execute test suites for the BL1_2 area',
    'end': 'End of BL1_2 test suites',
    'pattern': r"TEST: (?P<test_case_id>.+?) - (?P<result>(PASSED|FAILED|SKIPPED))",
    'fixup': {"pass": "PASSED", "fail": "FAILED", "skip": "SKIPPED"},
}

arch_tests_monitors_cfg = {
    'name': 'psa_api_suite',
    'start': 'Running..',
    'end': 'Entering standby..',
    'pattern': r" DESCRIPTION: +(?P<test_case_id>.+?)\r?\n"
                r".+?"
                r"TEST RESULT: (?P<result>(PASSED|FAILED|SKIPPED|SIM ERROR))",
    'fixup': {"pass": "PASSED", "fail": "FAILED", "skip": "SKIPPED", "sim_error": "SIM ERROR"},
}

# Group related monitors into same list to simplify the code
no_reg_tests_monitors = [no_reg_tests_monitors_cfg]

reg_tests_monitors = [] + \
                     ([mcuboot_tests_monitor_cfg] if "RegBL2" in os.getenv("TEST_REGRESSION") and os.getenv("BL2") == "True" else []) + \
                     ([s_reg_tests_monitors_cfg] if "RegS" in os.getenv("TEST_REGRESSION") else []) + \
                     ([ns_reg_tests_monitors_cfg] if "RegNS" in os.getenv("TEST_REGRESSION") else []) + \
                     ([bl1_1_reg_tests_monitors_cfg] if "RegBL1_1" in os.getenv("TEST_REGRESSION") else []) + \
                     ([bl1_2_reg_tests_monitors_cfg] if "RegBL1_2" in os.getenv("TEST_REGRESSION") else [])

arch_tests_monitors = [arch_tests_monitors_cfg]


# MPS2 with BL2 bootloader for AN521
# IMAGE0ADDRESS: 0x10000000
# IMAGE0FILE: \Software\bl2.bin  ; BL2 bootloader
# IMAGE1ADDRESS: 0x10080000
# IMAGE1FILE: \Software\tfm_s_ns_signed.bin ; TF-M example application binary blob
tfm_mps2_sse_200 = {
    "templ": "mps2.jinja2",
    "job_name": "mps2_an521_bl2",
    "device_type": "mps",
    "job_timeout": 15,
    "notification_email": "tf-m-ci-notifications@lists.trustedfirmware.org",
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "recovery_store_url": "https://ci.trustedfirmware.org/userContent/",
    "platforms": {"arm/mps2/an521": "mps2_sse200_an512_new.tar.gz"},
    "binaries": {
        # Run script references to test_.*/.*.bin
        # These files will be saved under folders: test_firmware and test_bootloader
        "test_firmware": {
            "data": "nspe/tfm_s_ns_signed.bin"
        },
        "test_bootloader": {
            "data": "spe/bin/bl2.bin"
        }
    },
    "monitors": {
        'no_reg_tests': no_reg_tests_monitors,
        # FPU test on FPGA not supported yet
        'reg_tests': (reg_tests_monitors if 'FPON' not in os.getenv("EXTRA_PARAMS") else [mcuboot_tests_monitor_cfg]),
        # FF test on FPGA not supported in LAVA yet
        'arch_tests': (arch_tests_monitors if os.getenv("TEST_PSA_API") != "IPC" else []),
    }
}

# FVP with BL2 bootloader for Corstone300
# firmware <-> ns <-> application: --application cpu0=bl2.axf
# bootloader <-> s <-> data: --data cpu0=tfm_s_ns_signed.bin@0x01000000
fvp_mps3_cs300_bl2 = {
    "templ": "fvp_mps3.jinja2",
    "job_name": "fvp_mps3_cs300_bl2",
    "device_type": "fvp",
    "job_timeout": 15,
    "notification_email": "tf-m-ci-notifications@lists.trustedfirmware.org",
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "platforms": {"arm/mps3/corstone300/fvp": ""},
    "binaries": {
        "bl2": {
            "application": "spe/bin/bl2.axf"
        },
        "tfm_s_ns_img": {
            "data": "nspe/tfm_s_ns_signed.bin",
            "offset": "0x38000000",
        }
    },
    "monitors": {
        'no_reg_tests': no_reg_tests_monitors,
        'reg_tests': reg_tests_monitors,
    }
}

# FVP with BL1 and BL2 bootloader for Corstone315
fvp_mps4_cs315_bl1_bl2 = {
    "templ": "fvp_mps4_cs315.jinja2",
    "job_name": "fvp_mps4_cs315_bl1_bl2",
    "device_type": "fvp",
    "job_timeout": 15,
    "notification_email": "tf-m-ci-notifications@lists.trustedfirmware.org",
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "platforms": {"arm/mps4/corstone315": ""},
    "binaries": {
        "bl1": {
            "data": "spe/bin/bl1_1.bin",
            "offset": "0x11000000",
        },
        "bl2": {
            "data": "spe/bin/bl2_signed.bin",
            "offset": "0x12031400",
        },
        "cm_prov": {
            "data": "spe/bin/cm_provisioning_bundle.bin",
            "offset": "0x12024000",
        },
        "dm_prov": {
            "data": "spe/bin/dm_provisioning_bundle.bin",
            "offset": "0x1202aa00",
        },
        "tfm_s_ns_img": {
            "data": "nspe/tfm_s_ns_signed.bin",
            "offset": "0x38000000",
        }
    },
    "monitors": {
        'no_reg_tests': no_reg_tests_monitors,
        'reg_tests': reg_tests_monitors,
    }
}

# FVP with BL1 and BL2 bootloader for Corstone320
fvp_mps4_cs320_bl1_bl2 = {
    "templ": "fvp_mps4_cs320.jinja2",
    "job_name": "fvp_mps4_cs320_bl1_bl2",
    "device_type": "fvp",
    "job_timeout": 15,
    "notification_email": "tf-m-ci-notifications@lists.trustedfirmware.org",
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "platforms": {"arm/mps4/corstone320": ""},
    "binaries": {
        "bl1": {
            "data": "spe/bin/bl1_1.bin",
            "offset": "0x11000000",
        },
        "bl2": {
            "data": "spe/bin/bl2_signed.bin",
            "offset": "0x12031400",
        },
        "cm_prov": {
            "data": "spe/bin/cm_provisioning_bundle.bin",
            "offset": "0x12024000",
        },
        "dm_prov": {
            "data": "spe/bin/dm_provisioning_bundle.bin",
            "offset": "0x1202aa00",
        },
        "tfm_s_ns_img": {
            "data": "nspe/tfm_s_ns_signed.bin",
            "offset": "0x38000000",
        }
    },
    "monitors": {
        'no_reg_tests': no_reg_tests_monitors,
        'reg_tests': reg_tests_monitors,
    }
}

# FVP with BL1 and BL2 bootloader for Corstone1000
fvp_corstone1000 = {
    "templ": "fvp_corstone1000.jinja2",
    "job_name": "fvp_corstone1000",
    "device_type": "fvp",
    "job_timeout": 15,
    "notification_email": "tf-m-ci-notifications@lists.trustedfirmware.org",
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "platforms": {"arm/corstone1000": ""},
    "binaries": {
        "bl1": {
            "application": "spe/bin/bl1.bin"
        },
        "tfm_s_ns_img": {
            "data": "spe/bin/cs1000.bin",
            "offset": "0x68000000",
        }
    },
    "monitors": {
        'reg_tests': reg_tests_monitors if "FVP" in os.getenv('EXTRA_PARAMS') else [],
    }
}

# FVP with BL2 bootloader for AN521
# application: --application cpu0=bl2.axf
# data: --data cpu0=tfm_s_ns_signed.bin@0x10080000
fvp_mps2_an521_bl2 = {
    "templ": "fvp_mps2.jinja2",
    "job_name": "fvp_mps2_an521_bl2",
    "device_type": "fvp",
    "job_timeout": 15,
    "notification_email": "tf-m-ci-notifications@lists.trustedfirmware.org",
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "platforms": {"arm/mps2/an521": ""},
    "binaries": {
        "bl2": {
            "application": "spe/bin/bl2.axf"
        },
        "tfm_s_ns_img": {
            "data": "nspe/tfm_s_ns_signed.bin",
            "offset": "0x10080000",
        }
    },
    "monitors": {
        'no_reg_tests': no_reg_tests_monitors,
        'reg_tests': reg_tests_monitors,
        'arch_tests': arch_tests_monitors,
    }
}


# FVP with BL2 bootloader for AN519
# application: --application cpu0=bl2.axf
# data: --data cpu0=tfm_s_ns_signed.bin@0x10080000
fvp_mps2_an519_bl2 = {
    "templ": "fvp_mps2.jinja2",
    "job_name": "fvp_mps2_an519_bl2",
    "device_type": "fvp",
    "job_timeout": 15,
    "notification_email": "tf-m-ci-notifications@lists.trustedfirmware.org",
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "platforms": {"arm/mps2/an519": ""},
    "cpu0_baseline": 1,
    "binaries": {
        "bl2": {
            "application": "spe/bin/bl2.axf"
        },
        "tfm_s_ns_img": {
            "data": "nspe/tfm_s_ns_signed.bin",
            "offset": "0x10080000",
        }
    },
    "monitors": {
        'no_reg_tests': no_reg_tests_monitors,
        'reg_tests': reg_tests_monitors,
    }
}

# RSE on TC3 FVP
fvp_rse_tc3 = {
    "templ": "fvp_rse_tc3.jinja2",
    "job_name": "fvp_rse_tc3",
    "device_type": "fvp",
    "job_timeout": 15,
    "notification_email": "tf-m-ci-notifications@lists.trustedfirmware.org",
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "platforms": {"arm/rse/tc/tc3": ""},
    "binaries": {
        "rom": {
            "data": "spe/bin/rom.bin"
        },
        "combined_provisioning_message": {
            "data": "spe/bin/provisioning/combined_provisioning_message.bin"
        },
        "flash": {
            "data": "spe/bin/host_flash.bin"
        }
    },
    "monitors": {
        'no_reg_tests': no_reg_tests_monitors,
        'reg_tests': reg_tests_monitors,
    }
}

# RSE on TC4 FVP
fvp_rse_tc4 = {
    "templ": "fvp_rse_tc4.jinja2",
    "job_name": "fvp_rse_tc4",
    "device_type": "fvp",
    "job_timeout": 15,
    "notification_email": "tf-m-ci-notifications@lists.trustedfirmware.org",
    "action_timeout": 10,
    "monitor_timeout": 15,
    "poweroff_timeout": 1,
    "platforms": {"arm/rse/tc/tc4": ""},
    "binaries": {
        "rom": {
            "data": "spe/bin/rom.bin"
        },
        "combined_provisioning_message": {
            "data": "spe/bin/provisioning/combined_provisioning_message.bin"
        },
        "flash": {
            "data": "spe/bin/host_flash.bin"
        }
    },
    "monitors": {
        'no_reg_tests': no_reg_tests_monitors,
        'reg_tests': reg_tests_monitors,
    }
}

# QEMU for AN521 with BL2 bootloader
qemu_mps2_bl2 = {
    "templ": "qemu_mps2_bl2.jinja2",
    "job_name": "qemu_mps2_bl2",
    "device_type": "qemu",
    "job_timeout": 30,
    "notification_email": "tf-m-ci-notifications@lists.trustedfirmware.org",
    "action_timeout": 20,
    "monitor_timeout": 20,
    "poweroff_timeout": 1,
    "platforms": {"arm/mps2/an521": ""},
    "binaries": {
        "mcuboot": {
            "data": "spe/bin/bl2.bin",
            "offset": "0x10000000"
        },
        "tfm": {
            "data": "nspe/tfm_s_ns_signed.bin",
            "offset": "0x10080000"
        }
    },
    "monitors": {
        # FPU test on AN521 qemu not supported yet
        'reg_tests': (reg_tests_monitors if 'FPON' not in os.getenv("EXTRA_PARAMS") else [mcuboot_tests_monitor_cfg]),
    }
}


# Musca-B1 with BL2 bootloader
# unified hex file comprising of both bl2.bin and tfm_s_ns_signed.bin
# srec_cat bin/bl2.bin -Binary -offset 0xA000000 bin/tfm_s_ns_signed.bin -Binary -offset 0xA020000 -o tfm.hex -Intel
musca_b1_bl2 = {
    "templ": "musca_b1.jinja2",
    "job_name": "musca_b1_bl2",
    "device_type": "musca-b",
    "job_timeout": 40,
    "notification_email": "tf-m-ci-notifications@lists.trustedfirmware.org",
    "action_timeout": 20,
    "monitor_timeout": 10,
    "poweroff_timeout": 5,
    "platforms": {"arm/musca_b1": ""},
    "binaries": {
        "test_binary": {
            "data": "spe/bin/tfm.hex"   # firmware
        }
    },
    "monitors": {
        'no_reg_tests': no_reg_tests_monitors,
        'reg_tests': reg_tests_monitors,
    }
}

# STM32L562E-DK
stm32l562e_dk = {
    "templ": "stm32l562e_dk.jinja2",
    "job_name": "stm32l562e_dk",
    "device_type": "stm32l562e-dk",
    "job_timeout": 24,
    "notification_email": "tf-m-ci-notifications@lists.trustedfirmware.org",
    "action_timeout": 15,
    "monitor_timeout": 15,
    "poweroff_timeout": 5,
    "platforms": {"stm/stm32l562e_dk": ""},
    "binaries": {
        "tarball": {
            "data": "spe/api_ns/bin/stm32l562e-dk-tfm.tar.bz2"
        }
    },
    "monitors": {
        'reg_tests': reg_tests_monitors,
    }
}

# STM32U5 B-U585I-IOT02A
b_u585i_iot02a = {
    "templ": "b_u585i_iot02a.jinja2",
    "job_name": "b_u585i_iot02a",
    "device_type": "b-u585i-iot02a",
    "job_timeout": 5,
    "notification_email": "tf-m-ci-notifications@lists.trustedfirmware.org",
    "action_timeout": 3,
    "monitor_timeout": 3,
    "poweroff_timeout": 2,
    "platforms": {"stm/b_u585i_iot02a": ""},
    "binaries": {
        "tarball": {
            "data": "spe/api_ns/bin/b_u585i_iot02a-tfm.tar.bz2"
        }
    },
    "monitors": {
        'reg_tests': reg_tests_monitors,
    }
}

# STM32H5 STM32H573I-DK
stm32h573i_dk = {
    "templ": "stm32h573i_dk.jinja2",
    "job_name": "stm32h573i_dk",
    "device_type": "stm32h573i-dk",
    "job_timeout": 5,
    "notification_email": "tf-m-ci-notifications@lists.trustedfirmware.org",
    "action_timeout": 3,
    "monitor_timeout": 3,
    "poweroff_timeout": 2,
    "platforms": {"stm/stm32h573i_dk": ""},
    "binaries": {
        "tarball": {
            "data": "spe/api_ns/bin/stm32h573i_dk-tfm.tar.bz2"
        }
    },
    "monitors": {
        'reg_tests': reg_tests_monitors,
    }
}

# LPCxpresso55S69
lpcxpresso55s69 = {
    "templ": "lpcxpresso55s69.jinja2",
    "job_name": "lpcxpresso55s69",
    "device_type": "lpcxpresso55s69",
    "job_timeout": 24,
    "notification_email": "tf-m-ci-notifications@lists.trustedfirmware.org",
    "action_timeout": 15,
    "monitor_timeout": 15,
    "poweroff_timeout": 5,
    "platforms": {"nxp/lpcxpresso55s69": ""},
    "binaries": {
        "tarball": {
            "data": "nspe/bin/lpcxpresso55s69-tfm.tar.bz2"
        }
    },
    "monitors": {
        'no_reg_tests': no_reg_tests_monitors,
        'reg_tests': reg_tests_monitors,
    }
}

# Cypress PSoC64
psoc64 = {
    "templ": "psoc64.jinja2",
    "job_name": "psoc64",
    "device_type": "cy8ckit-064s0s2-4343w",
    "job_timeout": 30,
    "notification_email": "tf-m-ci-notifications@lists.trustedfirmware.org",
    "action_timeout": 20,
    "monitor_timeout": 20,
    "poweroff_timeout": 5,
    "platforms": {"cypress/psoc64": ""},
    "binaries": {
        "spe": {
            "data": "spe/bin/tfm_s_signed.hex"
        },
        "nspe": {
            "data": "nspe/tfm_ns_signed.hex"
        }
    },
    "monitors": {
        'reg_tests': reg_tests_monitors,
    }
}

# All configurations should be mapped here
# Configs need bl2
lava_gen_config_map_bl2 = {
    "mps2_an521_bl2": tfm_mps2_sse_200,
    "fvp_mps3_cs300_bl2": fvp_mps3_cs300_bl2,
    "fvp_mps2_an521_bl2": fvp_mps2_an521_bl2,
    "fvp_mps2_an519_bl2": fvp_mps2_an519_bl2,
    "fvp_mps4_cs315_bl1_bl2": fvp_mps4_cs315_bl1_bl2,
    "fvp_mps4_cs320_bl1_bl2": fvp_mps4_cs320_bl1_bl2,
    "fvp_corstone1000": fvp_corstone1000,
    "fvp_rse_tc3": fvp_rse_tc3,
    "fvp_rse_tc4": fvp_rse_tc4,
    "qemu_mps2_bl2": qemu_mps2_bl2,
    "musca_b1": musca_b1_bl2,
    "stm32l562e_dk": stm32l562e_dk,
    "b_u585i_iot02a": b_u585i_iot02a,
    "stm32h573i_dk": stm32h573i_dk
}

# Configs without bl2
lava_gen_config_map_nobl2 = {
    "lpcxpresso55s69": lpcxpresso55s69,
    "psoc64": psoc64,
}

lavagen_config_sort_order = [
    "templ",
    "job_name",
    "device_type",
    "job_timeout",
    "action_timeout",
    "monitor_timeout",
    "recovery_store_url",
    "platforms",
    "monitors"
]

lava_gen_monitor_sort_order = [
    'name',
    'start',
    'end',
    'pattern',
    'fixup',
]

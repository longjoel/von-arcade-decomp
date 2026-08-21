printf "BOOT_TRACE_SCRIPT_LOADED\n"
bp 00000930:maincpu,{ logerror "RESET_ENTRY pc=%08X\n",pc ; g }
wp 00e00000:maincpu,4,w,{ logerror "EARLY_WRITE address=%08X data=%08X\n",wpaddr,wpdata ; g }
wp 00501814:maincpu,4,w,{ logerror "WORKRAM_WRITE address=%08X data=%08X\n",wpaddr,wpdata ; g }
wp 00501800:maincpu,4,w,{ logerror "WORKRAM_TABLE address=%08X data=%08X\n",wpaddr,wpdata ; g }
g

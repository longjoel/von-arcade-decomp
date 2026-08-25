# Export a small, reviewable report from the generated Ghidra project.
# This is intentionally limited to known anchors; it is a processor-module
# sanity check, not a replacement for the source annotations.

from ghidra.app.decompiler import DecompInterface


def addr(value):
    return toAddr(value)


def report_function(entry):
    function_manager = currentProgram.getFunctionManager()
    function = function_manager.getFunctionAt(addr(entry))
    if function is None:
        function = function_manager.getFunctionContaining(addr(entry))
    if function is None:
        print("FUNCTION 0x%08x <none>" % entry)
        return

    print("FUNCTION 0x%08x %s" % (function.getEntryPoint().getOffset(),
                                  function.getName()))
    print("  body=%s" % function.getBody())

    decompiler = DecompInterface()
    decompiler.openProgram(currentProgram)
    result = decompiler.decompileFunction(function, 30, monitor)
    if result.decompileCompleted():
        print("  DECOMPILE_BEGIN")
        print(result.getDecompiledFunction().getC())
        print("  DECOMPILE_END")
    else:
        print("  DECOMPILE_ERROR %s" % result.getErrorMessage())


def report_instructions(start, end):
    listing = currentProgram.getListing()
    iterator = listing.getInstructions(addr(start), True)
    print("INSTRUCTIONS 0x%08x-0x%08x" % (start, end))
    for instruction in iterator:
        address = instruction.getAddress().getOffset()
        if address >= end:
            break
        print("  %08x  %-32s %s" % (
            address,
            instruction.getMnemonicString(),
            instruction.toString()))


report_function(0x930)
report_instructions(0x930, 0xA40)
report_function(0x3C40)
report_function(0x28620)
report_instructions(0x28620, 0x28758)
report_function(0x284b0)
report_function(0x28de8)
report_function(0x28e88)
report_function(0x28c00)
report_function(0x28c80)
report_function(0x28d80)
report_function(0x28b40)
report_function(0x28b80)
report_function(0x28418)
report_function(0x28d08)
report_function(0x28548)
report_function(0x28d30)
report_function(0x28840)

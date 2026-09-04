# Build and regression entry points for the recovered C contracts.
#
# The recovered files are independent models and are intentionally checked as
# translation units rather than linked into one executable: many expose the
# same recovered entry-point names in different address-specific contracts.

CC ?= cc
CFLAGS ?= -std=c11 -Wall -Wextra -Werror

RECOVERED_C := $(wildcard i960/recovered_*.c)
RECOVERED_HEADERS := i960/recovered_common.h i960/recovered_float.h

.PHONY: all check-recovered-c test-recovered test-unit test-contract build-i960 run-mame check clean

all: check-recovered-c

check-recovered-c: $(RECOVERED_C) $(RECOVERED_HEADERS)
	$(CC) $(CFLAGS) -fsyntax-only $(RECOVERED_C)

test-recovered:
	python3 tools/test_recovered_io.py

test-unit:
	cd .. && python3 von/tools/run_tests.py unit

test-contract:
	cd .. && python3 von/tools/run_tests.py contract

# These targets use the pinned cross-toolchain and the MAME staging workflow.
# They are intentionally separate from the host-only checks above.
build-i960:
	cd .. && ./scripts/i960-build.sh

run-mame:
	cd .. && ./scripts/run-i960-reconstructed.sh $(MAME_ARGS)

check: check-recovered-c test-recovered test-unit test-contract

clean:
	@:

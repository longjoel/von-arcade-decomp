/* Minimal freestanding <stdint.h> for the pinned i960-elf toolchain.
 *
 * The i960_sbc image ships a bare i960-elf-gcc with no C library headers, so
 * recovered sources that say `#include <stdint.h>` (host_control, memory, text,
 * object_state_runtime, reconstructed_reset) need this shim. i960 is a 32-bit
 * target; keep the widths exact. */
#ifndef VON_I960_STDINT_H
#define VON_I960_STDINT_H

typedef signed char        int8_t;
typedef unsigned char      uint8_t;
typedef signed short       int16_t;
typedef unsigned short     uint16_t;
typedef signed int         int32_t;
typedef unsigned int       uint32_t;
typedef signed long long   int64_t;
typedef unsigned long long uint64_t;

typedef int32_t  intptr_t;
typedef uint32_t uintptr_t;
typedef int32_t  intmax_t;
typedef uint32_t uintmax_t;

typedef int8_t  int_least8_t;
typedef uint8_t uint_least8_t;
typedef int16_t int_least16_t;
typedef uint16_t uint_least16_t;
typedef int32_t int_least32_t;
typedef uint32_t uint_least32_t;
typedef int64_t int_least64_t;
typedef uint64_t uint_least64_t;

typedef int32_t  int_fast8_t;
typedef uint32_t uint_fast8_t;
typedef int32_t  int_fast16_t;
typedef uint32_t uint_fast16_t;
typedef int32_t  int_fast32_t;
typedef uint32_t uint_fast32_t;
typedef int64_t  int_fast64_t;
typedef uint64_t uint_fast64_t;

#define INT8_MIN   (-128)
#define INT16_MIN  (-32767 - 1)
#define INT32_MIN  (-2147483647 - 1)
#define INT64_MIN  (-9223372036854775807LL - 1)
#define INT8_MAX   127
#define INT16_MAX  32767
#define INT32_MAX  2147483647
#define INT64_MAX  9223372036854775807LL
#define UINT8_MAX  255
#define UINT16_MAX 65535
#define UINT32_MAX 4294967295U
#define UINT64_MAX 18446744073709551615ULL

#define INT8_C(x)  x
#define INT16_C(x) x
#define INT32_C(x) x
#define INT64_C(x) x##LL
#define UINT8_C(x)  x
#define UINT16_C(x) x
#define UINT32_C(x) x##U
#define UINT64_C(x) x##ULL

#define INTMAX_C(x)  x
#define UINTMAX_C(x) x##U

#endif /* VON_I960_STDINT_H */

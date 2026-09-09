/* Scheduler status path recovered from i960 0x83148-0x83300. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_scheduler_status_path_83148_route {
    RECOVERED_STATUS_PATH_WRITE_STATUS = 0,
    RECOVERED_STATUS_PATH_CALL_82800 = 1,
    RECOVERED_STATUS_PATH_STATUS_18 = 2,
    RECOVERED_STATUS_PATH_STATUS_19 = 3,
    RECOVERED_STATUS_PATH_STATUS_27 = 4,
    RECOVERED_STATUS_PATH_STATUS_33 = 5,
    RECOVERED_STATUS_PATH_STATUS_34 = 6
};

struct recovered_state_scheduler_status_path_83148 {
    enum recovered_state_scheduler_status_path_83148_route route;
    u32 write_504e1c;
    u32 value_504e1c;
    u32 write_504d80;
    u32 value_504d80;
    u32 write_504d8c;
    u32 value_504d8c;
    u32 write_504d90;
    u32 value_504d90;
    u32 random_calls;
};

static void publish_tail(struct recovered_state_scheduler_status_path_83148 *out)
{
    out->write_504d8c = 1U;
    out->write_504d90 = 1U;
    out->value_504d90 = 15U;
}

static void publish_status(struct recovered_state_scheduler_status_path_83148 *out,
                           u32 status,
                           enum recovered_state_scheduler_status_path_83148_route route)
{
    out->route = route;
    out->write_504d80 = 1U;
    out->value_504d80 = status;
}

struct recovered_state_scheduler_status_path_83148
recovered_state_scheduler_status_path_83148(u32 object_state,
                                            int32_t current_timing,
                                            int32_t converted_504df8,
                                            int32_t random_value,
                                            int32_t value_504dc0,
                                            u32 control_504e30,
                                            u32 control_504e28,
                                            int32_t pair_504e20,
                                            u32 handler_status,
                                            u32 caller_g14)
{
    struct recovered_state_scheduler_status_path_83148 out = {
        RECOVERED_STATUS_PATH_WRITE_STATUS, 1U, 1U, 0U, 0U,
        0U, 0U, 0U, 0U, 0U
    };
    int32_t remainder;

    if (object_state == 5U) {
        if (current_timing < converted_504df8) {
            out.random_calls = 0U;
            publish_status(&out, handler_status,
                           RECOVERED_STATUS_PATH_CALL_82800);
            return out;
        }
        if (current_timing < 0) {
            publish_status(&out, 18U, RECOVERED_STATUS_PATH_STATUS_18);
            return out;
        }
        out.random_calls = 1U;
        remainder = random_value % 10;
        if (remainder > 3) {
            publish_status(&out, 33U,
                           RECOVERED_STATUS_PATH_STATUS_33);
        } else if (control_504e28 == 1U && pair_504e20 == current_timing) {
            publish_status(&out, 27U,
                           RECOVERED_STATUS_PATH_STATUS_27);
        } else {
            publish_status(&out, 19U,
                           RECOVERED_STATUS_PATH_STATUS_19);
        }
        return out;
    }

    out.random_calls = 1U;
    if (current_timing < converted_504df8) {
        publish_status(&out, handler_status,
                       RECOVERED_STATUS_PATH_CALL_82800);
        out.value_504d8c = caller_g14;
        publish_tail(&out);
        return out;
    }
    if (current_timing < 0) {
        publish_status(&out, 18U, RECOVERED_STATUS_PATH_STATUS_18);
        publish_tail(&out);
        return out;
    }
    remainder = random_value % 17;
    if (remainder <= 13) {
        remainder = random_value % 6;
        if (remainder <= 3 || (control_504e30 & 2U) == 0U) {
            publish_status(&out, 33U, RECOVERED_STATUS_PATH_STATUS_33);
        } else if (control_504e28 == 1U && pair_504e20 == current_timing) {
            publish_status(&out, 27U, RECOVERED_STATUS_PATH_STATUS_27);
        } else {
            publish_status(&out, 19U, RECOVERED_STATUS_PATH_STATUS_19);
        }
    } else if (value_504dc0 <= 120) {
        /* The image adjusts signed negative values before clearing bit 0;
         * this is equivalent to an even/odd test over the signed remainder. */
        if (((uint32_t)remainder & 1U) == 0U)
            publish_status(&out, 33U, RECOVERED_STATUS_PATH_STATUS_33);
        else
            publish_status(&out, 34U, RECOVERED_STATUS_PATH_STATUS_34);
    } else {
        publish_status(&out, handler_status,
                       RECOVERED_STATUS_PATH_CALL_82800);
        out.value_504d8c = caller_g14;
        publish_tail(&out);
        return out;
    }
    out.value_504d8c = caller_g14;
    publish_tail(&out);
    return out;
}

/* Pure state-gate continuation from i960 0x7f5d0-0x7f6b0.
 * Floating-point/FIFO decisions are supplied as booleans by the caller. */
#include "recovered_common.h"
struct recovered_geometry_accumulator_transition_7f5d0_input { recovered_u32 state170, state172, mode64, gate504d68, gate504da4, gate504dc8; recovered_u32 candidate_pass, metric_pass, threshold_pass; };
struct recovered_geometry_accumulator_transition_7f5d0_plan { recovered_u32 eligible, action_state, action_code; };
void recovered_geometry_accumulator_transition_7f5d0(const struct recovered_geometry_accumulator_transition_7f5d0_input *i, struct recovered_geometry_accumulator_transition_7f5d0_plan *p)
{
 p->eligible=i->candidate_pass && i->metric_pass && i->threshold_pass;
 p->action_state=0; p->action_code=0;
 if (p->eligible && (i->state170==3U || i->state172==1U) && i->mode64==3U && i->gate504d68>=7U) { p->action_state=1U; p->action_code=10U; }
 if (i->mode64==4U && i->state170==3U && i->state172==1U && i->gate504d68<5U) { p->action_state=4U; p->action_code=4U; }
}

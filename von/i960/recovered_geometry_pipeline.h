#ifndef VON_RECOVERED_GEOMETRY_PIPELINE_H
#define VON_RECOVERED_GEOMETRY_PIPELINE_H

/* Public boundary between the reconstructed startup path and geometry code. */
typedef unsigned long recovered_geometry_u32;

void recovered_geometry_frame_submission(void);
void recovered_geometry_match_object_seed(void);
void recovered_geometry_buffer_prepare(volatile recovered_geometry_u32 *output);
void recovered_geometry_profile_setup(void);
void recovered_sharc_bootstrap_upload(void);
void recovered_geometry_program_upload(void);
void recovered_texture_initializer(void);
int recovered_texture_loader_profile_setup(void);
void recovered_geometry_initial_handshake(void);
void recovered_geometry_register_clear(void);
void recovered_geometry_auxiliary_submit_select(void);
void recovered_geometry_buffer_and_batch_chain(void);
void recovered_geometry_pipeline_startup(recovered_geometry_u32 mode);

#endif

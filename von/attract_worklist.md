# Attract Reconstruction Worklist

- Observed direct-call units: 262
- Modeled integration queue: 85
- Integrated or validated: 9
- Untriaged: 168

| Entry | Edges | Triage | Work unit |
| --- | ---: | --- | --- |
| `0x00000a30` | 1 | modeled-integration-queue | maincpu.reset-register-stack-setup |
| `0x00001348` | 4 | modeled-integration-queue | maincpu.host-service-request |
| `0x00001380` | 2 | modeled-integration-queue | maincpu.host-interrupt-dispatch-route |
| `0x000017c8` | 4 | modeled-integration-queue | maincpu.host-interrupt-mask-update |
| `0x00001bb8` | 1 | modeled-integration-queue | maincpu.host-interrupt-initialize |
| `0x00002330` | 4 | modeled-integration-queue | maincpu.text-startup-table-copy-wrapper |
| `0x00002700` | 1 | modeled-integration-queue | maincpu.io-failure-state-reset |
| `0x00002730` | 1 | modeled-integration-queue | maincpu.io-self-test-core |
| `0x000027d8` | 13 | modeled-integration-queue | maincpu.shared-abi-tail-return-trampoline |
| `0x000028b0` | 1 | modeled-integration-queue | maincpu.io-final-setup-sequence |
| `0x00002bb0` | 2 | modeled-integration-queue | maincpu.io-input-initializer |
| `0x00002cf8` | 1 | modeled-integration-queue | maincpu.io-failure-input-sampler |
| `0x00002da0` | 1 | modeled-integration-queue | maincpu.io-controller-byte-average |
| `0x00003120` | 4 | modeled-integration-queue | maincpu.runtime-crc16-table-checksum |
| `0x00018488` | 1 | modeled-integration-queue | maincpu.host-byte-queue-initialize |
| `0x00018ab0` | 4 | modeled-integration-queue | maincpu.timing-sample-extrema-update |
| `0x0001bb90` | 6 | modeled-integration-queue | maincpu.word-expand-blocks |
| `0x0001bc20` | 3 | modeled-integration-queue | maincpu.halfword-byte-swap-copy |
| `0x0001bc90` | 1 | modeled-integration-queue | maincpu.text-video-row-transfer-plan |
| `0x0001bda0` | 2 | modeled-integration-queue | maincpu.startup-asset-transfer-plan |
| `0x0001c220` | 2 | modeled-integration-queue | maincpu.video-control-bootstrap-plan |
| `0x0001c618` | 8 | modeled-integration-queue | maincpu.text-video-initialize |
| `0x0001c730` | 1 | modeled-integration-queue | maincpu.video-byte-lane-expand |
| `0x0001cac8` | 23 | modeled-integration-queue | maincpu.text-position-state |
| `0x0001cc40` | 2 | modeled-integration-queue | maincpu.text-character-output |
| `0x0001ccf8` | 7 | modeled-integration-queue | maincpu.text-tile-control-write |
| `0x0001ce00` | 1 | modeled-integration-queue | maincpu.text-alternate-two-row-glyph-plan |
| `0x0001cea0` | 1 | modeled-integration-queue | maincpu.text-alternate-two-row-glyph-plan |
| `0x0001d1b0` | 4 | modeled-integration-queue | maincpu.text-string-byte-dispatch |
| `0x0001d310` | 5 | modeled-integration-queue | maincpu.text-glyph-address-plan |
| `0x0001d9e0` | 4 | modeled-integration-queue | maincpu.text-alternate-string-font-mode |
| `0x0001da90` | 4 | modeled-integration-queue | maincpu.text-string-font-mode |
| `0x0001de80` | 4 | modeled-integration-queue | maincpu.text-tile-block-writer |
| `0x00028840` | 1 | modeled-integration-queue | maincpu.geometry-profile-dispatch |
| `0x00028b40` | 4 | modeled-integration-queue | maincpu.geometry-float-conversion-helper |
| `0x00028b80` | 1 | modeled-integration-queue | maincpu.geometry-buffer-prepare |
| `0x00028c80` | 1 | modeled-integration-queue | maincpu.geometry-command-batch-loop |
| `0x00028de8` | 7 | modeled-integration-queue | maincpu.geometry-frame-submission |
| `0x00028e88` | 1 | modeled-integration-queue | maincpu.geometry-function-command-submit |
| `0x0002a430` | 5 | modeled-integration-queue | maincpu.audio-short-delay |
| `0x0002a458` | 4 | modeled-integration-queue | maincpu.audio-queue-capacity-check |
| `0x0002a4a8` | 10 | modeled-integration-queue | maincpu.audio-queue-byte-push |
| `0x0002a4e0` | 24 | modeled-integration-queue | maincpu.audio-command-u16-send |
| `0x0002a5f0` | 7 | modeled-integration-queue | maincpu.audio-command-u16-send-when-idle |
| `0x0002a870` | 1 | modeled-integration-queue | maincpu.audio-selector-zero-send |
| `0x0002a8a0` | 1 | modeled-integration-queue | maincpu.audio-scsp-queue-initialize |
| `0x0002a990` | 3 | modeled-integration-queue | maincpu.geometry-service-submit |
| `0x0006ece0` | 15 | modeled-integration-queue | maincpu.geometry-coordinate-submit |
| `0x0006f6f0` | 5 | modeled-integration-queue | maincpu.geometry-projection-packet-core |
| `0x0006fa48` | 1 | modeled-integration-queue | maincpu.geometry-slot-pool-cursors |
| `0x0006fad8` | 1 | modeled-integration-queue | maincpu.geometry-slot-pool-cursors |
| `0x0006fb18` | 1 | modeled-integration-queue | maincpu.geometry-slot-pool-cursors |
| `0x0006fb90` | 1 | modeled-integration-queue | maincpu.geometry-record-initialization |
| `0x0006fec0` | 6 | modeled-integration-queue | maincpu.geometry-control-selector-zero-pulse |
| `0x00073508` | 20 | modeled-integration-queue | maincpu.signed-runtime-band-classifier |
| `0x00077e60` | 4 | modeled-integration-queue | maincpu.action-state-dispatcher |
| `0x000783c8` | 4 | modeled-integration-queue | maincpu.transition-action-wrapper |
| `0x00079050` | 11 | modeled-integration-queue | maincpu.shared-object-state-transition |
| `0x00079d60` | 5 | modeled-integration-queue | maincpu.secondary-object-state-transition |
| `0x0009e050` | 6 | modeled-integration-queue | maincpu.geometry-result-builder |
| `0x000bf0c0` | 15 | modeled-integration-queue | maincpu.fixed-record-last-nonempty-scan |
| `0x000c5130` | 4 | modeled-integration-queue | maincpu.object-pool-create |
| `0x000c5240` | 1 | modeled-integration-queue | maincpu.object-pool-create-constant-variant |
| `0x000c5310` | 2 | modeled-integration-queue | maincpu.object-pool-create-rebased-variant |
| `0x000c5530` | 1 | modeled-integration-queue | maincpu.object-pool-dispatch |
| `0x000c55a8` | 1 | modeled-integration-queue | maincpu.object-pool-reset |
| `0x000c5608` | 1 | modeled-integration-queue | maincpu.communication-control-reset |
| `0x000c5870` | 1 | modeled-integration-queue | maincpu.communication-board-recovery-state-machine |
| `0x000c5d48` | 1 | modeled-integration-queue | maincpu.zero-sixteen-bytes |
| `0x000c5d70` | 1 | modeled-integration-queue | maincpu.geometry-profile-packet-builder |
| `0x000c8f10` | 1 | modeled-integration-queue | maincpu.command-profile-dispatch-wrapper |
| `0x000c8f60` | 1 | modeled-integration-queue | maincpu.command-profile-advance-wrapper |
| `0x000c8fa0` | 1 | modeled-integration-queue | maincpu.command-profile-initializer |
| `0x000e1e08` | 1 | modeled-integration-queue | maincpu.video-palette-lookup-initialize |
| `0x000e1f20` | 14 | modeled-integration-queue | maincpu.video-tile-expand |
| `0x000e2040` | 7 | modeled-integration-queue | maincpu.video-tile-expand-mirrored |
| `0x000e2120` | 4 | modeled-integration-queue | maincpu.video-tile-expand-index-wrapper |
| `0x000e2130` | 1 | modeled-integration-queue | maincpu.video-asset-setup |
| `0x000e2330` | 1 | modeled-integration-queue | maincpu.video-dispatch-prefix |
| `0x000e3a10` | 6 | modeled-integration-queue | maincpu.text-two-digit-formatter |
| `0x000f5058` | 28 | modeled-integration-queue | maincpu.runtime-random-step |
| `0x000f5100` | 9 | modeled-integration-queue | maincpu.text-general-formatter-boundary |
| `0x000f5190` | 1 | modeled-integration-queue | maincpu.text-general-formatter-boundary |
| `0x000f5c58` | 4 | modeled-integration-queue | maincpu.runtime-byte-compare |
| `0x000f5d40` | 10 | modeled-integration-queue | maincpu.memory-copy-forward |
| `0x00027e50` | 3 | integrated-validation-queue | maincpu.texture-decompressor |
| `0x00028120` | 1 | integrated-validation-queue | maincpu.texture-loader-profile-setup |
| `0x00028418` | 1 | integrated-validation-queue | maincpu.geometry-initial-handshake |
| `0x00028548` | 1 | integrated-validation-queue | maincpu.texture-initializer |
| `0x00028620` | 1 | integrated-validation-queue | maincpu.geometry-program-upload |
| `0x00028c08` | 1 | integrated-validation-queue | maincpu.geometry-batch-submit |
| `0x00028d08` | 1 | integrated-validation-queue | maincpu.geometry-register-clear |
| `0x00028d30` | 3 | integrated-validation-queue | maincpu.geometry-auxiliary-submit-select |
| `0x00028d80` | 1 | integrated-validation-queue | maincpu.geometry-pipeline-startup |
| `0x00002040` | 1 | untriaged |  |
| `0x00002080` | 2 | untriaged |  |
| `0x000022f0` | 2 | untriaged |  |
| `0x00002440` | 1 | untriaged |  |
| `0x00002850` | 1 | untriaged |  |
| `0x00002990` | 2 | untriaged |  |
| `0x00002c70` | 1 | untriaged |  |
| `0x00002cb0` | 1 | untriaged |  |
| `0x00002d60` | 1 | untriaged |  |
| `0x000034c0` | 1 | untriaged |  |
| `0x00003540` | 1 | untriaged |  |
| `0x00003a38` | 2 | untriaged |  |
| `0x00003ae0` | 1 | untriaged |  |
| `0x00003ba0` | 1 | untriaged |  |
| `0x000183b8` | 1 | untriaged |  |
| `0x00018438` | 1 | untriaged |  |
| `0x00018538` | 1 | untriaged |  |
| `0x000186c0` | 1 | untriaged |  |
| `0x000186f0` | 1 | untriaged |  |
| `0x00018918` | 1 | untriaged |  |
| `0x00018960` | 1 | untriaged |  |
| `0x00018a10` | 1 | untriaged |  |
| `0x0001c2c0` | 1 | untriaged |  |
| `0x0001cbb8` | 1 | untriaged |  |
| `0x0001d090` | 1 | untriaged |  |
| `0x0001d1d0` | 1 | untriaged |  |
| `0x0001d210` | 2 | untriaged |  |
| `0x0001d570` | 3 | untriaged |  |
| `0x0001d880` | 2 | untriaged |  |
| `0x0001dc10` | 1 | untriaged |  |
| `0x0001dc90` | 1 | untriaged |  |
| `0x0001dd10` | 1 | untriaged |  |
| `0x0001df00` | 1 | untriaged |  |
| `0x0001df70` | 2 | untriaged |  |
| `0x0001e030` | 1 | untriaged |  |
| `0x0001ef70` | 1 | untriaged |  |
| `0x0001f010` | 3 | untriaged |  |
| `0x0001f060` | 1 | untriaged |  |
| `0x0001f0d0` | 1 | untriaged |  |
| `0x00020210` | 1 | untriaged |  |
| `0x000226b0` | 1 | untriaged |  |
| `0x00023670` | 2 | untriaged |  |
| `0x00023ce8` | 1 | untriaged |  |
| `0x00025040` | 1 | untriaged |  |
| `0x00027550` | 2 | untriaged |  |
| `0x000281f0` | 1 | untriaged |  |
| `0x000282e0` | 1 | untriaged |  |
| `0x000284b8` | 1 | untriaged |  |
| `0x000292d8` | 2 | untriaged |  |
| `0x000294b0` | 2 | untriaged |  |
| `0x000295d0` | 2 | untriaged |  |
| `0x000296d0` | 1 | untriaged |  |
| `0x00029738` | 1 | untriaged |  |
| `0x00029778` | 1 | untriaged |  |
| `0x00029a80` | 1 | untriaged |  |
| `0x00029ae8` | 1 | untriaged |  |
| `0x00029b20` | 1 | untriaged |  |
| `0x00029c08` | 1 | untriaged |  |
| `0x00029ca0` | 1 | untriaged |  |
| `0x00029d50` | 1 | untriaged |  |
| `0x0002b430` | 1 | untriaged |  |
| `0x0002be30` | 1 | untriaged |  |
| `0x0002d9a0` | 1 | untriaged |  |
| `0x0002e1c8` | 1 | untriaged |  |
| `0x0002e1e8` | 1 | untriaged |  |
| `0x00032810` | 1 | untriaged |  |
| `0x000371e0` | 1 | untriaged |  |
| `0x0003ecd0` | 1 | untriaged |  |
| `0x0003ed60` | 1 | untriaged |  |
| `0x0003ef50` | 1 | untriaged |  |
| `0x0003f4e8` | 2 | untriaged |  |
| `0x00041f20` | 1 | untriaged |  |
| `0x000423a8` | 1 | untriaged |  |
| `0x0006ede0` | 2 | untriaged |  |
| `0x0006f600` | 1 | untriaged |  |
| `0x0006f908` | 1 | untriaged |  |
| `0x0006f9e8` | 1 | untriaged |  |
| `0x00072c10` | 1 | untriaged |  |
| `0x00072ea0` | 1 | untriaged |  |
| `0x00073498` | 1 | untriaged |  |
| `0x000735d0` | 1 | untriaged |  |
| `0x00074860` | 1 | untriaged |  |
| `0x00074e60` | 1 | untriaged |  |
| `0x00075200` | 1 | untriaged |  |
| `0x00075d90` | 1 | untriaged |  |
| `0x000761b0` | 2 | untriaged |  |
| `0x00076590` | 1 | untriaged |  |
| `0x00076b00` | 1 | untriaged |  |
| `0x00077470` | 1 | untriaged |  |
| `0x000778b0` | 2 | untriaged |  |
| `0x00077c40` | 1 | untriaged |  |
| `0x00077de0` | 1 | untriaged |  |
| `0x00077e20` | 2 | untriaged |  |
| `0x00078090` | 2 | untriaged |  |
| `0x00078408` | 1 | untriaged |  |
| `0x000784c8` | 2 | untriaged |  |
| `0x000786d0` | 4 | untriaged |  |
| `0x00078818` | 1 | untriaged |  |
| `0x00078bd8` | 1 | untriaged |  |
| `0x00078dd0` | 1 | untriaged |  |
| `0x00079630` | 1 | untriaged |  |
| `0x00079c10` | 1 | untriaged |  |
| `0x0007a318` | 1 | untriaged |  |
| `0x0007a3e0` | 2 | untriaged |  |
| `0x0007a9f0` | 2 | untriaged |  |
| `0x0007b430` | 1 | untriaged |  |
| `0x0007bf10` | 1 | untriaged |  |
| `0x0007d1f0` | 2 | untriaged |  |
| `0x0007d670` | 1 | untriaged |  |
| `0x0007dcc0` | 1 | untriaged |  |
| `0x0007e390` | 1 | untriaged |  |
| `0x0007ea10` | 1 | untriaged |  |
| `0x0007f4d0` | 1 | untriaged |  |
| `0x0007fca0` | 1 | untriaged |  |
| `0x0007ff40` | 1 | untriaged |  |
| `0x00080710` | 1 | untriaged |  |
| `0x000807d0` | 1 | untriaged |  |
| `0x000810d0` | 1 | untriaged |  |
| `0x00081120` | 1 | untriaged |  |
| `0x00081610` | 1 | untriaged |  |
| `0x00081b30` | 1 | untriaged |  |
| `0x00081e60` | 2 | untriaged |  |
| `0x00081f60` | 1 | untriaged |  |
| `0x00082040` | 1 | untriaged |  |
| `0x00082650` | 1 | untriaged |  |
| `0x00082800` | 1 | untriaged |  |
| `0x00082ae0` | 1 | untriaged |  |
| `0x00083110` | 1 | untriaged |  |
| `0x00083ac0` | 1 | untriaged |  |
| `0x00086240` | 1 | untriaged |  |
| `0x000866c0` | 1 | untriaged |  |
| `0x000881b8` | 1 | untriaged |  |
| `0x0008d400` | 1 | untriaged |  |
| `0x0008d5d0` | 1 | untriaged |  |
| `0x0008dd40` | 2 | untriaged |  |
| `0x0008dfc0` | 2 | untriaged |  |
| `0x0009b288` | 1 | untriaged |  |
| `0x0009b308` | 1 | untriaged |  |
| `0x0009b320` | 1 | untriaged |  |
| `0x0009b498` | 1 | untriaged |  |
| `0x0009c050` | 1 | untriaged |  |
| `0x0009de50` | 3 | untriaged |  |
| `0x0009e250` | 3 | untriaged |  |
| `0x0009e650` | 1 | untriaged |  |
| `0x0009e880` | 1 | untriaged |  |
| `0x0009eab0` | 1 | untriaged |  |
| `0x000bd5a8` | 1 | untriaged |  |
| `0x000bd6b8` | 1 | untriaged |  |
| `0x000bd730` | 1 | untriaged |  |
| `0x000bd810` | 1 | untriaged |  |
| `0x000bd8e0` | 1 | untriaged |  |
| `0x000be1f0` | 1 | untriaged |  |
| `0x000bece0` | 1 | untriaged |  |
| `0x000bedf0` | 1 | untriaged |  |
| `0x000beee0` | 1 | untriaged |  |
| `0x000befd0` | 1 | untriaged |  |
| `0x000bf2f0` | 1 | untriaged |  |
| `0x000de670` | 1 | untriaged |  |
| `0x000de990` | 1 | untriaged |  |
| `0x000df070` | 2 | untriaged |  |
| `0x000e37f0` | 1 | untriaged |  |
| `0x000e3830` | 1 | untriaged |  |
| `0x000e39c0` | 2 | untriaged |  |
| `0x000e39f0` | 2 | untriaged |  |
| `0x000e3a70` | 2 | untriaged |  |
| `0x000e5d30` | 1 | untriaged |  |
| `0x000e5da0` | 1 | untriaged |  |
| `0x000f50a8` | 1 | untriaged |  |

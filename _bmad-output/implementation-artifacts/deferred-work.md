- source_spec: `_bmad-output/implementation-artifacts/spec-3-1-persist-the-trained-model-and-its-metrics.md`
  summary: Warn or error when --save-model is combined with --load-model instead of silently skipping the save.
  evidence: cli.py run() load branch skips training, evaluation, and saving with no message; pre-existing behaviour, and load-path ownership sits with story 3.2.
- source_spec: `_bmad-output/implementation-artifacts/spec-3-1-persist-the-trained-model-and-its-metrics.md`
  summary: Record producing-run provenance (classifier, test-size, dataset source, timestamp) in the metrics sidecar.
  evidence: Sidecar holds only the evaluation report dict; beyond story 3.1 AC, an enhancement for debuggability.
- source_spec: `_bmad-output/implementation-artifacts/spec-4-2-attack-the-edge-cases.md`
  summary: Harden dataset loading against malformed files (empty file, single column, all-invalid labels, BOM encoding) with actionable errors.
  evidence: Beyond story 4.2 ACs (which cover missing files only); blind review noted pandas would surface raw errors for these shapes.

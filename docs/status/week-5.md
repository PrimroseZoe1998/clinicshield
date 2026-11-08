# Week 5 status

## Done

November 8: exports, PDF, guided flow, findings table and wording checkpoint
e83df4f pushed; green CI reported by the user. Exercised sample paths verified.
Reading screen covers 56 prose blocks; technical-text exceptions and human
comprehension/timed-user checks remain documented in ../readability-review.md.

Docker packaging prepared locally: Python 3.13 image, existing pinned dependencies,
non-root user, allowlisted build context, health check and run guide. New
ClinicShield container workflow builds the image, checks offline sample scores
and exports, then verifies Streamlit startup. No registry publishing. See
../docker.md.

Validation: workflow YAML, Python smoke-script syntax and Docker JSON commands
checked; 33 sample/export/PDF tests passed. Changed-script medium/high Bandit and
diff checks passed. No container build/run, commit, push or new CI claimed.

## Next

Save/push packaging and check both existing checks and the new container workflow.
Verify a sample in a running container. Continue ownership/hosting prerequisites
and timed first-time-user/comprehension checks.

## Blocked

Docker CLI/Desktop is absent locally. Container and clean-machine benchmarks
remain pending the Docker-equipped runner. Week 3 framework gaps and repository
ownership before deployment remain unresolved.

## Ask

Week 4 LinkedIn publication remains unconfirmed.

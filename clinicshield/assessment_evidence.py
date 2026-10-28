from dataclasses import dataclass, field
from datetime import timedelta
from types import MappingProxyType
from typing import Mapping

from clinicshield.application_evidence import ApplicationSupportEvidence
from clinicshield.credential_evidence import DefaultPasswordEvidence
from clinicshield.epss_cache import EpssSnapshot
from clinicshield.kev_cache import KevSnapshot
from clinicshield.lifecycle_evidence import LifecycleEvidence
from clinicshield.segmentation_evidence import MedicalSeparationEvidence
from clinicshield.vulnerability_evidence import VulnerabilityEvidence


@dataclass(frozen=True)
class AssessmentFreshnessPolicy:
    administrator_observation_max_age: timedelta
    public_feed_max_age: timedelta = timedelta(days=8)

    def __post_init__(self):
        for value in (
            self.administrator_observation_max_age,
            self.public_feed_max_age,
        ):
            if not isinstance(value, timedelta) or value <= timedelta(0):
                raise ValueError("Freshness limits must be positive durations.")


@dataclass(frozen=True)
class AssessmentEvidence:
    os_support: Mapping[str, LifecycleEvidence] = field(default_factory=dict)
    application_support: Mapping[
        str, ApplicationSupportEvidence
    ] = field(default_factory=dict)
    default_passwords: Mapping[
        str, DefaultPasswordEvidence
    ] = field(default_factory=dict)
    medical_separation: Mapping[
        str, MedicalSeparationEvidence
    ] = field(default_factory=dict)
    vulnerabilities: Mapping[
        str, tuple[VulnerabilityEvidence, ...]
    ] = field(default_factory=dict)
    kev_snapshot: KevSnapshot | None = None
    epss_snapshot: EpssSnapshot | None = None

    def __post_init__(self):
        for name in (
            "os_support",
            "application_support",
            "default_passwords",
            "medical_separation",
        ):
            object.__setattr__(
                self,
                name,
                MappingProxyType(dict(getattr(self, name))),
            )

        object.__setattr__(
            self,
            "vulnerabilities",
            MappingProxyType({
                key: tuple(records)
                for key, records in self.vulnerabilities.items()
            }),
        )
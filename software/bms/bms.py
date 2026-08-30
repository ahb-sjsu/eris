"""Eris software BMS core: per-bank state from voltage-first sensing.

Judgment layer for flooded lead-acid starting banks. Consumes samples,
maintains per-bank state, emits derived values and alarms. No hardware
assumptions beyond: bank voltage, optional midpoint voltage, optional
temperature, engine-run flag for the bank's consumers.

Thresholds mirror software/bms/README.md and are starting points; tune
against the boat's own history.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field

# Flooded lead-acid 24 V bank: rested OCV -> SoC (linear segments).
OCV_SOC = [(25.4, 1.00), (25.1, 0.90), (24.9, 0.80), (24.4, 0.70),
           (24.1, 0.60), (23.9, 0.50), (23.5, 0.30), (23.0, 0.10)]
REST_S = 4 * 3600           # rest needed before OCV is trusted
LOW_WARN_V, LOW_ALARM_V = 24.4, 23.8
IMBALANCE_V = 0.35
CHARGE_FAIL_V, CHARGE_FAIL_AFTER_S = 26.0, 300
SAG_TREND_V, SAG_BASELINE_N = 0.8, 20


def soc_from_ocv(v: float) -> float:
    """Rested open-circuit voltage to state of charge, clamped [0, 1]."""
    if v >= OCV_SOC[0][0]:
        return 1.0
    if v <= OCV_SOC[-1][0]:
        return max(0.0, OCV_SOC[-1][1] * v / OCV_SOC[-1][0])
    for (v1, s1), (v2, s2) in zip(OCV_SOC, OCV_SOC[1:]):
        if v2 <= v <= v1:
            return s2 + (s1 - s2) * (v - v2) / (v1 - v2)
    return 0.0


@dataclass
class CrankEvent:
    t: float
    min_v: float
    recovery_s: float
    temp_k: float | None


@dataclass
class BankState:
    name: str
    shared: bool = False          # generator bank: alarms escalate
    last_v: float = 0.0
    last_t: float = 0.0
    rest_since: float | None = None
    engine_on_since: float | None = None
    soc: float | None = None
    cranks: list[CrankEvent] = field(default_factory=list)
    # live crank capture
    _crank_buf: list[tuple[float, float]] = field(default_factory=list)
    _cranking: bool = False

    # ---- sample ingestion -------------------------------------------------
    def sample(self, t: float, v: float, midpoint_v: float | None = None,
               engine_on: bool = False, temp_k: float | None = None) -> list[dict]:
        alarms: list[dict] = []
        # rest tracking: any engine activity or big dV/dt resets rest
        if engine_on or (self.last_v and abs(v - self.last_v) > 0.05):
            self.rest_since = None
        elif self.rest_since is None:
            self.rest_since = t

        # engine-on bookkeeping (charge verification)
        if engine_on and self.engine_on_since is None:
            self.engine_on_since = t
            self._cranking = True
            self._crank_buf = []
        elif not engine_on:
            self.engine_on_since = None

        # cranking capture: buffer until voltage recovers above 24 V
        if self._cranking:
            self._crank_buf.append((t, v))
            if v > 24.0 and len(self._crank_buf) >= 3:
                lo_t, lo_v = min(self._crank_buf, key=lambda p: p[1])
                self.cranks.append(CrankEvent(
                    t=lo_t, min_v=lo_v, recovery_s=t - lo_t, temp_k=temp_k))
                self._cranking = False
                alarms += self._check_sag_trend()

        # rested SoC
        if self.rest_since is not None and t - self.rest_since >= REST_S:
            self.soc = soc_from_ocv(v)
            if v < LOW_ALARM_V:
                alarms.append(self._alarm("LOW_VOLTS", "alarm", v=v))
            elif v < LOW_WARN_V:
                alarms.append(self._alarm("LOW_VOLTS", "warn", v=v))

        # series imbalance
        if midpoint_v is not None and abs(midpoint_v - v / 2) > IMBALANCE_V:
            alarms.append(self._alarm(
                "IMBALANCE", "warn", midpoint=midpoint_v, half=round(v / 2, 2)))

        # charge verification
        if (self.engine_on_since is not None and not self._cranking
                and t - self.engine_on_since > CHARGE_FAIL_AFTER_S
                and v < CHARGE_FAIL_V):
            alarms.append(self._alarm("CHARGE_FAIL", "alarm", v=v))

        self.last_v, self.last_t = v, t
        return alarms

    # ---- helpers ----------------------------------------------------------
    def _check_sag_trend(self) -> list[dict]:
        if len(self.cranks) < SAG_BASELINE_N + 1:
            return []
        baseline = statistics.median(
            e.min_v for e in self.cranks[-(SAG_BASELINE_N + 1):-1])
        latest = self.cranks[-1].min_v
        if baseline - latest > SAG_TREND_V:
            return [self._alarm("SAG_TREND", "advisory",
                                latest=round(latest, 2),
                                baseline=round(baseline, 2))]
        return []

    def _alarm(self, code: str, severity: str, **data) -> dict:
        if self.shared and severity != "advisory":
            severity = "alarm"          # shared gen bank: escalate
            data["shared_bank"] = True
        return {"bank": self.name, "code": code, "severity": severity, **data}


def make_banks() -> dict[str, BankState]:
    return {
        "mainPort": BankState("mainPort"),
        "mainStarboard": BankState("mainStarboard"),
        "generators": BankState("generators", shared=True),
    }

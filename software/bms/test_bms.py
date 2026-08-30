"""Synthetic-data tests for the BMS core. Run: python -m pytest test_bms.py"""
import bms


def test_soc_table_monotone():
    vs = [23.0 + i * 0.05 for i in range(50)]
    socs = [bms.soc_from_ocv(v) for v in vs]
    assert all(b >= a for a, b in zip(socs, socs[1:]))
    assert bms.soc_from_ocv(25.4) == 1.0
    assert abs(bms.soc_from_ocv(24.4) - 0.70) < 0.01


def test_rested_soc_and_low_volts():
    b = bms.BankState("mainPort")
    alarms = []
    # 5 hours at rest, weak battery
    for i in range(0, 5 * 3600, 60):
        alarms += b.sample(t=i, v=23.9)
    assert b.soc is not None and abs(b.soc - 0.50) < 0.02
    # 23.9 V rested: below warn (24.4), above alarm (23.8) -> warn
    lv = [a for a in alarms if a["code"] == "LOW_VOLTS"]
    assert lv and all(a["severity"] == "warn" for a in lv)


def test_crank_capture_and_sag_trend():
    b = bms.BankState("mainStarboard")
    t = 0.0
    def crank(min_v):
        nonlocal t
        b.sample(t, 25.0, engine_on=True)          # start begins
        for v in (24.2, min_v, 23.9, 24.6, 26.5):  # sag and recover
            t += 0.1
            b.sample(t, v, engine_on=True)
        t += 600
        b.sample(t, 25.2, engine_on=False)         # shutdown, rest
        t += 5 * 3600
    for _ in range(21):
        crank(22.8)                                 # healthy baseline
    assert len(b.cranks) == 21
    crank(21.7)                                     # degraded start
    assert len(b.cranks) == 22
    trend = b._check_sag_trend()
    assert trend and trend[0]["code"] == "SAG_TREND"


def test_imbalance_detects_failing_series_partner():
    b = bms.BankState("mainPort")
    alarms = b.sample(t=0, v=24.8, midpoint_v=11.9)   # 12.9/11.9 split
    assert any(a["code"] == "IMBALANCE" for a in alarms)
    alarms = b.sample(t=1, v=24.8, midpoint_v=12.4)   # healthy split
    assert not any(a["code"] == "IMBALANCE" for a in alarms)


def test_charge_fail_after_start():
    b = bms.BankState("mainPort")
    b.sample(0, 25.0, engine_on=True)
    for v in (24.0, 23.5, 24.5, 26.8):               # crank + recovery
        b.sample(1, v, engine_on=True)
    alarms = b.sample(400, 25.0, engine_on=True)      # 400 s in, still low
    assert any(a["code"] == "CHARGE_FAIL" for a in alarms)


def test_shared_bank_escalates():
    b = bms.BankState("generators", shared=True)
    alarms = b.sample(t=0, v=24.8, midpoint_v=11.8)
    a = next(a for a in alarms if a["code"] == "IMBALANCE")
    assert a["severity"] == "alarm" and a.get("shared_bank")

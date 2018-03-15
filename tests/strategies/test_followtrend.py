#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_followtrend
----------------------------------

Tests for `cointrader.indicators` module.
"""


def test_monoton_raising():
    """Monoton raising chart. State is still in in initial phase.
    Therefor no signal is emitted"""
    from cointrader.indicators import followtrend
    chart1 = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9)]
    signal = followtrend(chart1)
    assert signal.value == 0


def test_monoton_falling():
    """Monoton falling chart.  State is still in in initial phase.
    Therefor no signal is emitted"""
    from cointrader.indicators import followtrend
    chart1 = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9)]
    chart1.reverse()
    signal = followtrend(chart1)
    assert signal.value == 0


def test_localmin_found():
    """Test initial phase. After reaching a local minimum no local
    maximum has been found yet. No signal is emitted. We are still
    waiting for entering the correction phase"""
    from cointrader.indicators import followtrend
    chart = [(0, 9), (0, 8), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1), (0, 2), (0, 4), (0, 5)]
    signal = followtrend(chart)
    assert signal.value == 0


def test_localmax_found():
    """Test initial phase. After reaching a local maximum no local
    minimum has been found yet. No signal is emitted. We are still
    waiting for entering the correction phase"""
    from cointrader.indicators import followtrend
    chart = [(0, 1), (0, 2), (0, 5), (0, 7), (0, 8), (0, 7), (0, 6), (0, 5), (0, 4)]
    signal = followtrend(chart)
    assert signal.value == 0


def test_raising_correction():
    """Test correction phase. After reaching a local maximum and local
    minimum we are in correction phase. No signal is emitted. We are still
    waiting for crossing the last maximum."""
    from cointrader.indicators import followtrend
    chart = [(0, 1), (0, 2), (0, 5), (0, 4), (0, 3), (0, 4), (0, 3), (0, 4), (0, 3)]
    signal = followtrend(chart)
    assert signal.value == 0


def test_falling_correction():
    """Test correction phase. After reaching a local maximum and local
    minimum we are in correction phase. No signal is emitted. We are still
    waiting for crossing the last minimum."""
    from cointrader.indicators import followtrend
    chart = [(0, 9), (0, 7), (0, 5), (0, 1), (0, 2), (0, 3), (0, 6), (0, 2), (0, 3), (0, 2), (0, 3)]
    signal = followtrend(chart)
    assert signal.value == 0


def test_raising_buy_signal():
    """Test correction phase. After reaching a local maximum and local
    minimum we are in correction phase. At the end the local max is
    exeeded and a BUY signal is emitted"""
    from cointrader.indicators import followtrend
    chart = [(0, 1), (0, 2), (0, 5), (0, 4), (0, 3), (0, 4), (0, 3), (0, 4), (0, 3), (0, 5), (0, 6)]
    signal = followtrend(chart)
    assert signal.value == 1


def test_raising_sell_signal():
    """Test correction phase. After reaching a local maximum and local
    minimum we are in correction phase. At the end the local min is
    exeeded and a SELL signal is emitted"""
    from cointrader.indicators import followtrend
    chart = [(0, 1), (0, 2), (0, 5), (0, 4), (0, 3), (0, 4), (0, 3), (0, 4), (0, 3), (0, 1), (0, 0)]
    signal = followtrend(chart)
    assert signal.value == -1


def test_falling_buy_signal():
    """Test correction phase. After reaching a local maximum and local
    minimum we are in correction phase and the end the local max is
    exeeded and a BUY signal is emitted."""
    from cointrader.indicators import followtrend
    chart = [(0, 9), (0, 8), (0, 5), (0, 6), (0, 7), (0, 6), (0, 5), (0, 6), (0, 11), (0, 12), (0, 12)]
    signal = followtrend(chart)
    assert signal.value == 1


def test_falling_sell_signal():
    """Test correction phase. After reaching a local maximum and local
    minimum we are in correction phase and the end the local min is
    exeeded and a SELL signal is emitted."""
    from cointrader.indicators import followtrend
    chart = [(0, 9), (0, 8), (0, 5), (0, 6), (0, 7), (0, 6), (0, 5), (0, 6), (0, 1), (0, 0), (0, 0)]
    signal = followtrend(chart)
    assert signal.value == -1

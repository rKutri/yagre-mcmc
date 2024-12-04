import pytest
import numpy as np

from yagremcmc.chain.transition import TransitionData
from yagremcmc.parameter.scalar import ScalarParameter
from yagremcmc.chain.diagnostics import *


@pytest.mark.parametrize("testLag", [5, 500, 50000])
def test_acceptance_rate_diagnostics(testLag):
    """
    Test AcceptanceRateDiagnostics for global and rolling acceptance rates.
    """
    diagnostics = AcceptanceRateDiagnostics()
    diagnostics.lag = testLag

    # Create transition data with alternating ACCEPTED and REJECTED
    transitions = [TransitionData(state=None, outcome=outcome) for outcome in (
        [TransitionData.ACCEPTED] * testLag + [TransitionData.REJECTED] * testLag)]

    for t in transitions:
        diagnostics.process(t)

    expectedRate = 0.5
    assert np.isclose(diagnostics.global_acceptance_rate(), expectedRate)

    diagnostics.clear()
    assert diagnostics._decisions == []


@pytest.mark.parametrize("paramDim",
                         [(10, 1),
                          (10, 3),
                          (1000, 5),
                          (100000, 100),
                          (100000, 1000)])
def test_moment_diagnostics(paramDim):
    """
    Test WelfordAccumulator against NumPy implementations of mean and variance.
    """
    diagnostics = WelfordAccumulator()

    stateVectors = [np.random.randn(paramDim[1]) for _ in range(paramDim[0])]

    for vector in stateVectors:
        transitionData = TransitionData(state=ScalarParameter(
            vector), outcome=TransitionData.ACCEPTED)
        diagnostics.process(transitionData)

    computedMean = diagnostics.mean()
    computedVar = diagnostics.marginal_variance()

    # Compute expected results using NumPy
    expectedMean = np.mean(stateVectors, axis=0)
    expectedVar = np.var(stateVectors, axis=0, ddof=1)

    # Assertions
    assert np.allclose(computedMean, expectedMean), \
        f"mean mismatch: {computedMean} vs. {expectedMean}"
    assert np.allclose(computedVar, expectedVar), \
        f"variance mismatch: {computedVar} vs. {expectedVar}"

    diagnostics.clear()


if __name__ == "__main__":
    pytest.main()

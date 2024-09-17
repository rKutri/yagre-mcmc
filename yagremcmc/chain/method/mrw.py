from numpy import exp
from yagremcmc.chain.proposal import ProposalMethod
from yagremcmc.chain.metropolisHastings import MetropolisHastings, UnnormalisedPosterior
from yagremcmc.chain.builder import ChainBuilder
from yagremcmc.statistics.parameterLaw import Gaussian


class MRWProposal(ProposalMethod):

    def __init__(self, proposalCov):

        super().__init__()

        self.cov_ = proposalCov

        self.proposalLaw_ = None

    def set_state(self, newState):

        self._state = newState
        self.proposalLaw_ = Gaussian(self._state, self.cov_)

    def generate_proposal(self):

        if self._state is None:
            raise ValueError(
                "Trying to generate proposal with undefined state")

        return self.proposalLaw_.generate_realisation()


class MetropolisedRandomWalk(MetropolisHastings):

    def __init__(self, targetDensity, proposalCov):

        proposalMethod = MRWProposal(proposalCov)

        super().__init__(targetDensity, proposalMethod)

    def _acceptance_probability(self, proposal, state):

        # proposal is symmetric
        densityRatio = exp(self._tgtDensity.evaluate_log(proposal)
                           - self._tgtDensity.evaluate_log(state))

        return densityRatio if densityRatio < 1. else 1.


class MRWBuilder(ChainBuilder):

    def __init__(self):

        super().__init__()
        self._proposalCov = None

    @property
    def proposalCovariance(self):
        return self._proposalCov

    @proposalCovariance.setter
    def proposalCovariance(self, covariance):
        self._proposalCov = covariance

    def build_from_model(self) -> MetropolisHastings:

        self._validate_parameters()

        targetDensity = UnnormalisedPosterior(self._bayesModel)

        return MetropolisedRandomWalk(targetDensity, self._proposalCov)

    def build_from_target(self) -> MetropolisHastings:

        self._validate_parameters()

        return MetropolisedRandomWalk(self._explicitTarget, self._proposalCov)

    def _validate_parameters(self) -> None:

        if self._proposalCov is None:
            raise ValueError("Proposal Covariance not set for MRW")
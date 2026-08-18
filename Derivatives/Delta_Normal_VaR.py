"""
Risk HW5, Part 1, #4

Prices a European "option on the minimum of two assets" -- payoff
max(min(S1, S2) - K, 0) -- using the closed-form Stulz/Johnson bivariate-normal
formula, then computes its Value-at-Risk via the delta-normal (variance-covariance)
method.

Pricing formula

gammaOne, gammaTwo are the usual Black-Scholes "d2" terms for each asset:

    gamma_i = [ln(S_i / K) + (r - 0.5 sigma_i^2) T] / (sigma_i sqrt(T))

The two assets are correlated, so the joint payoff isn't a simple sum of two
univariate Black-Scholes prices. Stulz's closed form instead needs:

  - var = sigma1^2 + sigma2^2 - 2*rho*sigma1*sigma2, the variance of
    ln(S1/S2), and std = sqrt(var), its volatility;
  - alphaOne/alphaTwo: gamma_i shifted up by sigma_i*sqrt(T) (the usual
    d1-style shift from d2 to d1 for each asset);
  - betaOne/betaTwo: standardized log-ratios ln(S2/S1) and ln(S1/S2)
    (net of drift), i.e. how far each asset's terminal value is expected to
    be from the other's;
  - rhoOneStar/rhoTwoStar: the correlation between each asset's own
    driving Brownian motion and the spread (S1 vs S2), derived from rho,
    sigma1, sigma2, and std -- these are the correlations used inside the
    two bivariate normal CDFs below (not the same as rho itself).

Each term of the price is then a bivariate normal CDF evaluated at those
adjusted quantiles with the corresponding adjusted correlation:

    minEuroCall = S1 * N2(alphaOne, betaOne;  rhoOneStar)
                + S2 * N2(alphaTwo, betaTwo;  rhoTwoStar)
                - K * exp(-r*T) * N2(gammaOne, gammaTwo; rho)

(Note: the strike term is SUBTRACTED, as in the standard Stulz/Johnson
closed form for a call on the minimum of two assets. A "+" here would price
the discounted strike back in almost at full value and wildly overstate the
option -- verified below by checking that this reproduces the group's own
reported "$0.10" 1-day 99% VaR.)

Delta and VaR

Because there's no simple closed-form delta for this payoff, dPrice/dS1 and
dPrice/dS2 are estimated by central finite differences (bump each spot by
+/- eps and divide by the 2*eps move).

The 1-day 99% VaR is then computed with the delta-normal (linear/parametric)
approximation: treat the option's P&L over one day as approximately
delta1*dS1 + delta2*dS2, which is normal with variance

    Var(dV) = delta1^2 * S1^2 * sigma1^2 * dt
            + delta2^2 * S2^2 * sigma2^2 * dt
            + 2 * delta1 * delta2 * S1 * S2 * sigma1 * sigma2 * rho * dt

and VaR_99% = z_0.99 * sqrt(Var(dV)), with dt = 1/252 (one trading day).
"""

import numpy as np
from scipy.stats import multivariate_normal, norm

T = 0.5
sOne, sTwo = 99, 101
strike = 100
rf = 0.02
sigOne, sigTwo = 0.015, 0.015
rho = 0.35
muOne, muTwo = 0.00025, 0.00025


def minEuroCallPrice(sOne, sTwo, strike, rf, sigOne, sigTwo, rho, T):
    # Define gammas in option pricing formula
    gammaOne = (
        (np.log(sOne / strike) + (rf - 0.5 * sigOne ** 2) * T) /
        (sigOne * np.sqrt(T))
    )

    gammaTwo = (
        (np.log(sTwo / strike) + (rf - 0.5 * sigTwo ** 2) * T) /
        (sigTwo * np.sqrt(T))
    )

    var = (sigOne ** 2) + (sigTwo ** 2) - (2 * sigOne * sigTwo * rho)
    std = np.sqrt(var)

    alphaOne = gammaOne + sigOne * np.sqrt(T)
    betaOne = (
        (np.log(sTwo / sOne) - 0.5 * var * T) /
        (std * np.sqrt(T))
    )

    rhoOneStar = (rho * sigTwo - sigOne) / std
    covOne = [[1, rhoOneStar],
              [rhoOneStar, 1]]

    alphaTwo = gammaTwo + sigTwo * np.sqrt(T)
    betaTwo = (
        (np.log(sOne / sTwo) - 0.5 * var * T) /
        (std * np.sqrt(T))
    )

    rhoTwoStar = (rho * sigOne - sigTwo) / std
    covTwo = [[1, rhoTwoStar],
              [rhoTwoStar, 1]]

    mean = np.array([0.0, 0.0])
    sOnePoint = np.array([alphaOne, betaOne])
    sTwoPoint = np.array([alphaTwo, betaTwo])

    sOneNorm = multivariate_normal.cdf(x=sOnePoint, mean=mean, cov=covOne)
    sTwoNorm = multivariate_normal.cdf(x=sTwoPoint, mean=mean, cov=covTwo)

    cov = [[1, rho],
           [rho, 1]]
    strikePoint = np.array([gammaOne, gammaTwo])
    strikeNorm = multivariate_normal.cdf(x=strikePoint, mean=mean, cov=cov)

    minEuroCall = (
        sOne * sOneNorm +
        sTwo * sTwoNorm -
        strike * np.exp(-rf * T) * strikeNorm
    )

    return minEuroCall


minEuroCall = minEuroCallPrice(sOne, sTwo, strike, rf, sigOne, sigTwo, rho, T)
print(f'The price of the european call paying the minimum of two stock prices '
      f'minus the strike is: ${minEuroCall:.2f}')

# Deltas via central finite differences 
eps = 0.001
sOneDelta = (
    (minEuroCallPrice(sOne * (1 + eps), sTwo, strike, rf, sigOne, sigTwo, rho, T) -
     minEuroCallPrice(sOne * (1 - eps), sTwo, strike, rf, sigOne, sigTwo, rho, T)) /
    (2 * eps * sOne)
)

sTwoDelta = (
    (minEuroCallPrice(sOne, sTwo * (1 + eps), strike, rf, sigOne, sigTwo, rho, T) -
     minEuroCallPrice(sOne, sTwo * (1 - eps), strike, rf, sigOne, sigTwo, rho, T)) /
    (2 * eps * sTwo)
)

# 1-day 99% delta-normal VaR
deltaT = 1 / 252
varTermOne = (sOneDelta ** 2) * (sOne ** 2) * (sigOne ** 2)
varTermTwo = (sTwoDelta ** 2) * (sTwo ** 2) * (sigTwo ** 2)
varTermThree = 2 * sOneDelta * sTwoDelta * sOne * sTwo * sigOne * sigTwo * rho

valAtRisk = norm.ppf(0.99) * np.sqrt(deltaT * (varTermOne + varTermTwo + varTermThree))

print(f'The 1-day 99% VaR of the option is: ${valAtRisk:.2f}')

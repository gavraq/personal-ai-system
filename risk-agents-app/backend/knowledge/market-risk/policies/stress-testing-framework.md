---
title: Market Risk Stress Testing Framework
domain: market-risk
category: policies
slug: stress-testing-framework
description: Framework governing stress testing and scenario analysis for market risk, including worst-case stresses, historical event scenarios, and point-of-weakness analysis
artefact_type: framework
risk_domain: Market Risk
owner: Head of Market Risk
approval_committee: Market & Liquidity Risk Committee
approval_date: 2024-09-01
effective_date: 2024-09-01
review_date: 2024-09-01
version: "5.2"
tags: [market-risk, stress-testing, scenario-analysis, point-of-weakness, icaap]
related_artefacts:
  policies:
    - var-policy
    - market-risk-policy
  methodologies:
    - stress-scenario-methodology
    - var-methodology
  models:
    - stress-var-model
    - scenario-analysis-model
  data:
    - stress-scenario-library
    - historical-stress-events
  governance:
    - market-risk-committee-tor
    - mlrc-tor
    - rmc-tor
    - stress-forum-tor
  controls:
    - stress-loss-limit-monitoring
    - pow-stress-monitoring
  processes:
    - biweekly-stress-testing-process
    - quarterly-scenario-review-process
    - pow-stress-identification-process
  reports:
    - stress-testing-report
    - top-risks-weekly-pack
    - icaap-concentration-report
related_skills:
  - stress-testing
  - scenario-analysis
  - pow-stress-calculation
difficulty: Intermediate
reading_time: 15 min
---

# Market Risk Stress Testing Framework

## 1. Introduction

### 1.1
As part of the Market Risk Policy, all risk factors are subject to stress shocks under the Market Risk Stress Framework, to determine loss vulnerabilities in the trading portfolio under market stress moves. Stress testing is performed on a bi-weekly basis with functionality to run stress testing daily if required.

### 1.2
In addition to individual risk factor stress measures, the trading book of ICBC Standard Bank Plc ("ICBCS") and particular sub-portfolios thereof are subject to stress testing and scenario analysis, i.e. combinations of extreme moves across a range of risk factors.

The portfolio stress scenarios are a key market risk control that work in conjunction with the value-at-risk (VaR) measure to loss vulnerabilities on the trading book. Market Risk scenario stresses, unlike VaR which is a historical simulation calculation methodology, are blunt shocks applied to all risk factors in the trading portfolios.

### 1.3
Typically Stress scenario exposures differ from VaR exposures in that the shock parameters can be forward-looking (i.e. they are not confined to loss returns associated with past market events). Stress Scenarios deliberately target the "tail" aspect of the trading risk which is beyond the VaR frontier exposure loss of 99% confidence interval.

## 2. Scope

### 2.1
The bank's programme of stress testing includes all traded linear and non-linear products and considers the following:
- Concentration risk
- liquidity horizons on position exit across all asset classes in stressed market conditions
- One-way market behaviour
- Event and jump-to-default risks
- Asymmetry of Stress moves associated with deep out-of-the-money and onshore vs offshore positions
- Positions that are sensitive to the grouping of prices
- Other risks (if material) that may not be captured appropriately in the bank's value-at-risk model e.g. recovery rate uncertainty, implied correlations and certain volatility skew risks

The stress shocks applied to individual risk factors must reflect the nature of the underlying portfolios and the time it could take to hedge out or manage risk under severe market conditions. Historical scenarios are calibrated to a 10d liquidity horizon exit in line with the regulatory VaR and SVaR and ICAAP market risk concentration monthly risk assessments.

### 2.2
Market Risk is responsible on a quarterly basis to assess Net (outright risk), Curve (tenor impact) and Basis risk impact(i.e.g. Bond swap, Futures vs Physical, Onshore/Offshore currency spot rate risk) in the trading portfolio. Such positions should be incorporated into the relevant Stress scenario(s) or if no new positions are identified on a quarterly basis, then this should be attested to.

### 2.3
Market Risk is responsible for identifying market risk stress scenarios that highlight underlying risk factors to seek out vulnerabilities to the trading portfolio. Scenarios used must be appropriate to test the effect of adverse movements in market volatilities with considerations to correlated impacts across other key positions in competing asset classes, as well as the effect of any change in the assumptions underlying the bank's value-at-risk model. The results of the bank's Market risk stress testing and scenario analysis must be reviewed by management and is an intrinsic Level 1 limit that supports the bank's Risk Appetite Framework.

## 3. Types of Market Risk Stress

### 3.1 "Worst-Case" Stresses

#### 3.1.1
The "worst-case" base case stress loss attributable to the bank's trading book (Global Markets) is the greatest loss produced by each day's 1-day or 10-day VaR or SVaR formats. This measure, by definition, includes all severe market events and disruptions during the historical observation period.

#### 3.1.2
Market Risk consult in with Business to determine stress scenario parameters but ultimately the changes are at the discretion of Market risk to interpret these simulations for the purposes of monitoring the bank's stress loss estimations. This can include selection of the most appropriate window (stress or historic), holding period or portfolio aggregation level.

#### 3.1.3
Working of the VaR and the VaR methodology can be found in the Bank's VaR Methodology and Value at Risk policies.

### 3.2 Severe Historical Event Stresses

#### 3.2.1
Severe historical events are those outside the historical observation period that underlies the bank's VaR measures.

---

<!-- Page 3 -->

# Market Risk Stress Testing Procedures

### 3.3 Potential Stress Scenarios
The specific market moves associated with such an historical event may be directly applied to the bank's trading book or particular sub-portfolio thereof, but more often they are built into a potential stress scenario – see section 3.3 below.

#### 3.3.1 Potential stress scenarios are developed by Market Risk and may be based on:
- Historical events, which may include events covered by the historical data series
- Events currently considered possible thematic issues point in time (e.g. Brexit, Covid-19, Russia/Ukraine crisis and Global inflation cycle and 2008 Global Financial Crisis.)

#### 3.3.2
Findings from the Market Risk monthly ICAAP Concentration risk assessments, fortnightly Risk vs trader FIC and commodity meetings and weekly point-of -weakness stresses. In selecting potential stress scenarios, Market Risk will take account of the major risks identified by the daily risk factor exposure and stress loss measures, issuer risk exposures and country risk exposures.

### 3.4 Point-of-Weakness Stress Scenarios

#### 3.4.1
In addition to the key market risk stress testing scenarios (Pillar Stresses), which are typically top-down in scenario assessment, Market Risk perform, analysis and reporting on a weekly frequency for specific loss scenarios associated with key trading strategies (bottom up stress approach) known as Point- of -weakness (PoW) stress. The PoW stresses:
- Identify the main vulnerabilities or top risks in the trading portfolio which are most sensitive to price (implied volatility, correlation, spread, basis or any other market related information) changes weighted by their P&L impact (bottom-up approach)
- Define a set of extreme, but plausible, market price changes for the identified key trading strategies.

## 4 Stress Testing

### 4.1 Frequency & Level of Stress Testing

#### 4.1.1
Stress testing is performed on a bi-weekly basis for all traded positions residing under the Management VaR population reporting

#### 4.1.2
Market Risk is responsible for ensuring that the stress testing results above are reported to the bank's regulator in accordance with section 4.3

#### 4.1.3
Market Risk is responsible for ensuring that stress testing results cover the entire trading book are reported to senior risk and trading management and ExCo in accordance with section 4.4

### 4.2 Conduct of Stress Testing

#### 4.2.1
Market Risk is responsible for market risk stress testing.

### 4.3 Reporting of Stress Testing Results to Regulators

#### 4.3.1
Market Risk is responsible for ensuring that stress testing results cover all positions in the trading book. As part of ICBCS model permission, market risk is required to report the stress loss exposure to its regulator on a quarterly basis.

#### 4.3.2
Market Risk is also responsible for ensuring that any other "ad hoc" regulatory reporting requirements are met.

### 4.4 Reporting of Stress Testing Results to Management

#### 4.4.1
Market Risk is responsible for ensuring that stress testing results covering the entire trading book are reported to the bank's Risk Management Committee ("RMC") and its Market & Liquidity Risk sub-committee (MLRC) on a monthly basis.

#### 4.4.2
RMC is responsible for evaluating the bank's capacity to absorb market risk stress losses in accordance to the Firms Stress Risk appetite and identify steps to control or reduce the size of such risks where appropriate.

#### 4.4.3
Market Risk Stress testing results are reported weekly in the Top Risks weekly pack to senior risk, trading and Exco.

#### 4.4.4
A new Stress Forum was established Q1 2023 which focuses the stress towards a more enterprise approach across the primary risks of the firm. Market risk division is a key contributor and stakeholder. Key developments in market risk stress are tabled for discussion in this forum.

#### 4.4.5
Market Risk stress by Global markets and business decomposition and quarterly trend are reported to ICBC Head office monthly.

---

<!-- Page 4 -->

# Market Risk Stress Testing Policy Sections

## 4.5 Alignment with Group level stress testing initiatives

### 4.5.1
Market Risk may take necessary steps to align the market risk stress testing methodology and results for ICBC head office as part of the ICBC Group stress submission to comply with stress testing results.

## 4.6 Pre-Trade Scenario Analysis

### 4.6.1
Market Risk may take such steps as may be necessary to set up, modify, maintain and improve scenarios for pre-trade scenario analysis. Under the bank's swap dealer requirements, Market Risk may be requested to assist Front Office with providing pre-trade scenario analyses to its clients. These scenarios must be designed in consultation with the client.

## 5 Market Risk Stress Loss Trigger & Limits

### 5.1 Stress Loss Appetite

#### 5.1.1
The bank's Market Risk Stress Loss appetite shall be subject to the limits set in line with the Bank's Risk Appetite Statement.

### 5.2 Basis of Limits

#### 5.2.1
The max stress derived through the various stress-types described in section 2 is assigned a Level 1 Limit status and defined under the Market Risk appetite of the firm which is owned and approved at a Board level.

#### 5.2.2
Global Markets business manage the stress exposure to a Level 1 limit prescribed by Market risk in accordance with the Boards stress risk appetite. (Section 5.2.1.3 of the Market Risk Policy).

#### 5.2.3
Market Risk is responsible for monitoring exposure against these stress loss limits at least bi-weekly. Any limit breaches are dealt in accordance with limit breach management section outlined in the Market Risk Policy. (Section 3.2.4)

### 5.3 Ad Hoc Reductions in Limits

#### 5.3.1
The Stress Loss limits may be reviewed and revised at any time by appropriately authorised ICBCS risk committees or forums at any time if the Financial Stability of the Bank so requires.

### 5.4 Stress Test & Scenario Reviews

#### 5.4.1
Market Risk is responsible for identifying suitable severe historical event stresses, potential stress scenarios and Point-of-Weakness scenarios.

#### 5.4.2
Stress test scenarios are reviewed at least annually with a view to ensuring that both regularly applied scenarios and those identified 'ad hoc' (i.e. in response to prevailing market conditions or particular concentrations of risk) remain relevant and serve to identify those market events which will most hurt the bank, even if improbable.

#### 5.4.3
Market Risk will provide new or amended Point-of-Weakness scenarios or analysis of Top Risks to the MLRC on a minimum monthly basis.

#### 5.4.4
Market Risk will incorporate Basis risk scenarios into the existing Pillar Stresses as noted in Section 2.3

## 6 Exceptions

### 6.1
There are no exceptions to this Policy.

## 7 Related Policies and Standards

### 7.1
Please refer to the following related documents for further information:
- Market Risk Policy
- VaR Policy
- VaR Methodology

### 7.2
All Bank policies can be located via the Bank's Intranet Document Portal.

---

<!-- Page 5 -->

# Policy Document

## 8. Definitions

The following defined terms apply to this policy:

| Term | Definition |
|------|------------|
| Bank | Refers to ICBC Standard Bank Plc and its subsidiary entities and branches within the ICBC Standard Bank Plc Group. |

## 9. Policy Contact

| Name: | Brendan Melvin |
|-------|----------------|

## 10. Revision History

| Version No. | Purpose of revision | Review Date | Effective Date | Summary of key revision points |
|-------------|-------------------|--------------|----------------|----------------------------|
| 2.0 | Annual Review | July 2008 | Aug 2008 | Amended for changes from CapCom for the 2008 annual review |
| 3.0 | Annual review | May 2012 | Jun 2012 | Annual Review of Policy (2012) |
| 3.1 | Annual review | May 2013 | Jun 2013 | Annual Review of Policy (2013) |
| 3.2 | Annual review | Dec 2013 | Jan 2014 | Addition of Section 4.6 to reflect Dodd Frank Governance Requirements for pre-trade scenario analysis |
| 4.0 | Annual review | May 2014 | Jun 2014 | Annual Review of the Policy (2014) and amendment to permit conservative adjustments in aggregation methodology |
| 4.1 | Policy amendments | Aug 2014 | Sep 2014 | Amending Policy for Change in Control |
| 4.1 | Annual Review | May 2015 | Jun 2015 | Annual Review of Policy (2015) |
| 4.3 | Annual Review | May 2016 | Jun 2016 | Annual Review of Policy (2016) |
| 4.4 | Annual Review | May 2016 | June 2016 | Annual Review of Policy (2017) |
| 4.5 | Policy amendments | Aug 2017 | Sep 2017 | Amendments to pre-trade scenario analysis |
| 4.6 | Annual Review | Sep 2018 | Oct 2018 | Annual Review of Policy (2018) |
| 4.7 | Annual Review | Sep 2020 | Sep 2019 | Annual Review of Policy (2019) |
| 5.0 | Annual Review | Sep 2023 | Sep 22 | Annual Review of Policy |
| 5.1 | Annual Review | Sep 2023 | Sep 2023 | Annual review of policy |
| 5.2 | Annual Review | Sep 2024 | Sep 2024 | Annual review of Policy<br>Revisions for ICAAP liquidity assessments, PoW (bottom up approach) |

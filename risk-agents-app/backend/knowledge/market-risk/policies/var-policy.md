---
title: Value-At-Risk Policy
domain: market-risk
category: policies
slug: var-policy
description: Policy governing the definition, measurement, and control protocols for Value-at-Risk (VaR) and Stress VaR (SVaR) for regulatory capital and risk management purposes
artefact_type: policy
risk_domain: Market Risk
owner: Head of Market Risk
approval_committee: Market & Liquidity Risk Committee
approval_date: 2023-06-01
effective_date: 2024-08-01
review_date: 2024-08-01
version: "4.5"
tags: [market-risk, var, svar, regulatory-capital, ima, backtesting, rniv]
related_artefacts:
  methodologies:
    - var-methodology
    - historical-simulation-methodology
    - proxy-methodology
  models:
    - historical-var-model
    - stress-var-model
  data:
    - market-data-dictionary
    - var-time-series
  feeds:
    - bloomberg-market-data
    - asset-control-feeds
    - xenomorph-feeds
  governance:
    - market-risk-committee-tor
    - mlrc-tor
    - rmac-tor
  controls:
    - var-limit-monitoring
    - var-backtesting-control
    - svar-window-review
  processes:
    - daily-var-calculation-process
    - svar-window-change-process
    - proxy-assignment-process
    - rniv-identification-process
  systems:
    - murex
    - asset-control
    - xenomorph
    - vespa
related_skills:
  - var-calculation
  - stress-testing
  - backtesting-analysis
difficulty: Advanced
reading_time: 30 min
---

# Value-At-Risk Policy

[ICBC Standard Bank logo]

**Confidential**

August 2024

| Field | Value |
|-------|--------|
| Policy | Value-At-Risk Policy |
| Level | ICBC Standard Bank Plc and ICBC Standard Bank Plc Group |
| Applicability | All Staff |
| Approved by | Market Risk |
| Approval date & Committee | June 2023 Market & Liquidity Risk Committee |
| Effective date | August 2024 |
| Review date | August 2024 |
| Version | 4.5 |

*This document is strictly private and confidential and is proprietary information to ICBC Standard Bank Plc and its subsidiary entities within the ICBC Standard Bank Plc Group (the "Bank").*

*External circulation is strictly prohibited.*

www.icbcstandard.com

---

<!-- Page 2 -->

# Value-at-Risk (VaR) Policy

## 1. Introduction

The Value-at-Risk (VaR) policy is designed to provide a comprehensive outline on the definition of VaR and Stress VaR (SVaR), how they are measured and used in ICBC Standard PLC "The Bank", and the associated control protocols around time series management and model integrity which are key to effective measure for both regulatory capital and Market Risk management. Further details on the underlying VaR Model can be found in the RMA owned "VaR Methodology" document.

## 2. Value at Risk ( VaR) definition

The Value-at-Risk (VaR) is the key portfolio risk measure assigned to all trading books of ICBC Standard Bank PLC. The VaR is applied at Global markets (Level 1 exposure) and sub business levels (Level 2 exposure). The historical simulation VaR calculates an expected loss amount of a portfolio over a given time horizon based on a predefined confidence level. VaR is used for both Regulatory Capital and risk management purposes.

Regulatory Capital VaR (RVaR, IMA VAR) is the expected loss on our Global markets Portfolio based on a 10d return over the current 1yr trading horizon using a 99% confidence interval. It is the key capital metric for calculating the market risk regulatory capital for Global Markets.

Management VaR (MVaR) is the expected loss calculated on Global Markets or any sub business portfolios, based on a 1-day return over the current 1-year trading horizon using a 99% confidence interval. This is a key daily market risk management measure for risk and works in tandem with Stress testing to assess both normal and tail order portfolio risk assessment.

The VaR is a historical simulation based model, approved under the Banks IMA waiver, which in the main cases uses a full revaluation approach based on the loss calculation and aggregation of all market risk factor (the risk drivers associated with all approved traded product in the Global markets Portfolio) to produce a loss result in a USD denominated amount.

### 2.1
The Bank's VaR measure covers all material market risk factors in its trading book (as defined by the Trading Book Policy Statement) or in the Banking Book for instruments held at fair value. The VaR specifically covers the following market risk categories:
- General interest rate risk (excluding Interest Rate Risk in the Banking Book);
- Specific interest rate risk (in conjunction with interest rate general market risk which account for traded credit spread risk);
- foreign currency risk; and
- commodity risk.

### 2.2
The VaR implicitly captures the correlations between individual risk factors, both within and across Asset class categories.

## 3. Value-at-Risk (VaR) measurement

### 3.1
The RVaR calculation is the footing for the IMA VaR, while the MVaR is the key VaR for measuring portfolio exposure vs portfolio limits (Level 1 and Level 2 limits as defined in section 4 of the Market Risk Policy).

### 3.2
The Bank reports VaR with a confidence loss interval of 99%, but also uses 1% Confidence interval for positive back testing exception reporting purposes daily.

### 3.3
Risk Methodologies & Analytics (RMA) is responsible for keeping a record of the various different Value-at-Risk measures used by the Bank, including details of the agreed confidence level and holding period in each case. RMA is also responsible for specifying, justifying and documenting any techniques used to scale and aggregate all VaR measures RMA. When assumptions have a material impact, remediation must be considered if necessary via Risk not in VaR add-ons (RNiVs) or adjustments to the model.

### 3.4
Any changes to the VaR methodology (as detailed in the VaR Methodology document) need to be considered and approved, with evidence on a case by case basis by the Risk Methodologies Approval Committee (RMAC) and material changes submitted to the Market & Liquidity Risk Committee (MLRC) for noting if requested by RMAC. Risk Methodologies & Analytics must ensure that detailed documentation is maintained at all times on the VaR methodology. Market Risk is responsible for ensuring that any changes to the VaR methodology comply with the regulatory requirements under the Internal Model Approach (as defined in the Capital Requirements Regulation and Supervisory Statements) where applicable.

---
¹ Taylor Series VaR is used for Linear Rate Metals and Energy trading businesses.

---

<!-- Page 3 -->

# Market Risk Management - VaR and SVaR Procedures

### 3.5
RMA is responsible for ensuring that Model Validation is fully informed of any proposed alternatives and/or extensions to the VaR methodology. Model Validation must conduct a review of any such proposals following the standards and principles contained in the Model Validation Policy. The results of this review, together with any recommendations or caveats, must be submitted to RMAC.

### 3.6
RMA is responsible for specifying, justifying and documenting the simulation re-pricing methodology used for each product or set of products/risk factors covered by the VaR model. For example:
- Full revaluation using independently-validated pricing models (e.g. those implemented in a particular Front Office system).
- Interpolated revaluation using two-dimensional scenario grids (e.g. spot-volatility).
- Extrapolated revaluation using a Taylor series expansion based on instantaneous price derivatives (e.g. delta and gamma).

### 3.7
Market Risk and Front Office should review and sign off the VaR on a daily basis in line with agreed SLA's. Late sign offs should be reported to the Business Management & Control team.

## 4. Stress VaR (SVaR)

The SVaR is a key portfolio measure that's intrinsic to The Banks market risk regulatory capital, which was introduced as part of Basel 2.5 in response to the GFC. Similar to VaR, the SVaR is applied at Global Markets (Level 1 exposure) and sub business levels. Like VaR, the SVaR is historical simulation based and calculates an expected loss amount of a portfolio over a given time horizon based on a predefined confidence level. The defining difference is that where VaR takes the current 1-year trading horizon, the SVAR looks for the worst 1-year trading horizon window to perform its loss calculation on the portfolio which can look back to 2007.

Regulatory Capital SVaR (SVaR) is the expected loss on our Global markets Portfolio based on a 10d return over the worst 1yr trading horizon looking back to 2008, using a 99% confidence interval.

The below flow explains where SVaR fits in relation to the Market Risk regulatory calculation as part of our IMA capital requirements. VaR and SVaR are the Max (10d, 60d Average), IRC is the Max (Spot IRC, 60d Average) and RNIV.

[Table showing Market Risk Regulatory Capital calculation flow with columns for 10d VaR, 10d SVaR, IRC, 10d VaR RNV, 10d SVaR VaR RNV, Stress Test based RNV, and Modified Market Risk, all measured in USD m]

SVaR, because of its stress nature of its calculation approach to capture the worst 1-year time horizon, looking back to 2007, becomes an effective measure to complement the Banks current VaR and Stress testing loss exposures. For this reason, the SVaR measures are used beside the pillar stresses to consider worse case stress loss consideration in weekly stress loss reporting (refer to Stress Policy)

## 5. Stress VaR Window Change Process

The SVaR window is determined by a weekly monitoring process of identifying the worst 1-year window of daily historical returns associated with the current trading positions i.e. it is a look-back for the worst 1-year window since 2007. This identification process is known as the Extended Stress VaR process (ESVaR).

### 5.1
Market Risk reviews the results of the weekly ESVaR calculations and reports the results to the Head of Market Risk, CRO, business and TOM for sign off on the need for an SVaR window change. Risk change assessment justification on the SVaR window focuses on at least 3 consecutive results that point to a competing window alternative to the incumbent SVaR window. The weekly trend on the ESVaR competing windows to the current window is illustrated and discussed in every MLRC cycle.

If a window has been established, under assessment by Market Risk, to challenge an incumbent SVaR window, the Market Risk division will communicate to desk heads, Risk Methodology and Analytics, Treasury Capital Markets, CRO and Risk Change/RAV of the imminent window change to the SVaR. As a courtesy to IT Risk production run-the-bank division, and Capital reporting and forecasting, that are most impacted by the SVaR window change, Market Risk will give a minimum of a 2 week indication on the effective window change to be implemented. All changes will be formally noted in the nearest MLRC cycle.

---

<!-- Page 4 -->

# Market Risk Time Series and Proxying Process

## 5.2
Market Risk is responsible for informing the PRA of any changes in the SVAR window upon conclusion to internal Risk governance in the nearest PRA back testing quarterly reporting. Market Risk is also responsible for providing the PRA with a quarterly summary of the results of the reviews of the SVAR window.

## 6 Historical Time Series

### 6.1
The historical time series used in the Bank's VaR, SVaR and ESVaR calculations are maintained in Asset Control (FIC and Energy) and Xenomorph (Base Metals)². The historical time series used in the RVaR calculation are updated on a daily basis (i.e. on a daily basis the VaR window is rolled forward by one day with a 5-day lag to clean more recent dates).

### 6.2
The Risk Reporting, Analysis and Validation team is responsible for updating and maintaining the time series data in the systems according to parameters agreed with Market Risk and RMA. Market Risk is responsible for reviewing these parameters on at least an annual basis.

### 6.3
Where a reliable historical time series is not available for a particular risk factor, Market Risk is responsible for assigning a suitable proxy (per Proxy Methodology guidelines) and providing evidence to justify that choice. Where no suitable proxy is available or the extent of proxying is deemed too high Market Risk should notify the RAV(RTB) and RMA(new) that the risk is accounted for via an alternative VaR measurement technique (e.g. via a new or existing RNM framework).

### 6.4
Any adjustment (other than adjustments related to the cleaning of data such as backfilling missing dates) to individual time series to reflect material changes or discontinuity in market conditions requires the approval of the Head of Market Risk.

## 7 Historical Time Series Proxying Process for Fixed Income (Credit/Rates/FX) and Commodities

### 7.1 Roles and responsibilities
- RAV is responsible for the initial identification of when a proxy is first required and alerting Market Risk;
- Market Risk is responsible for determining if an existing proxy should change (e.g. due to changing market conditions);
- Market Risk is responsible for performing the analysis to identify the most appropriate proxy and to document this analysis.;
- RMA is responsible for reviewing this analysis, providing challenge to Market Risk and finally approving the proxy choice;
- Once the proxy has been approved, RAV is responsible for implementation.
- RAV is responsible for providing reporting on proxies.

### 7.2
Rates (yield curve) and Foreign Exchange risk factors are set up as part of the BAU process run by Murex via Formal Approval Request forms. At the point of set-up of a new currency or yield curve, Market Risk and Reporting Risk Analytics and Validation (RAV) ensures that the VAR/SVAR data is in place with Asset Control/Xenomorph platforms prior to the sign-off with Murex on a specific curve. RAV will share at the point of set-up using the appropriate Market label each Time series new historic opener the VAR/SVAR in place. For all markets, proxies that do not exist in the Rates & FX time series therefore – only the standard generic, specific ones of own data. All material proxies for all Rates and FX curves are highlighted at the RNM & Proxy Governance forum for complete transparency.

### 7.3
Credit products (credit aware bonds, credit default swaps) need a more dynamic proxy set-up as individual time series specific to the asset are required on an ongoing, dynamic basis. Specific (level 2) proxies that are set up at the request of Market Risk. The proxy setup process is described in Appendix 1 (Appendix 1: RAV own the Proxy Setup Process for Credit Products). Appendix 2 describes the scoring process and documented audit trail for each requested asset that is requested to be scored for each asset, this is saved by RAV to a share point website for all to be able to inspect (the final scoring is implicitly approved by Market Risk at point in time of the asset set-up and through daily VaR sign offs).

### 7.4
Any proxy requested by Market Risk will be formally scored by RAV and scoring failures will be immediately informed to Market Risk for formal approval or rationale for were the failed timeseries to be allowed to stand (e.g. volatility is explained by a particularly stressed market period).

### 7.5
Market Risk work with RAV to provide the market Risk Model Risk Management forum with visibility on the top credit bond proxied positions VAR timeseries via explicit review and rescoring as well as the top positions that use their own timeseries. The proportion of the positions investigated will be point in time and comprise at minimum the top 10 in

---
² Note a project is on-going to migrate from Asset Control to FRDM in 2024

---

<!-- Page 5 -->

# Market Risk Management Procedures

## 7.5 Portfolio Coverage and Proxy Assignment
Each category along with an explicit statement on the net portfolio coverage achieved. The minimum coverage achieved on proxied positions will be >50% of the total analysed portfolio proxied positions (unless explicitly explained to the governance forum owing to the number of bonds being involved being too great). The documentation is submitted to the forum by MR, "Appendix 3: Quarterly Scoring Report", highlights the Asset Control procedure followed. Rates and FX products have their proxy assignment formally shown at the Market Risk Model Risk Management forum with Risk Analytics commentary and materiality highlighted for each curve (Appendix 4: RNIV & Proxy Governance Forum: Rates & FX Curve).

### 7.5.1
The top proxied positions all have explicitly detailed the exact proxy currently assigned explicitly detailed to the forum. Market Risk will highlight if any such proxy has become sub-optimal (either through poor time series scoring or through better proxy being available) as part of the commentary to the forum (Appendix 4).

### 7.5.2
Asset Control have an automated process that looks to assign Proxy 1 (own timeseries) data as soon as available on an automated process.

## 7.6
For Commodities (Xenomorph) please refer to the data cleaning procedures as documented in the RAV procedures documentation (Appendix 5).

# 8 Risks Not in VaR (RNIV's)

## 8.1 Roles and Responsibilities

**Individual existing RNIV**

### 8.1.1
Market Risk has the primary responsibility for monitoring the approved scope of an RNIV and to escalate to Risk Methodologies & Analytics (RMA) to provide secondary challenge as a result of for example risk factor or product scope changes.

**Family of existing RNIV**

### 8.1.2
Market Risk has the primary responsibility for monitoring the approved scope of all existing RNIV and to escalate to Risk Methodologies & Analytics to provide secondary challenge as a result of a potential void in the risk measurement framework that can lead to a new RNIV

**New Product and Significant Transaction Approval Process**

### 8.1.3
Market Risk are responsible for escalation of potential RNIVs to Risk Methodologies & Analytics in advance of NPSTAC sign off to ensure the accurate identification of market risks associated with a new product / market and to assess whether these risks are adequately captured under the existing VaR or RNIV methodologies.

### 8.1.4
Risk Reporting, Analysis & Validation and Market Risk are responsible for the assessments of any EWI triggers (RAG status versus thresholds)

### 8.1.5
Risk Reporting, Analysis & Validation are responsible for monitoring, updating and control of RNIV in Vespa where they have been handed over by Risk Methodologies and Analytics (i.e. in BAU mode)

### 8.1.6
Market Risk are responsible for update of RNIVs and commentaries for Market Risk Model Risk Management forum (on sharepoint)

### 8.1.7
Risk Methodologies & Analytics are responsible for the review/improvement of existing RNIV methodology and the development of new RNIV methodologies and all associated methodology documentation through time (this includes materiality assessments of new RNIVs raised)

### 8.1.8
Risk Methodologies & Analytics are responsible for performing quarterly/annual RNIV recalibrations

### 8.1.9
Risk Methodologies & Analytics will have ownership and version control of all RNIVs computed outside of Vespa (EUC). Risk Reporting, Analysis & Validation is responsible for the running of the EUC's on the agreed upon frequency and to update the results in Vespa.

### 8.1.10
Model Validation are responsible for the ongoing validation and review of existing and new RNIV methodologies that use a model

---

<!-- Page 6 -->

# Market Risk Methodology and Controls

## 8.1 Risk Notification and Analysis
### 8.1.1.1
Risk Methodologies and Analytics is responsible for pre-notifying the PRA of all extensions and changes to the RNIV framework in line with the requirements of Supervisory Statement 13/13. Market Risk is responsible for inclusion of pre- and post-notifications in the quarterly report provided to the PRA.

## 8.2 RNIV Identification Process
The identification of the RNIV's is performed in several ways:

### 8.2.1 Backtesting
Market Risk is responsible for analysing backtesting exceptions (please refer to section 7) to identify whether the exceptions may be the result of P&L arising from risk factors not captured in the VaR model, or by other approximations inherent in the VaR modelling.

### 8.2.2 Model review
A primary goal of the annual model review or specific targeted model review is to ensure existing models capture all market risks and price the product correctly. The annual model review will consist of a combination of targeted and light touch reviews and can include comparing internal valuations with "the street" in order to ensure pricing functions are reasonable and capture "de facto" all the relevant risk parameters used by the pricing function and the risk analytics computation. Ad hoc model reviews are usually triggered by issues or suspicion of issues, and ensure the ongoing accuracy of the models. Model validation performs model reviews.

### 8.2.3 Daily VaR and SVaR analysis
The daily VaR and SVaR analysis performed by Market Risk, and review of large movements is one of the tools that can highlight missing risk factors.

### 8.2.4 Early Warning Indicators (EWI's)
Market Risk & RMA in conjunction with Model Validation has developed a range of EWI's, which are monitored on a periodic basis (e.g. through the Quarterly Proxy & RNIV forum). These indicators target specific model risks (weaknesses) identified as part of the Model Review. If EWI's are triggered, mitigating measures, which include the potential introduction of additional RNIV's may be implemented. Market Risk / Risk Methodologies & Analytics monitor and report EWIs (predominantly through the Proxy & RNIV forum).

### 8.2.5 Interaction with Front Office / Product Control
Front Office, Product Control and Risk have regular formal meetings where information is exchanged on risk and P&L. This forum may identify risks not captured in the VaR, as P&L and risk metrics are analysed across the three areas.

## 8.3
For each risk factor within scope of the RNIV framework a VaR and SVaR metric should be calculated where sufficient data is available and where appropriate. Unless agreed otherwise in the RNIV sign off process, the stressed period for the RNIV SVaR should be consistent with that used for the SVaR. No offsetting or diversification may be recognised across risk factors included in the RNIV framework. The multipliers used for VaR and SVaR should be applied to generate the capital requirement.

## 8.4
If it is not appropriate to calculate a VaR and SVaR metric for a risk factor, then the methodology must be based upon stress test / stressed add-on. The confidence level and capital horizon of the stress test should be commensurate with the liquidity of the risk factor, and should be at least as conservative as comparable risk factors under the internal model approach. The capital charge should be at least equal to the losses arising from the stress test if that is used.

## 9 Limit controls

### 9.1
VaR limits may be applied to any of the following portfolio levels and are administered at Level 1 and Level 2 (refer to market risk Policy on Level definition). Level 3 VaR limits are set and managed by the business. All Level Limits are monitored by Market Risk daily
- Legal Entity
- Business Unit
- Trading Area
- Trading Desk
- Trader
- Book

### 9.2
VaR limits have a "pyramid" structure, i.e. the limit at any level of aggregation within the business is less than the sum of individual limits applying to sub-portfolios within that level of aggregation. It therefore follows that excesses over limits at higher levels (e.g. Business Unit) can occur without there being any excesses at lower levels (e.g. Trading Area).

### 9.3
Market Risk is responsible for ensuring that all level 2 limits are consistent across the Bank. To this effect, VaR limits are reviewed at least annually at a global level and the VaR limit structure and the rationale behind the VaR limits is separately documented. Market Risk considers the following factors in the setting of the VaR limit structure:

---

<!-- Page 7 -->

# Market Risk Management Guidelines

## Risk Appetite and Limits

- Adherence to the overall risk appetite which are outlined in the Market Risk Appetite – Level 1 supporting limits document presented to BRMC (typically Q3 cycle);
- Reasonable concentration of risk / diversification;
- Historical metrics:
  - Past average usage of limits;
  - Peak usage of limits and desk discipline;
- Forward looking metrics:
  - Business appetite for Market Risk, expected business plan and forthcoming business mix;
  - Desk strategy, typically client flow and expected budget;
  - Market trends and conditions .

### 9.4
Notwithstanding this, front office must make every reasonable effort to ensure that their Value-at-Risk limits are adhered to at all times.

### 9.5
Any change to the confidence level or holding period for the purposes of setting risk appetite requires the approval of the Risk Management Committee.

## 10 Backtesting

Backtesting is a key market risk control which ensures integrity on the VaR model performance. It acts as one of the mechanisms for the ongoing validation of a firm's VaR model under the IMA License.

For regulatory and internal reporting purposes, backtesting is conducted using both the 1-day 99% and 1% confidence level value-at-risk measures. (Regulatory requirements expect the VaR model is tested not only the losses in excess of the 99% CI, but also the gain excesses associated with 1% tail)

### 10.1
For positions that are within the scope of the Bank's VaR model permission (i.e. those covered by IMA), backtesting must be conducted using both Actual as well as Hypothetical profit and loss figures.
- Hypothetical profit and loss backtesting are used for model validation, internal reporting purposes, for reporting to the PRA and to calculate capital multipliers plus factors.
- Actual profit and loss figures are used for reporting to the PRA and to calculate capital multipliers plus factors.

Backtesting for non-IMA positions may be conducted using only actual profit & loss figures if hypothetical P&L is not available.

### 10.2
Actual Profit & Loss is defined as the actual changes in the portfolio's value based on a comparison between the portfolio's end-of-day value and its actual value at the end of the subsequent day excluding fees, commissions, and net interest income.

### 10.3
Hypothetical Profit & Loss for a particular portfolio and business day is the profit and loss that would have occurred on that day had the underlying portfolio remained unchanged.

### 10.4
Section 10.2 and 10.3 is articulated in the table form below, as prescribed by the PRA in the back testing supervisory reporting that occurs each quarter. For each portfolio or set of portfolios, Market Risk is responsible for documenting the Bank's methodology for calculating hypothetical and actual profit and loss in accordance to regulatory directives.

---

<!-- Page 8 -->

# Back-testing Procedures and Requirements

[Image shows a table at the top indicating back-testing is conducted using both hypothetical (hypo) and actual P&L with various risk factors and metrics]

## Portfolio Levels for Back-testing

10.5 For positions that are within the scope of the bank's model permission, back-testing is conducted daily at the following portfolio levels:
- ICBC Standard Bank Plc;
- Trading Area or Risk Class;
- Trading Desk.

Back-testing should also be done on a daily basis for the overall management scope (i.e. IMA and non-IMA) of the VaR model per the SLA's agreed between Product Control and Market Risk.

- For any business day, a regulatory back-testing exception is deemed to have occurred if the measure of P&L as per that stated in PRA Article 366 (section 10.4) or otherwise agreed with the PRA, shows a loss which in absolute magnitude exceeds the corresponding one-day 99% confidence level VaR measure.
- For any business day, an internal back-testing exception is deemed to have occurred if a particular back-tested profit or loss figure exceeds the corresponding one-day 99% confidence level VaR measure.

10.6 Market Risk is responsible for assessing the number of regulatory back-testing exceptions over the most recent 250 days as and when exceptions occur to determine whether the VaR & SVAR multiplier needs to be updated in line with the regulatory requirements. The Risk Reporting, Analysis and Validation team is responsible for ensuring that the multiplier is updated in the risk reporting as well as ensuring that TCM are informed.

10.7 The required adjustment to the multipliers is summarised in the below table.

| Zone | Number of Recorded Exceptions | Plus Factor |
|------|----------------------------|------------|
| Green | 4 or less | 0.00 |
| Yellow | 5 | 0.40 |
| | 6 | 0.50 |
| | 7 | 0.65 |
| | 8 | 0.75 |
| | 9 | 0.85 |
| Red | 10 or more | 1.00 |

10.8 The Bank is entitled to seek a variation of its value-at-risk model permission in order to exclude a particular back-testing exception. The Bank's regulator will then decide whether to agree to such a variation. An example of this is when a back-testing exception might properly be disregarded is when it has arisen as a result of a risk that is not captured in the VaR model, but against which regulatory capital resources are already held (e.g. through an RNIV).

10.9 Specific risk back-testing involves the back-testing of a standalone specific value-at-risk measure against a profit and loss determined by reference to specific risk factors. Alternatively, specific risk back-testing may take the form of regular back-testing of portfolios or sets of portfolios that are predominantly exposed to specific risk factors. Market Risk is responsible for specifying and documenting the Bank's approach to specific risk back-testing.

---

<!-- Page 9 -->

# Market Risk Back-Testing Policy

## 10. Product Control and Market Risk Responsibilities

### 10.10
Product Control is responsible for the accuracy of the various measures of profit and loss against which backtesting of the value-at-risk is conducted. As a result, Product Control is required to sign off the P&L on a daily basis as confirmation the accuracy. Market Risk is required to give daily sign off for the overall integrity of the backtesting. Backtesting should be conducted on a "T-1" basis, and no later than "T+2". If, for operational reasons, the value-at-risk or relevant profit and loss reporting fails, Market Risk and Product Control will use estimates produced on whatever basis is deemed appropriate and report revised figures as soon as actual value-at-risk and profit and loss figures are available.

### 10.11
If a negative back-testing exception occurs, Market Risk is responsible for investigating the source of the exception. Product Control is responsible for providing Market Risk with commentary explaining the profit or losses. The explanation will generally include a brief market commentary and a detailed analysis of the profits or losses contributing to the exception, including a breakdown by significant sub-portfolio or book and / or significant risk factor. Market Risk must provide detailed commentary on all 99% negative backtesting exceptions explaining why the P&L exceeded the VaR.

### 10.12
Market Risk is responsible for ensuring that backtesting results covering all positions that are within the scope of the Bank's value-at-risk model permission are reported to its regulator on a quarterly basis. Specifically, a summary of backtesting performance against the measure(s) of P&L as per that stated in CRR Article 366 or otherwise agreed with the PRA must be provided in electronic format as stipulated in the Bank's value-at-risk model permission. If a regulatory backtesting exception occurs (as defined by the PRA model approval permission), Market Risk is responsible for notifying the Bank's regulator by close-of-business 2 business days after the business day for which the backtesting exception occurred. This explanation must include the causes of the backtesting exceptions, an analysis of whether the backtesting exceptions indicate a deficiency in the Bank's value-at-risk model and details of any proposed remedial action. Market Risk is also responsible for ensuring that any other "ad hoc" regulatory reporting requirements are met.

### 10.13
Market Risk will report all/P exceptions to the Market & Liquidity Risk Committee and the Risk Management Committee on a monthly basis (both positive and negative level 1 and level 2 exceptions).

### 10.14
Market Risk will notify RMA and Model Validation of all negative level 1 and level 2 exceptions on the day of the sign off including commentary on the significant P&L drivers.

### 10.15
RMA perform an independent review of the exception within 5 working days covering at least the below:
- Whether the exception is driven by market moves exceeding 99% confidence levels from the prior 12 months (i.e. a genuine historical simulation model exception)
  - If the exception is genuine, detail the observed market moves versus the prior year's history defending this
  - If the exception is not clearly driven by genuine 99% market moves, the potential model deficiency should be detailed (e.g. issues on risk capture, issues on data collection etc)
  - Any other mitigants to this breach from a capitalisation perspective (e.g. RNIV)
- A final review concluding on at least the below should be presented from RMA to MV for review
  - Is there a potential flaw in the VaR Model?
  - Is the bank at risk of being undercapitalized for the market risks that drove these exceptions?
  - The current number of total exceptions in the prior 12 months and any trend behaviour
  - recommended actions and timelines

### 10.16
Should there be 5 or more exceptions in a 12-month period (in line with regulatory multipliers) a formal review should be brought to RTF/RMAC indicating RMA comfort. This should be tracked via the EWI dashboard

### 10.17
Owing to the fact that backtesting has only limited power to validate the VaR model, the Bank should complement backtesting with additional model validation processes. This is governed by the "Model Validation Policy for Valuation and Market Risk Models".

## 11. Exceptions

### 11.1
There are no exceptions to this Policy.

## 12. Related Policies and Standards

### 12.1
Please refer to the following related documents for further information:
- Market Risk Policy

---

<!-- Page 10 -->

# Policy Document

## Related Policies
- Valuation, Provisions & Revenue Recognition Policy
- Stress Testing Policy
- Model Validation Policy for Valuation and Market Risk Models

### 12.2
All Bank policies can be located via the Bank's Intranet Document Portal.

## 13. Definitions
The following defined terms apply to this policy:

| Term | Definition |
|------|------------|
| Bank | Refers to ICBC Standard Bank Plc and its subsidiary entities and branches within the ICBC Standard Bank Plc Group. |

## 14. Policy Contact

| Field | Details |
|-------|----------|
| Name: | Brendan Melvin |
| Telephone: | +44 (0) 20 31455863 |
| Email: | Brendan.melvin@icbcstandard.com |

## 15. Revision History

| Version No. | Purpose of revision | Review Date | Effective Date | Summary of key revision points |
|-------------|-------------------|--------------|----------------|----------------------------|
| 1.0 | Policy amended for new ICBC Standard Bank entity | Oct 2014 | Nov 2014 | Change from Standard Bank PLC to ICBC Standard Bank PLC |
| 1.1 | Annual review | Apr 2014 | May 2015 | Minor changes |
| 1.2 | Annual review | Oct 2015 | Nov 2015 | Incorporation of Audit recommendations |
| 1.3 | Annual review | Oct 2016 | Nov 2016 | Added Model Validation requirements |
| 2.0 | Updated for Risk Analytics role | Feb 17 | Mar 17 | Added Risk Analytics' role as well as requirements on assumptions, justifications, proxy and RNIV framework. |
| 3.0 | Annual review | Sep 2018 | Sep 2018 | • Backtesting Policy and RNIV Policy incorporated into VAR Policy<br>• RNIV responsibilities further defined<br>• General clean-up of overall policy |

---

<!-- Page 11 -->

# Document Version History

| Version | Description | Start Date | End Date | Changes/Notes |
|---------|-------------|------------|----------|---------------|
| 4.0 | Review addressing an audit point regarding roles and responsibilities between RMA and MR | June 2019 | June 2020 | Updates to section 4 and 5 to articulate Roles and Responsibilities between RMA and MR |
| 4.0a | Annual review - no material changes proposed | June 2020 | June 2021 | No significant changes |
| 4.1 | Mid-cycle update | Jan 2021 | June 2021 | Update to insert 2.14 and additional line in 7.7 (on non-IMA backtesting) for internal audit |
| 4.2 | Update to include | Feb 2021 | Feb 2021 | Historical Time Series Proving Process for Fixed Income (Credit/Rates/FX) and Energy |
| 4.3 | Mid-cycle update | Feb 2022 | Feb 2022 | Mid-cycle update to account for RMA guidelines for escalation of backtesting exceptions |
| 4.4 | Annual review | June 2022 | June 2022 | No significant changes |
| 4.5 | Annual review | June 2022 | June 2022 | No significant changes |
| 4.6 | Annual Review | July 2023 | July 2023 | No significant changes |
| 4.7 | Annual Review | Aug 2024 | Aug 2024 | Whole sale changes to define VaR, SVaR and ESVAR<br>Revision on Proxy process<br>Revision on RNIV<br>Revision on Back testing<br>RMA, RAV, Change, TOM, MR |

# Interpreting the results

## Reproduced data facts

The four datasets have 14 cities, 28 products, 497 customers and 10,388 recorded sales. Their revenue totals ₹6,070,190. Q4 2023 contributes ₹1,963,300. Dates span 2023-01-01 through 2024-10-01; October 2024 is a partial month, so its decline must not be interpreted as a complete-month demand decline.

The revenue shortlist is Pune, Chennai and Bangalore. The upstream recommendation is Pune, Delhi and Jaipur, referring to rent, consumer estimates and revenue/customer. Those factors are plausible criteria, but no weights, thresholds or selection method were supplied. This replica reports a reproducible revenue ranking rather than presenting an undefined scoring method as objective.

## Assumptions and limits

- The 25% consumer rate is an assumption provided by the original business question. It is not measured consumer demand.
- Values are interpreted as INR from the India-based business context; the CSVs do not include a currency column.
- Estimated rent has no documented period or unit. Rent/customer means the supplied rent amount divided by purchasing customers, without claiming it is monthly. Revenue/customer uses all sales in the observed period. They cannot be directly compared as matched-period profit metrics.
- Product sales counts assume a sale row corresponds to one recorded product sale. There is no quantity field. Do not label these verified unit counts.
- No quantity, discount, tax, refund, delivery cost, acquisition cost, staffing cost or store capital expenditure is available. Product price should not replace recorded sales total.
- Observed sales come from existing online activity. They may reflect customer acquisition or supply differences, not only underlying city demand.
- A customer is assigned one city in this dataset. Historical moves and changing city populations are not tracked.
- A missing month is treated as zero **recorded** sales. Missing records cannot be distinguished from true zero demand without collection metadata.

## A defensible store-opening study

Use this project as a screening analysis. Before recommending actual openings, obtain comparable completed-period demand, rent units, operating margins, footfall, competition, delivery catchments and startup costs. Then define a transparent scoring model or financial forecast with sensitivity analysis. Do not choose weights merely to reproduce a preferred city list.

## Interview framing

“I rebuilt a four-table expansion analysis with normalized tables, validated CSV ingestion, reusable SQL metrics and ten reports. I used CTEs and window functions for per-city ranking and calendar-based monthly growth. I reconciled SQL totals to source data and tested inactive cities and zero denominators. I also found that the source README's recommendation did not match its revenue-ranking query, so I made the ranking rule and business assumptions explicit.”

Adapt this wording to what you have personally run, understood and modified. Running this project is not production deployment or proof of business impact.

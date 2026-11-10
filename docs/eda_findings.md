# EDA Findings (Phase 3)

Main population: 96,203 delivered orders purchased 2017-01 to 2018-08.
Late = delivered on a later calendar date than the estimate. Late rate in this
population: 6.79% (6,531 orders). Other populations are stated per finding.

## 1. Scope
- 2016 months and 2018-09/10 hold 0-324 orders a month (Nov 2016 has none), so they are
  excluded from trend charts and kept in totals.
- Monthly orders grew from 800 (2017-01) to about 6,000-7,500 (2018).

## 2. Lateness is clustered in time
- Most months are 1-7% late. 2017-11 (12.4%), 2018-02 (14.1%) and 2018-03 (19.0%) stand out
  (all orders in the delivery population, by purchase month).
- Feb+Mar 2018 hold 2,254 of 6,534 late orders (about 34.5%) in the full delivery population.
- These months are bad in every destination group (Other 13.0/6.5/14.3/23.7% in
  Nov, Dec, Feb, Mar), so there is a system-wide component.
- RJ is hit harder: 26.0/24.0/34.0/34.5% in the same months, and still 24.0% in Dec 2017
  when Other was 6.5%.

## 3. Geography
- SP is 42% of orders (4.50% late, 27.8% of all late orders). RJ is 12.8% of orders but
  22.9% of late orders (12.14% late).
- Highest rates: AL 21.46%, MA 17.53%, SE 15.36%, PI 13.89%, CE 13.83% (small volumes).
- Same-state orders (34,489): median 6.53 days, 4.53% late. Cross-state (61,207): median
  12.81 days, 8.11% late (single-seller-state orders, 95,696).
- Holding SP as origin, delivery time rises with distance, but late rate does not follow
  (MG 10.79 days, 5.30% late; RJ 12.84 days, 14.20% late).

## 4. Sellers
- Single-seller orders (94,931): 2,925 sellers; the 614 with 30+ orders cover 83.2% of orders.
- Top 10 sellers by late count: 1,019 of 6,518 late orders (about 15.6%). Lateness is
  not concentrated in a few sellers.
- Among the 10 highest-rate sellers, 54965b and ede0c0 had 0% late outside the four spike
  months and 712e6e 6.5%: timing artifacts. Five (2a1348, ef990a, beadbe, 835f0f, ad7815)
  stayed at 19-30% outside spike months: candidates for review (small samples,
  destination mix not tested).

## 5. Customer experience (association, not proof of cause)
- On time: mean review 4.29, 6.60% one-star. Late: 2.27, 53.76% (95,560 orders with a review).
- Mean score by delay: early 4.29, on date 4.03, 1-3 d 3.29, 4-7 d 2.10, 8-14 d 1.67,
  15+ d 1.72. It falls through the first week and flattens after about 8 days.

## 6. Where the time goes
- Median days: approval to carrier 1.84, carrier to customer 7.10, total 10.21.
- Late orders: carrier to customer 26.20 days vs 6.95 on time; approval to carrier
  3.07 vs 1.79. Most lateness sits in carrier transit.

## 7. Categories, freight, weight
- Top 12 of 74 categories = 69.0% of item revenue (price only).
- Freight as % of price: furniture_decor 23.7, housewares 23.2, garden_tools 20.6,
  watches_gifts 8.4.
- Late rate by category ranges about 4.3% to 12.1% (32 categories with 300+ orders): a modest spread.
- Weight bands: median delivery 9.43 to 11.19 days; late rate 6.1% to 7.56%, not monotonic.

## 8. What this phase did NOT show
- Causes. Carrier capacity, seasonality, promotions and the like are untested hypotheses.
- Whether estimated delivery dates vary by state or category (a possible reason long routes
  are not more often late).
- Seller and category rates are not adjusted for destination or month mix.
- Review links are associations, and review data is leakage for Phase 6.

## 9. Ideas for later phases (hypotheses, not results)
- SQL (Phase 4): reproduce the state, month, seller and category tables.
- Power BI (Phase 5): show the late rate next to order counts, and the seller late rate
  outside the spike months next to the raw rate.
- ML (Phase 6): candidate features known at purchase time include same_state, customer
  state, seller state, order weight, category and purchase month. Check the prediction
  time and the estimated-date and shipping-limit timing first.
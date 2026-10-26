# Real Exchange Rate Explorer

A Streamlit app using monthly IMF consumer-price indices and period-average exchange rates. Compatible with **Python 3.12**. You can deploy it using only GitHub and Streamlit Community Cloud; you do not need to install Python on your computer.

## Files and deployment

Put these three files at the **top level** of your public `real-exchange-rate-app` GitHub repository:

```text
app.py
requirements.txt
README.md
```

1. Upload `app.py` and `requirements.txt` to GitHub and replace the existing README with this file. Commit the changes. Do not paste Markdown code fences into the Python file.
2. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
3. Create an app, choose your repository and branch (normally `main`), and enter `app.py` as the main file.
4. In Advanced settings, select **Python 3.12**. Leave Secrets empty: this app does not require an IMF API key.
5. Deploy and save your public `streamlit.app` link. The initial dependency installation and IMF downloads can take a little time.

See [Streamlit's deployment instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app).

## How to use the app

- Select Country 1 and Country 2. The default is United Kingdom → United States.
- Select inclusive start and end months. The app requests monthly observations from January 1976, wherever available.
- Select **Real**, **Nominal**, or **Both**. Both uses separate vertical axes.
- Download the CSV for the selected period. It contains every calendar month in the period, including months with missing data.
- Open **Verify one observation** to see the calculation for the first valid month.
- Use **Refresh IMF data** to clear the download cache and retry.

Changing the date selectors recalculates the sample average and real index. Zooming or moving the chart's range slider only changes the visible view, not the calculation sample.

## Economics

Let `E1(t)` and `E2(t)` be IMF exchange rates in local-currency units per U.S. dollar. Then:

```text
S(t) = E2(t) / E1(t)
RER(t) = S(t) × P1(t) / P2(t)
RER* = arithmetic mean of RER(t) over valid months in the selected sample
Real_Index(t) = 100 × RER(t) / RER*
```

`S` is **Country 2 currency per one unit of Country 1 currency**. For UK → U.S., `S = 1 / (GBP per USD)`, so the units are **USD per GBP**. Nominal rates are plotted in actual units, without normalization.

A valid real-rate month must have positive, finite values for both price indices and both FX inputs. All valid months receive equal weight. The exported real index therefore averages 100 over its nonmissing observations, subject to floating-point precision. Nominal S can still be calculated in months with both FX rates but a missing CPI.

A rise in this RER represents **real appreciation of Country 1 relative to Country 2**. An index above 100 means above the selected sample's average. The average is not an estimated equilibrium, and the app does not measure overvaluation or undervaluation against purchasing power parity.

The two CPIs may have different reference years. A constant rebasing of either CPI cancels from the normalized real index. This does not eliminate problems from historical currency reforms, series breaks, or changing coverage. The cross-rate uses the ratio of two monthly average USD rates; it is not necessarily the average of daily bilateral cross-rates.

## IMF data and the Euro area

API base: <https://api.imf.org/external/sdmx/3.0>

The app uses the latest available versions of the `IMF.STA` dataflows:

| Input | Dataflow | Monthly key |
|---|---|---|
| All-items national CPI | `CPI` | `{ISO3}.CPI._T.IX.M` |
| Currency units per USD, period average | `ER` | `{ISO3}.XDC_USD.PA_RT.M` |
| Euro area consumer prices, if national CPI is empty | `CPI` | `G163.HICP._T.IX.M` |

Example request:

```text
https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/CPI/~/GBR.CPI._T.IX.M?c%5BTIME_PERIOD%5D=ge%3A1976-M01
```

The request uses `Accept: text/csv`. Monthly labels such as `2024-M01` are converted to calendar months. IMF `SCALE` factors are applied as `OBS_VALUE × 10**SCALE`; original values and scales are retained in the export.

**Euro area exception:** On October 26, 2026, `G163.CPI._T.IX.M` returned no observations. The IMF supplies the Euro area's harmonised consumer price index under `G163.HICP._T.IX.M` in the same CPI dataset. The app tries the specified CPI key first and uses HICP only for the Euro area when that CPI series is empty. It displays this choice and records the actual series key in the CSV. HICP is a consumer-price index, not an inflation-rate series. If your instructor requires the literal national CPI key for every selection, discuss this documented exception with them.

In the live data retrieved for testing, Euro area FX began in January 1999 and its HICP began in December 1999. The app does not invent pre-euro exchange rates or fill earlier gaps. Country selection comes from the IMF country codelist, including countries/economies and the Euro area. A dated copy of those names is embedded in `app.py` for metadata outages; this fallback contains **no fabricated observations**. A listed country is not guaranteed to have both required monthly series.

Sources: [IMF CPI](https://data.imf.org/Datasets/CPI), [IMF exchange rates](https://data.imf.org/Datasets/ER), [IMF API information](https://data.imf.org/en/Resource-Pages/IMF-API), and [SDMX REST data-query specification](https://github.com/sdmx-twg/sdmx-rest/blob/master/doc/data.md).

## CSV fields

| Field | Meaning |
|---|---|
| `month` | Calendar month, `YYYY-MM` |
| `country1_code`, `country2_code` | IMF country identifiers |
| `P1`, `P2` | Consumer-price indices after applying IMF scale factors |
| `FX1_LCU_per_USD`, `FX2_LCU_per_USD` | Currency units per USD after scale factors |
| `S_C2_per_C1` | Nominal cross-rate, Country 2 currency per Country 1 currency |
| `RER` | `S_C2_per_C1 × P1 / P2` |
| `RER_star` | Average valid RER for the selected sample, repeated on each row |
| `Real_Index` | `100 × RER / RER_star` |
| `valid_RER` | Whether that month contributes to the sample average |
| `sample_start`, `sample_end`, `S_units` | Sample bounds and nominal units |
| Prefixed IMF fields | Original observations, scales, statuses, reference periods, and other supplied attributes |
| Prefixed `series_key`, `source_url`, `retrieved_utc` | Provenance for each downloaded input |
| Prefixed `download_error` | Error information if an input download failed |

Blank calculations remain blank. No interpolation, forward filling, or backfilling is applied. The CSV is not restricted to the series currently visible in the chart. If inputs failed to download, the app displays an error and exports available observations with the failure recorded; that partial export should not be mistaken for a completed homework check.

## Verification and homework checks

Checks were run with Python 3.12.14 using live IMF downloads retrieved on October 26, 2026. The app's own download code was also exercised against the IMF API. Streamlit application tests covered all three chart modes, changed sample dates, the Euro area, same-country selection, and invalid date order. Calculation checks covered missing/invalid inputs, preservation of nominal levels, separate chart axes, and a CSV round trip whose real-index mean is 100. These checks do not replace testing your deployed URL.

**Worked example using actual IMF data:** UK as Country 1, U.S. as Country 2; sample January–December 2024; observation January 2024.

```text
P1 = 130.0
P2 = 141.439679347689
E1 = 0.7875078750787511 GBP per USD
E2 = 1.0 USD per USD

S = 1.0 / 0.7875078750787511
  = 1.2698285714285709 USD per GBP

RER = 1.2698285714285709 × 130.0 / 141.439679347689
    = 1.167124494675344

RER* for the January–December 2024 sample = 1.1804795033355544
Real_Index for January 2024 = 100 × 1.167124494675344 / 1.1804795033355544
                           = 98.86867932713152
```

The 12 monthly real-index values for that sample average 100. IMF revisions may change these values; always verify against your own downloaded CSV. For your submission:

1. Run the UK/U.S. example and confirm the chart says USD per GBP.
2. Select another sample, download again, and confirm the mean of nonblank `Real_Index` values is approximately 100. In a spreadsheet, use `AVERAGE` on that column.
3. Independently calculate one month's `S`, `RER`, and real index from the CSV inputs.
4. Try Real, Nominal, and Both, and confirm Both has two axes.
5. Submit your deployed URL, GitHub repository URL, prompts/chat screenshots, model name and date, your manual verification, and your exported CSV as required by your instructor.

## Prompt and model record

- Date of this generation session: **October 26, 2026** (America/Chicago).
- Assistant/model: **OpenAI Codex, GPT-6**. Record the exact variant shown in your model selector as well, if it is more specific.
- Actual user request: “I have a homework here, can you help me with the second section \"ask an LLM to write the app\"”, followed by the full assignment.
- The supplied requirements specified IMF countries and the Euro area, monthly data from January 1976, `S` in Country 2 currency per Country 1 currency, `RER = S × P1 / P2`, sample-average normalization, Real/Nominal/Both charts, CSV exports, and the three Python 3.12-compatible files.
- Preserve the original chat or screenshots as the complete prompt record. This summary is not a verbatim transcript of the pasted assignment.

The prompt below is a **suggested reusable prompt written after the original request**, not a claim that you originally wrote or submitted these exact words. Adapt it in your own words if your instructor wants a separately authored prompt:

> Write a Streamlit app compatible with Python 3.12 and return complete app.py, requirements.txt, and README.md files. Use monthly IMF all-items CPI and period-average exchange rates from January 1976 where available. Allow users to choose two IMF countries or the Euro area (G163). IMF rates are local currency per USD: calculate S = FX2 / FX1 so S is Country 2 currency per Country 1 currency. Calculate RER = S × CPI1 / CPI2, then divide by the mean RER over valid months in the user-selected inclusive sample and multiply by 100. Recalculate that mean when sample dates change. Plot Real, Nominal, or Both interactively, using separate axes for Both and leaving nominal S in actual units. Export every sample month, the original inputs, calculated values, missing-data flags, and source information to CSV. Handle API errors and missing observations without inventing or filling data. Verify the current API format and explain any required Euro area HICP exception. Test UK/U.S. exchange-rate direction, changed sample dates, and that the exported real index averages 100. Explain deployment through GitHub and Streamlit Community Cloud without requiring a local Python installation.

## Troubleshooting

If the IMF is slow or unreachable, try **Refresh IMF data** later. The app uses request timeouts and limited retries. It shows request errors instead of silently substituting another provider or artificial data. If no valid real-rate observations exist, try a more recent sample or another country pair; nominal rates may still be available.

For a deployment or runtime error, copy the exact Streamlit log/error and provide all three current files to your LLM. Ask for complete corrected files, then replace and commit them on GitHub. The pinned dependencies in `requirements.txt` are the versions used for testing this delivery.

Optional local development, if Python is already installed:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```
